import cv2
import mediapipe as mp
from twilio.rest import Client
import time

# Twilio setup (fill these with your actual Twilio account information)
account_sid ='twilio account sid'
auth_token = 'twilio auth token'
twilio_phone_number = 'Your Twilio phone number'
recipient_phone_number ='person yoiu want to call'

# Set up Twilio client
client = Client(account_sid, auth_token)

# Set up MediaPipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Set up video capture
cap = cv2.VideoCapture(0)

# Fall detection function
def detect_fall(landmarks):
    try:
        head_y = landmarks[0].y  # Head
        hip_y = landmarks[24].y   # Hip
        ankle_y = landmarks[28].y # Ankle

        # Fall detection logic
        if head_y > ankle_y - 0.1 and hip_y > ankle_y - 0.1:
            return True
        return False
    except IndexError:
        return False

# Function to make a call to the recipient if a fall is detected
def make_call():
    print("Fall detected! Calling emergency contact...")

    # Making a phone call using Twilio
    call = client.calls.create(
        to=recipient_phone_number,
        from_=twilio_phone_number,
        url="http://demo.twilio.com/docs/voice.xml"
    )

    print(f"Call initiated: {call.sid}")

# Main loop
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the image to RGB for pose processing
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    # If landmarks are detected, draw them on the frame
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Check for fall detection
        if detect_fall(results.pose_landmarks.landmark):
            cv2.putText(frame, "FALL DETECTED!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # If fall detected, make a call
            make_call()
            time.sleep(10)  # Pause to avoid multiple calls during one fall

    # Display the frame
    cv2.imshow("Fall Detection", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Release resources and close the window
cap.release()
cv2.destroyAllWindows()
