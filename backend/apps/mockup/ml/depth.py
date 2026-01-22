"""
MiDaS Depth Estimation using ONNX Runtime.

Uses MiDaS v3.1 dpt_swin2_tiny_256 for fast CPU inference.
Model size: ~165MB
Inference time: 1-3 seconds on CPU
"""
import os
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Singleton for model caching
_model_session = None
_model_transform = None

# Model configuration
MODEL_INPUT_SIZE = 256  # dpt_swin2_tiny expects 256x256
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'dpt_swin2_tiny_256.onnx')


def download_model():
    """
    Download the MiDaS ONNX model if not present.
    Returns True if model exists or was downloaded successfully.
    """
    if os.path.exists(MODEL_PATH):
        return True

    # Model URL from HuggingFace
    MODEL_URL = 'https://huggingface.co/isl-org/MiDaS/resolve/main/dpt_swin2_tiny_256.onnx'

    logger.info(f'Downloading MiDaS model from {MODEL_URL}...')

    try:
        import urllib.request

        # Create models directory if needed
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

        # Download with progress
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        logger.info(f'MiDaS model downloaded successfully to {MODEL_PATH}')
        return True

    except Exception as e:
        logger.error(f'Failed to download MiDaS model: {e}')
        return False


def get_model():
    """
    Lazy load the MiDaS ONNX model.
    Returns the ONNX Runtime session.
    """
    global _model_session

    if _model_session is not None:
        return _model_session

    try:
        import onnxruntime as ort

        # Download model if not present
        if not download_model():
            logger.warning('MiDaS model not available. ML features disabled.')
            return None

        # Create ONNX Runtime session with optimizations
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = 4

        _model_session = ort.InferenceSession(
            MODEL_PATH,
            sess_options,
            providers=['CPUExecutionProvider']
        )

        logger.info('MiDaS model loaded successfully')
        return _model_session

    except ImportError:
        logger.warning('ONNX Runtime not installed. ML features disabled.')
        return None
    except Exception as e:
        logger.error(f'Failed to load MiDaS model: {e}')
        return None


def preprocess_image(image_path: str, max_size: int = 800) -> tuple:
    """
    Preprocess image for MiDaS inference.

    Args:
        image_path: Path to the input image
        max_size: Maximum dimension to resize to before processing (saves memory)

    Returns:
        Tuple of (preprocessed array, original size)
    """
    # Load image
    img = Image.open(image_path).convert('RGB')
    original_size = img.size  # (width, height)

    # Resize large images to save memory (OOM prevention)
    if max(original_size) > max_size:
        ratio = max_size / max(original_size)
        new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.BILINEAR)
        logger.info(f'Resized image from {original_size} to {new_size} for processing')

    # Resize to model input size
    img_resized = img.resize((MODEL_INPUT_SIZE, MODEL_INPUT_SIZE), Image.Resampling.BILINEAR)

    # Convert to numpy array and normalize
    img_array = np.array(img_resized, dtype=np.float32)

    # Normalize to [0, 1]
    img_array = img_array / 255.0

    # Apply MiDaS normalization (ImageNet stats)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_array = (img_array - mean) / std

    # Transpose to NCHW format (batch, channels, height, width)
    img_array = img_array.transpose(2, 0, 1)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array, original_size


def postprocess_depth(depth_output: np.ndarray, original_size: tuple) -> np.ndarray:
    """
    Postprocess MiDaS depth output.

    Args:
        depth_output: Raw model output
        original_size: Original image size (width, height)

    Returns:
        Depth map resized to original dimensions, normalized to [0, 1]
    """
    # Remove batch dimension
    depth = depth_output.squeeze()

    # Normalize to [0, 1]
    depth_min = depth.min()
    depth_max = depth.max()
    if depth_max - depth_min > 0:
        depth = (depth - depth_min) / (depth_max - depth_min)
    else:
        depth = np.zeros_like(depth)

    # Resize to original dimensions
    depth_pil = Image.fromarray((depth * 255).astype(np.uint8))
    depth_pil = depth_pil.resize(original_size, Image.Resampling.BILINEAR)

    return np.array(depth_pil, dtype=np.float32) / 255.0


def run_depth_estimation(image_path: str) -> np.ndarray:
    """
    Run MiDaS depth estimation on an image.

    Args:
        image_path: Path to the input image

    Returns:
        Depth map as numpy array (height, width) with values in [0, 1]
        Higher values = closer to camera
        Returns None if ML is not available
    """
    session = get_model()
    if session is None:
        return None

    try:
        # Preprocess
        input_array, original_size = preprocess_image(image_path)

        # Get input name
        input_name = session.get_inputs()[0].name

        # Run inference
        outputs = session.run(None, {input_name: input_array})
        depth_output = outputs[0]

        # Postprocess
        depth_map = postprocess_depth(depth_output, original_size)

        return depth_map

    except Exception as e:
        logger.error(f'Depth estimation failed: {e}')
        return None
