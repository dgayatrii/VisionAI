

# #backend_utils.py
# import os
# import json
# import numpy as np
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.models import load_model

# ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# MODEL_PATH = os.path.join(ROOT_DIR, "models", "best_model.keras")
# CLASS_PATH = os.path.join(ROOT_DIR, "models", "class_indices.json")

# ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def preprocess_image(img_path, target_size=(224, 224)):
#     img = image.load_img(img_path, target_size=target_size)
#     x = image.img_to_array(img)
#     x = x / 255.0
#     x = np.expand_dims(x, axis=0)
#     return x

# def load_class_mapping():
#     if not os.path.exists(CLASS_PATH):
#         raise FileNotFoundError(f"Class mapping JSON not found at {CLASS_PATH}")
#     with open(CLASS_PATH, "r") as f:
#         class_mapping = json.load(f)
#     return {int(k): v for k, v in class_mapping.items()}

# def load_dr_model():
#     if not os.path.exists(MODEL_PATH):
#         raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
#     print(f"✅ Loading model from: {MODEL_PATH}")
#     return load_model(MODEL_PATH)


# backend_utils.py

import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing import image

# --- Constants and Path Definitions ---

# Use pathlib for a modern, object-oriented approach to paths
# ROOT_DIR is the main project folder (e.g., DRDETECTION)
ROOT_DIR: Path = Path(__file__).resolve().parent.parent
MODEL_PATH: Path = ROOT_DIR / "models" / "best_model.keras"
CLASS_PATH: Path = ROOT_DIR / "models" / "class_indices.json"

# Set of allowed image file extensions
ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg"}


# --- Helper Functions ---

def allowed_file(filename: str) -> bool:
    """
    Checks if an uploaded file has an allowed image extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file extension is in ALLOWED_EXTENSIONS, False otherwise.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(
    img_path: str | Path, target_size: Tuple[int, int] = (224, 224)
) -> np.ndarray:
    """
    Loads, resizes, normalizes, and prepares an image for model prediction.

    Args:
        img_path (str | Path): The file path of the image.
        target_size (Tuple[int, int], optional): The target size for the image. Defaults to (224, 224).

    Returns:
        np.ndarray: The preprocessed image as a NumPy array with a batch dimension.
    """
    img = image.load_img(img_path, target_size=target_size)
    x = image.img_to_array(img)
    x = x / 255.0  # Normalize pixel values to the [0, 1] range
    x = np.expand_dims(x, axis=0)  # Add a batch dimension
    return x


def load_class_mapping() -> Dict[int, str]:
    """
    Loads the class index to class name mapping from a JSON file.

    Raises:
        FileNotFoundError: If the class_indices.json file is not found.

    Returns:
        Dict[int, str]: A dictionary mapping the integer class index to the string label.
    """
    if not CLASS_PATH.is_file():
        raise FileNotFoundError(f"Class mapping JSON not found at {CLASS_PATH}")
    with open(CLASS_PATH, "r") as f:
        class_mapping = json.load(f)
    # Convert string keys from JSON to integers for model output compatibility
    return {int(k): v for k, v in class_mapping.items()}


def load_dr_model() -> Model:
    """
    Loads the trained Keras model for Diabetic Retinopathy detection.

    Raises:
        FileNotFoundError: If the model file (best_model.keras) is not found.

    Returns:
        Model: The loaded TensorFlow/Keras model.
    """
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    print(f"✅ Loading model from: {MODEL_PATH}")
    return load_model(MODEL_PATH)