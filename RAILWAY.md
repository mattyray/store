# Railway Production Notes

## Quick Reference - Common Commands

```bash
# SSH into production container
railway ssh

# Once inside the container:
python manage.py shell -c "from apps.core.models import Subscriber; print(list(Subscriber.objects.values('email', 'mailerlite_id', 'subscribed_at')))"
python manage.py shell -c "from apps.orders.models import Order; print(list(Order.objects.values('id', 'email', 'total', 'status', 'created_at').order_by('-created_at')[:10]))"
python manage.py shell -c "from apps.core.models import GiftCard; print(list(GiftCard.objects.values('code', 'balance', 'is_active')))"
python manage.py shell -c "from apps.catalog.models import Photo; print(f'Embeddings: {Photo.objects.filter(embedding__isnull=False).count()}/{Photo.objects.count()}')"

# Regenerate AI data
python manage.py generate_photo_embeddings
python manage.py generate_photo_descriptions

# View logs (run locally, not in SSH)
railway logs
railway logs --follow


# Check env vars (run locally)
railway variables
railway variables | grep MAILERLITE
```

**Important:** `railway ssh` connects to the server. `railway run` runs locally with Railway's env vars.



---

## Key Production Files

| File | Purpose |
|------|---------|
| `backend/start.sh` | Main startup script - runs migrations, embeddings, starts gunicorn |
| `backend/Procfile` | Defines web + worker processes (web uses start.sh via Dockerfile) |
| `backend/Dockerfile` | Container build - installs deps, copies code, runs start.sh |
| `backend/config/settings/production.py` | Production Django settings |
| `backend/config/settings/base.py` | Shared Django settings |
| `frontend/netlify.toml` | Netlify build config for Next.js |

## Deployment Architecture

```


┌─────────────────┐     ┌─────────────────────────────────────────┐
│    Netlify      │     │              Railway                    │
│   (Frontend)    │────▶│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│   Next.js 15    │     │  │   Web   │  │ Worker  │  │  Redis  │ │
└─────────────────┘     │  │ Django  │  │ Celery  │  │         │ │
                        │  └────┬────┘  └────┬────┘  └────┬────┘ │
                        │       │            │            │      │
                        │       └────────────┴────────────┘      │
                        │                    │                    │
                        │           ┌────────▼────────┐          │
                        │           │    PostgreSQL   │          │
                        │           │   + pgvector    │          │
                        │           └─────────────────┘          │
                        └─────────────────────────────────────────┘
```

## Railway Services

You should have these services in your Railway project:

### 1. Web Service (Django)
- **Source**: `backend/` directory
- **Dockerfile**: Uses `backend/Dockerfile`
- **Start command**: Runs `start.sh` which does migrations, embeddings, then gunicorn
- **Port**: Uses `$PORT` env var (Railway sets this)
- **Purpose**: Handles all HTTP requests - API, chat SSE streaming, webhooks

### 2. Worker Service (Celery)
- **Source**: Same `backend/` directory
- **Start command**: `celery -A config worker -l info --concurrency=2`
- **Purpose**: Background task processing (currently not heavily used, but available for async jobs)
- **Depends on**: Redis

### 3. PostgreSQL (Database)
- **Type**: Railway addon
- **Extension**: pgvector enabled for vector similarity search
- **Auto-configured**: Railway sets `DATABASE_URL` automatically
- **Contains**: All Django models - photos, orders, cart, chat conversations, etc.

#### pgvector for Semantic Search

pgvector is a PostgreSQL extension that adds vector/embedding support directly to Postgres. No separate vector database needed.

**How it works:**
1. Photo model has a `VectorField(dimensions=1536)` for storing OpenAI embeddings
2. When user searches "calming ocean photos", query gets embedded via OpenAI
3. pgvector finds photos with similar embeddings using cosine distance

