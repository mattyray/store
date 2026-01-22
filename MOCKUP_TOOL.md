# Wall Mockup Tool - Technical Reference

This document captures the implementation details, architecture, and troubleshooting knowledge for the "See In Your Room" ML-powered wall visualization feature.

---

## Overview

The mockup tool lets users upload a photo of their wall and see how prints would look at actual scale. It uses ML for automatic wall detection with manual fallback.

**User Flow:**
1. User clicks "See In Your Room" on a photo detail page
2. Uploads wall photo (camera on mobile, file picker on desktop)
3. ML attempts wall detection (or falls back to manual selection)
4. User can drag/reposition prints, adjust ceiling height, add multiple prints
5. Download image or generate shareable link

---

## Architecture

```
Frontend (Next.js)                    Backend (Django)
┌─────────────────────┐              ┌─────────────────────┐
│ MockupTool.tsx      │   upload     │ UploadWallImageView │
│ WallCanvas.tsx      │ ──────────►  │ POST /api/mockup/   │
│ (Fabric.js canvas)  │              │     analyze/        │
└─────────────────────┘              └──────────┬──────────┘
                                                │
                                     queues task via .delay()
                                                │
                                                ▼
┌─────────────────────┐              ┌─────────────────────┐
│ Redis               │ ◄──────────  │ Celery Worker       │
│ (message broker)    │              │ analyze_wall_image  │
└─────────────────────┘              └──────────┬──────────┘
                                                │
                                     runs ML pipeline
                                                │
                                                ▼
                                     ┌─────────────────────┐
                                     │ ML Pipeline         │
                                     │ 1. MiDaS depth est. │
                                     │ 2. RANSAC plane fit │
                                     └─────────────────────┘
```

---

## Railway Services

### 1. Backend (Django Web)
- **Root Directory:** `backend`
- **Start Command:** Default (uses Procfile or gunicorn)
- **Purpose:** Serves API, queues Celery tasks

### 2. Celery Worker
- **Root Directory:** `backend`
- **Start Command:** `celery -A config worker -l info --concurrency=1`
- **Purpose:** Processes ML tasks asynchronously
- **Memory:** Keep concurrency at 1 to prevent OOM

### 3. Redis
- **Service:** Railway Redis addon (or Redis Cloud)
- **Purpose:** Message broker for Celery
- **URL:** Set as `REDIS_URL` env var

---

## Environment Variables

### Backend (Django)
```
REDIS_URL=redis://...        # Redis connection string (from Railway addon)
```

### Celery Settings (in Django settings)
```python
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_TASK_SOFT_TIME_LIMIT = 30
CELERY_TASK_TIME_LIMIT = 45
```

---

## Key Files

### Backend

| File | Purpose |
|------|---------|
| `backend/config/__init__.py` | **CRITICAL:** Must import celery_app for broker connection |
| `backend/config/celery.py` | Celery app configuration |
| `backend/apps/mockup/tasks.py` | Celery task for ML processing |
| `backend/apps/mockup/views.py` | API endpoints |
| `backend/apps/mockup/models.py` | WallAnalysis, SavedMockup models |
| `backend/apps/mockup/ml/depth.py` | MiDaS ONNX inference |
| `backend/apps/mockup/ml/wall.py` | RANSAC wall plane detection |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/components/mockup/MockupTool.tsx` | Main modal/overlay |
| `frontend/src/components/mockup/WallCanvas.tsx` | Fabric.js canvas |
| `frontend/src/components/mockup/WallUploader.tsx` | Image upload |
| `frontend/src/components/mockup/CeilingSlider.tsx` | Height adjustment |

---

## ML Pipeline Details

### MiDaS Depth Estimation
- **Model:** `dpt_swin2_tiny_256.onnx` (~165MB)
- **Input:** 256x256 RGB image
- **Output:** 256x256 depth map (relative depth, 0-1)
- **Runtime:** ONNX Runtime (CPU)
- **Location:** `backend/apps/mockup/ml/models/dpt_swin2_tiny_256.onnx`

### RANSAC Wall Detection
- **Library:** scikit-learn RANSACRegressor
- **Approach:** Fits plane z = ax + by + c to depth values
- **Sample Size:** 3,000 points (reduced from 10k for memory)
- **Output:** Wall bounds {top, bottom, left, right} + confidence

### Memory Optimizations (Critical for Railway)
The ML pipeline was optimized to run in ~512MB-1GB memory:

1. **Image resize:** Max 800px before processing (was 1280)
2. **No coordinate grids:** Compute x,y from flat indices instead of meshgrid
3. **Smaller RANSAC sample:** 3,000 points instead of 10,000
4. **No morphological ops:** Removed scipy ndimage operations
5. **Float32:** Explicit float32 instead of float64
6. **Percentile bounds:** Estimate bounds from sample, not full mask

---

## API Endpoints

### Upload Wall Image
```
POST /api/mockup/analyze/
Content-Type: multipart/form-data

Body: image (file)

Response:
{
  "id": "uuid",
  "status": "pending" | "processing" | "completed" | "manual" | "failed",
  "original_image": "url",
  "wall_bounds": null,
  "confidence": null
}
```

### Poll Analysis Status
```
GET /api/mockup/analyze/{id}/

