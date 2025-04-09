import cv2
import numpy as np
import serial
import time

# Initialize serial communication with Arduino
try:
    arduino = serial.Serial('COM5', 9600)  # Replace with the correct port
    time.sleep(2)  # Allow time for Arduino to initialize
except Exception as e:
    print(f"Error: Unable to connect to Arduino: {e}")
    exit()

# Open the camera
cap = cv2.VideoCapture(0)

# Check if the camera is opened correctly
if not cap.isOpened():
    print("Error: Unable to open the camera.")
    exit()

# Define the ArUco dictionary and detector parameters
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)  # Use your dictionary type
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

# Variables to track detection and servo state
marker_detected = False
last_command_time = time.time()
cooldown_duration = 2  # Cooldown period in seconds

try:
    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()

        if not ret:
            print("Error: Unable to read the frame.")
            break  # Exit the loop if there's an issue with reading the frameq

        # Detect markers in the frame
        markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(frame)

        current_time = time.time()

        if markerIds is not None:
            # If any ArUco markers are detected
            print(f"ArUco marker(s) detected! IDs: {markerIds.flatten()}")

            # Draw detected markers on the frame
            for corners in markerCorners:
                cv2.polylines(frame, [corners.astype(int)], True, (0, 255, 0), 2)

            # If marker is detected and cooldown period has passed, move servo to 0 degrees
            if not marker_detected and current_time - last_command_time > cooldown_duration:
                print("Sending 0 degrees command to Arduino")
                arduino.write(b'0')  # Send command to Arduino to move servo to 0 degrees
                marker_detected = True  # Update detection state
                last_command_time = current_time

        else:
            # If no markers are detected and cooldown period has passed, move servo back to 90 degrees
            if marker_detected and current_time - last_command_time > cooldown_duration:
                print("No marker detected, sending 90 degrees command to Arduino")
                arduino.write(b'9')  # Send command to Arduino to move servo back to 90 degrees
                marker_detected = False  # Reset detection state
                last_command_time = current_time

        # Display the frame with detected markers
        cv2.imshow("Frame", frame)

        # Exit if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    # Release resources and close connections
    print("Releasing resources...")
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
    print("Arduino connection closed.")
