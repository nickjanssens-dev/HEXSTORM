import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from tensorflow.keras.models import load_model

import cv2  # Install opencv-python
import numpy as np
import time
import sys

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model - matching the local filename
MODEL_PATH = "keras_model.h5"
LABELS_PATH = "labels.txt"

if not os.path.exists(MODEL_PATH):
    print(f"ERROR: Model file {MODEL_PATH} not found.")
    sys.stdout.flush()
    sys.exit(1)

model = load_model(MODEL_PATH, compile=False)

# Load the labels
if not os.path.exists(LABELS_PATH):
    print(f"ERROR: Labels file {LABELS_PATH} not found.")
    sys.stdout.flush()
    sys.exit(1)
    
class_names = open(LABELS_PATH, "r").readlines()

# Set to False to hide the webcam window
SHOW_WINDOW = True

# CAMERA can be 0 or 1 based on default camera of your computer
camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not camera.isOpened():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("ERROR: Could not open any webcam.")
    sys.stdout.flush()
    sys.exit(1)

# Create the array of the right shape to feed into the keras model
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Timing variables - making them slightly more forgiving than before
target_confidence = 0.85 
required_duration = 2.0  
delay_between_cards = 1.0 

current_class = None
start_time = None
cooldown_end_time = 0

print("Webcam initialized. Press 'esc' to exit.")
sys.stdout.flush()

try:
    while True:
        # Grab the webcameras image.
        ret, image = camera.read()
        if not ret:
            print("ERROR: Failed to grab frame")
            sys.stdout.flush()
            break

        # Resize the raw image into (224-height,224-width) pixels
        resized_image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Show the image in a window if enabled
        if SHOW_WINDOW:
            cv2.imshow("Webcam Image", image)

        # Preprocess the image for the model
        img_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        image_array = np.asarray(img_rgb)

        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

        # Load the image into the array
        data[0] = normalized_image_array

        # Predicts the model
        prediction = model.predict(data, verbose=0)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        # Display prediction on screen if window is open
        if SHOW_WINDOW:
            display_text = f"Class: {class_name[2:]} ({confidence_score:.2f})"
            cv2.putText(image, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Webcam Image", image)
            if cv2.waitKey(1) == 27: # Esc
                break

        # Log detections to terminal for transparency
        sys.stderr.write(f"\rAI DETECTION: {class_name[2:]} ({confidence_score:.2f})")
        
        # Check if we are in cooldown
        current_time = time.time()
        if current_time < cooldown_end_time:
            # remaining_cooldown = cooldown_end_time - current_time
            pass
        else:
            # Check for high confidence
            if confidence_score >= target_confidence:
                if current_class != index:
                    # New class detected with high confidence
                    current_class = index
                    start_time = current_time
                    print(f"Detected {class_name[2:]}... Hold for {required_duration}s")
                    sys.stdout.flush()
                else:
                    # Same class detected, check duration
                    elapsed = current_time - start_time
                    if elapsed >= required_duration:
                        # Success result format: +++ GAME_RESULT: <Name> +++
                        print(f"\n+++ GAME_RESULT: {class_name[2:]} +++")
                        sys.stdout.flush()

                        # Set cooldown for the next card
                        cooldown_end_time = current_time + delay_between_cards
                        current_class = None
                        start_time = None
            else:
                # Confidence dropped, reset timer
                if current_class is not None:
                    print(f"\nConfidence dropped ({confidence_score:.2f}). Resetting timer.")
                    sys.stdout.flush()
                    current_class = None
                    start_time = None

        # Small sleep
        time.sleep(0.01)

finally:
    camera.release()
    cv2.destroyAllWindows()
