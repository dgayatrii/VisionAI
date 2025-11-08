import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. SET UP PATHS ---
# Adjust these paths to match your project structure
BASE_DIR = r"E:\DRdetection\dataset"
TEST_CSV_PATH = os.path.join(BASE_DIR, "test.csv")
TEST_IMG_DIR = os.path.join(BASE_DIR, "test_images")
MODEL_PATH = r"E:\DRdetection\models\best_model.keras"

# --- 2. LOAD AND PREPROCESS TEST DATA ---
print("Loading and preprocessing test data...")

# Load the CSV file
test_df = pd.read_csv(TEST_CSV_PATH)

# Function to load and preprocess a single image
def preprocess_image(image_path, target_size=(224, 224)):
    try:
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=target_size)
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Create a batch
        img_array /= 255.0  # Rescale to [0,1]
        return img_array
    except FileNotFoundError:
        print(f"Warning: Image not found at {image_path}. Skipping.")
        return None

# Load all test images and their true labels
test_images = []
true_labels = []

for index, row in test_df.iterrows():
    image_path = os.path.join(TEST_IMG_DIR, str(row['id_code']) + '.png')
    processed_image = preprocess_image(image_path)
    
    if processed_image is not None:
        test_images.append(processed_image)
        true_labels.append(row['diagnosis'])

# Convert lists to numpy arrays for efficiency
test_images = np.vstack(test_images) # Stack images into a single batch
true_labels = np.array(true_labels)

print(f"Loaded {len(true_labels)} test images.")

# --- 3. LOAD THE TRAINED MODEL ---
print(f"Loading model from {MODEL_PATH}...")
model = tf.keras.models.load_model(MODEL_PATH)

# --- 4. MAKE PREDICTIONS ---
print("Making predictions on the test set...")
predictions = model.predict(test_images)
predicted_labels = np.argmax(predictions, axis=1)

# --- 5. EVALUATE THE MODEL ---
print("\n--- Model Evaluation Results ---")

# Calculate and print accuracy as a percentage
accuracy = accuracy_score(true_labels, predicted_labels)
print(f"\n✅ Overall Accuracy: {accuracy * 100:.2f}%")

# Generate Classification Report (Precision, Recall, F1-Score)
print("\n📊 Classification Report:")
# Assuming your class labels are 0, 1, 2, 3, 4
class_names = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']
report = classification_report(true_labels, predicted_labels, target_names=class_names)
print(report)

# Generate and Display Confusion Matrix
print("\n📈 Confusion Matrix:")
cm = confusion_matrix(true_labels, predicted_labels)
print("The matrix shows true labels on the y-axis and predicted labels on the x-axis.")

# Plot the confusion matrix for better visualization
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.title('Confusion Matrix')
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.show()