```python
# In tools.py - semantic search
from pgvector.django import CosineDistance

photos = Photo.objects.filter(
    embedding__isnull=False
).order_by(
    CosineDistance('embedding', query_embedding)  # Lower = more similar
)[:5]
```

**Why pgvector vs Pinecone/Weaviate?**
- No extra service to manage
- Railway Postgres supports it out of the box
- For ~30 photos, a dedicated vector DB is overkill
- Scales fine to millions of vectors if needed

### 4. Redis
- **Type**: Railway addon
- **Purpose**: Celery message broker and result backend
- **Auto-configured**: Railway sets `REDIS_URL` automatically
- **Used by**: Celery worker for task queue

## Service Dependencies

```
Web ──────┬──▶ PostgreSQL (DATABASE_URL)
          └──▶ Redis (REDIS_URL) - for checking Celery status

Worker ───┬──▶ PostgreSQL (DATABASE_URL)
          └──▶ Redis (REDIS_URL) - task queue
```

## Setting Up Services in Railway

1. **Create project** from GitHub repo
2. **Add PostgreSQL** - Click "New" → "Database" → "PostgreSQL"
3. **Add Redis** - Click "New" → "Database" → "Redis"
4. **Web service** - Auto-created from Dockerfile, uses `backend/` as root
5. **Worker service** (optional) - Click "New" → "Service" → same repo
   - Set root directory to `backend/`
   - Set start command to `celery -A config worker -l info --concurrency=2`

## Environment Variables Per Service

**All services need access to:**
- `DATABASE_URL` (auto-set by PostgreSQL addon)
- `REDIS_URL` (auto-set by Redis addon)

**Web service specifically needs:**
- All the API keys (Stripe, Anthropic, OpenAI, AWS)
- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL`

**Worker service needs:**
- Same as web (shares env vars or copy them over)

Railway's "Shared Variables" feature lets you define variables once and share across services.

## Procfile vs Dockerfile

The `Procfile` defines two processes:
```
web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn ...
worker: celery -A config worker -l info --concurrency=2
```

But the **web** service uses `Dockerfile` which runs `start.sh` instead (more control).

The **worker** service can use the Procfile's worker command directly, or you can set the start command manually in Railway.

- **Frontend**: Netlify (auto-deploys from `frontend/` on push to main)
- **Backend**: Railway (auto-deploys from `backend/` on push to main)
- **Database**: Railway PostgreSQL addon with pgvector extension
- **Media**: AWS S3
- **Payments**: Stripe

## Accessing the Container Shell

Railway uses `railway ssh` (not `railway shell`) to access the running container:

```bash
railway login
railway link        # link to your project if not already
railway ssh         # SSH into the container
```

Or get the full command from the Railway dashboard: **right-click on your service** → **"Copy SSH Command"**

**Important distinction:**
- `railway ssh` - connects to the actual running container on Railway
- `railway shell` / `railway run` - runs commands LOCALLY with Railway env vars (doesn't connect to the container)

## Running Django Management Commands

Since `railway ssh` works, you can run commands directly:

```bash
railway ssh
# then inside the container:
python manage.py generate_photo_embeddings
python manage.py generate_photo_descriptions
```

Or use start.sh for one-time commands by adding them before gunicorn starts.

## Start Script (start.sh)

The backend uses `start.sh` instead of `Procfile` for the web process. Current startup sequence:

1. Run migrations
2. Run Django checks
3. Generate embeddings for any new photos (skips existing)
4. Log embedding count
5. Start gunicorn

To run a one-time command in production, add it to start.sh before the gunicorn line, push, then remove it after it runs.

## Environment Variables

Required in Railway dashboard:

```
# Django
SECRET_KEY
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# Database (Railway provides DATABASE_URL automatically)
DATABASE_URL

# AWS S3
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME
AWS_S3_REGION_NAME

# Stripe
STRIPE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET

# AI APIs
ANTHROPIC_API_KEY      # For Claude (chat agent, photo descriptions)
OPENAI_API_KEY         # For embeddings (text-embedding-ada-002)

