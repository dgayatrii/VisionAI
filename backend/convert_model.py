import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # goes to project root
old_model_path = os.path.join(BASE_DIR, "models", "best_model.h5")
new_model_path = os.path.join(BASE_DIR, "models", "best_model.keras")

print("Loading old model...")
model = tf.keras.models.load_model(old_model_path, compile=False)

print("Saving in new format...")
model.save(new_model_path)
print("✅ Conversion complete:", new_model_path)
