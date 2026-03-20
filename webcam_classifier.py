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
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not camera.isOpened():
    camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("ERROR: Could not open any webcam.")
    sys.stdout.flush()
    sys.exit(1)

# Create the array of the right shape to feed into the keras model
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Timing variables
confidence_threshold = 0.85
no_card_threshold = 0.80
REQUIRED_HOLD_TIME = 0.3  # seconds to hold card before casting

current_class = None
last_fired_class = None
class_start_time = None  # Track when current class was first detected

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
        
        class_name_clean = class_name[2:].strip()
        is_no_card = (class_name_clean == "No card")
        
        # State machine: ready OR waiting for no card
        if last_fired_class is None:
            # Ready to fire - track card detection timing
            if not is_no_card and confidence_score >= confidence_threshold:
                if class_start_time is None:
                    # Start timing when we first detect this card
                    class_start_time = time.time()
                    current_class = class_name_clean
                elif class_name_clean == current_class:
                    # Same card detected, check if we've held it long enough
                    held_time = time.time() - class_start_time
                    if held_time >= REQUIRED_HOLD_TIME:
                        # Fire after holding for required time
                        print(f"\n+++ GAME_RESULT: {class_name_clean} +++")
                        sys.stdout.flush()
                        last_fired_class = class_name_clean
                        class_start_time = None  # Reset timing
                else:
                    # Different card detected, restart timing
                    class_start_time = time.time()
                    current_class = class_name_clean
            else:
                # No card detected, reset timing
                class_start_time = None
                current_class = None
        else:
            # Waiting for "No card" to reset
            if is_no_card and confidence_score >= no_card_threshold:
                last_fired_class = None
                class_start_time = None
                current_class = None

        # Small sleep
        time.sleep(0.01)

finally:
    camera.release()
    cv2.destroyAllWindows()