# Email
EMAIL_HOST_PASSWORD    # Resend API key
DEFAULT_FROM_EMAIL
ADMIN_EMAIL

# CORS
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
FRONTEND_URL

# Redis (if using Celery)
REDIS_URL
```

## Checking Embeddings

The startup script logs embedding count:
```
Photos with embeddings: 31/31
```

If this shows 0/31, embeddings need to be generated. The `generate_photo_embeddings` command runs automatically on startup for any photos missing embeddings.

## pgvector

Railway PostgreSQL supports pgvector. The extension is enabled via migration:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `railway shell` doesn't connect | Use `railway ssh` instead |
| Django AppRegistryNotReady | Need `DJANGO_SETTINGS_MODULE` set before `django.setup()` |
| Embeddings not generating | Check `OPENAI_API_KEY` is set in Railway |
| Container restart loop | Check logs - usually a startup script error |

## AI Agent Stack

- **LangChain** - Agent framework with tool calling
- **Claude API** - Chat responses (via langchain-anthropic)
- **OpenAI** - Embeddings for semantic search (text-embedding-ada-002)
- **pgvector** - Vector similarity search in PostgreSQL
- **MiDaS ONNX** - Depth estimation for room mockups

## Useful Commands

```bash
# Update Railway CLI
npm update -g @railway/cli

# Check current linked project
railway status

# View logs
railway logs

# SSH into container
railway ssh
```

## Backend File Structure

```
backend/
├── start.sh                    # Startup script (migrations, embeddings, gunicorn)
├── Procfile                    # web: uses Dockerfile, worker: celery
├── Dockerfile                  # Python 3.12, installs requirements, runs start.sh
├── manage.py
├── requirements.txt
├── config/
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # Local dev settings
│   │   └── production.py       # Production settings (uses env vars)
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── catalog/                # Photos, Collections, ProductVariants
    │   ├── models.py           # Photo model has embedding field (pgvector)
    │   └── management/commands/
    │       ├── generate_photo_descriptions.py  # Claude Vision
    │       └── generate_photo_embeddings.py    # OpenAI embeddings
    ├── chat/                   # AI Shopping Agent
    │   ├── agent.py            # LangChain agent with streaming
    │   ├── tools.py            # All agent tools (search, cart, mockup, etc.)
    │   ├── prompts.py          # System prompt
    │   ├── models.py           # Conversation, Message
    │   └── views.py            # SSE streaming endpoint
    ├── mockup/                 # Room mockup generation
    │   ├── wall_detector.py    # MiDaS ONNX depth estimation
    │   └── mockup_generator.py # Composite print onto wall
    ├── orders/                 # Cart, Order, OrderItem
    ├── payments/               # Stripe checkout, webhooks
    └── core/                   # Contact, Newsletter, GiftCards
```

## Frontend (Netlify)

The frontend auto-deploys to Netlify from the `frontend/` directory.

**netlify.toml** configures:
- Build command: `npm run build`
- Publish directory: `.next`
- Uses `@netlify/plugin-nextjs` for App Router support

**Environment variables** (set in Netlify dashboard):
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

## Stripe Webhooks

Webhook endpoint: `https://your-backend.railway.app/api/payments/webhook/`

Events to enable in Stripe dashboard:
- `checkout.session.completed`
- `payment_intent.succeeded`
- `payment_intent.payment_failed`

Set `STRIPE_WEBHOOK_SECRET` in Railway from the Stripe dashboard webhook signing secret.

## Adding New Photos

When you add new photos via Django admin:

1. Upload the photo (goes to S3)
2. Run `generate_photo_descriptions` to get AI metadata (auto on next deploy, or via SSH)
3. Run `generate_photo_embeddings` to create vector embeddings (auto on every deploy)

The startup script runs embeddings automatically, so just push a deploy after adding photos.