Response:
{
  "id": "uuid",
  "status": "completed",
  "original_image": "url",
  "wall_bounds": {"top": 100, "bottom": 800, "left": 50, "right": 950},
  "confidence": 0.72,
  "pixels_per_inch": 12.5
}
```

### Update Analysis (Manual Bounds)
```
PATCH /api/mockup/analyze/{id}/
Content-Type: application/json

Body: {
  "wall_bounds": {"top": 100, "bottom": 800, "left": 50, "right": 950},
  "wall_height_feet": 9.0
}
```

### Save Mockup
```
POST /api/mockup/save/
Content-Type: application/json

Body: {
  "analysis_id": "uuid",
  "mockup_image": "data:image/jpeg;base64,...",
  "config": {
    "prints": [...],
    "wall_height_feet": 8.0
  }
}

Response:
{
  "id": "uuid",
  "mockup_image": "url",
  "share_url": "https://store.matthewraynor.com/mockup/{id}"
}
```

---

## Status Flow

```
pending → processing → completed (ML success, confidence >= 0.3)
                    → manual (ML success but low confidence < 0.3)
                    → manual (ML failed/timeout)
                    → failed (unrecoverable error)
```

**Frontend polling:** Poll GET `/api/mockup/analyze/{id}/` every 2 seconds while status is `pending` or `processing`.

---

## Common Issues & Solutions

### Issue: Tasks Not Being Queued
**Symptom:** Status stays "manual" immediately, logs show "OperationalError"
**Cause:** `config/__init__.py` not importing celery_app
**Fix:** Ensure this file contains:
```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

### Issue: S3 Image Path Error
**Symptom:** "No such file" errors in task
**Cause:** `analysis.original_image.path` doesn't work with S3 storage
**Fix:** Download to temp file:
```python
with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
    with analysis.original_image.open('rb') as img_file:
        tmp.write(img_file.read())
    temp_image_path = tmp.name
```

### Issue: OOM Kill (SIGKILL signal 9)
**Symptom:** Worker killed ~10-15 seconds into processing
**Cause:** Memory exhaustion from large arrays
**Fix:**
- Set Celery concurrency to 1
- Reduce image max_size to 800px
- Use memory-optimized wall.py (no meshgrid, smaller samples)

### Issue: Model Not Found
**Symptom:** "MiDaS model not available" in logs
**Cause:** ONNX model not downloaded during Docker build
**Fix:** Dockerfile should include:
```dockerfile
RUN curl -L -o /app/apps/mockup/ml/models/dpt_swin2_tiny_256.onnx \
    https://huggingface.co/isl-org/MiDaS/resolve/main/dpt_swin2_tiny_256.onnx
```

---

## Scale Calculation

The tool calculates real-world scale from wall height:

```python
# Given wall_bounds and wall_height_feet:
wall_height_px = wall_bounds['bottom'] - wall_bounds['top']
wall_height_inches = wall_height_feet * 12
pixels_per_inch = wall_height_px / wall_height_inches

# To render a 24x36 inch print:
print_width_px = 24 * pixels_per_inch
print_height_px = 36 * pixels_per_inch
```

Default ceiling height: 8 feet (adjustable 7-12 feet via slider)

---

## Dockerfile Model Download

The MiDaS model is too large for git (~165MB). It's downloaded during Docker build:

```dockerfile
# In backend/Dockerfile
RUN mkdir -p /app/apps/mockup/ml/models && \
    curl -L -o /app/apps/mockup/ml/models/dpt_swin2_tiny_256.onnx \
    https://huggingface.co/isl-org/MiDaS/resolve/main/dpt_swin2_tiny_256.onnx
```

The code also has a fallback `download_model()` function that downloads at runtime if needed.

---

## Testing Locally

### Start Services
```bash
# Start all services
docker compose up

# Or start Redis separately for Celery testing
docker run -p 6379:6379 redis:7-alpine

# Run Celery worker locally
cd backend
celery -A config worker -l info --concurrency=1
```

### Test Upload
```bash
curl -X POST http://localhost:7974/api/mockup/analyze/ \
  -F "image=@test_wall.jpg"
```

### Check Task Status
```bash
curl http://localhost:7974/api/mockup/analyze/{id}/
```

---

## Logging

Key log messages to look for in Railway:

**Success path:**
```
Queuing wall analysis task for {id}
Task queued successfully for {id}
Starting wall analysis for {id}
Image downloaded to temp file
Resized image from (2820, 3760) to (600, 800) for processing
MiDaS model loaded successfully
Wall detection starting: depth map 256x256
Valid depth points: 52000
Running RANSAC...
RANSAC complete. Sample confidence: 72.00%
Wall detected with confidence: 72.00%, bounds: {...}
Wall analysis completed: status=completed, confidence=0.72
```

**Failure indicators:**
```
Failed to queue Celery task: OperationalError  # Redis connection issue
Worker exited with signal 9 (SIGKILL)          # OOM kill
Depth estimation failed: ...                    # Model/inference error
Wall detection failed: ...                      # RANSAC error
```

---

## Future Improvements

- [ ] GPU inference (if Railway supports)
- [ ] Multiple wall detection (corners, alcoves)
- [ ] Furniture occlusion handling
- [ ] AR/camera preview mode
- [ ] Print shadow direction based on detected lighting
