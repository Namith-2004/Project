import os
import cv2
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer, BaseHTTPRequestHandler
import mimetypes
import controller as cnt
from cvzone.HandTrackingModule import HandDetector

# Initialize Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# ESP32-CAM stream URL
ESP32_CAM_URL = "http://192.168.1.128:81/stream" 
video = cv2.VideoCapture(0)

# Video capture setup
# video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set resolution
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video.set(cv2.CAP_PROP_FPS, 60)  # Set the desired frame rate


# Shared variable for the video frame
current_frame = None
frame_lock = threading.Lock()

# Function to correctly detect finger states
def correct_fingers_up(hand):
    fingers_up = [0, 0, 0, 0, 0]  # Initialize all fingers as down
    tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
    lm_list = hand['lmList']
    hand_type = hand['type']  # Left or Right hand

    # Thumb: Check the x-coordinates relative to the hand type
    if hand_type == "Right":
        if lm_list[tip_ids[0]][0] < lm_list[tip_ids[0] - 1][0]:  # Thumb is open
            fingers_up[0] = 1
    else:  # Left hand
        if lm_list[tip_ids[0]][0] > lm_list[tip_ids[0] - 1][0]:  # Thumb is open
            fingers_up[0] = 1

    # Other fingers: Check y-coordinates (higher means open)
    for i in range(1, 5):
        if lm_list[tip_ids[i]][1] < lm_list[tip_ids[i] - 2][1]:
            fingers_up[i] = 1

    return fingers_up

# Thread to continuously capture frames
def capture_frames():
    global current_frame
    while True:
        success, frame = video.read()
        if not success:
            break
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally
        hands, img = detector.findHands(frame, flipType=False)

    # global current_frame
    
    # if not cap.isOpened():
    #     print("Error: Unable to connect to ESP32-CAM stream")
    #     return

    # while True:
    #     success, frame = cap.read()
    #     if not success:
    #         print("Error: Failed to fetch frame from ESP32-CAM")
    #         break

    #     frame = cv2.flip(frame, 1)  # Flip the frame horizontally
    #     hands, img = detector.findHands(frame, flipType=False)
        if hands:
            fingers_up = correct_fingers_up(hands[0])  # Get correct finger states
            cnt.led(fingers_up,1)
            if fingers_up==[0,0,0,0,0]:
                cv2.putText(frame,'Finger count:0',(20,460),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)
            elif fingers_up==[0,1,0,0,0]:
                cv2.putText(frame,'Finger count:1',(20,460),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)    
            elif fingers_up==[0,1,1,0,0]:
                cv2.putText(frame,'Finger count:2',(20,460),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)
            elif fingers_up==[0,1,1,1,0]:
                cv2.putText(frame,'Finger count:3',(20,460),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)
            elif fingers_up==[0,1,1,1,1]:
                cv2.putText(frame,'Finger count:4',(20,460),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1,cv2.LINE_AA)
            elif fingers_up==[1,1,1,1,1]:
                cv2.putText(frame,'Finger count:5',(20,460),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1,cv2.LINE_AA) 


            # Display finger count
            # finger_count = sum(fingers_up)
            # cv2.putText(
            #     frame,
            #     f'Finger count: {finger_count}',
            #     (20, 460),
            #     cv2.FONT_HERSHEY_COMPLEX,
            #     1,
            #     (255, 255, 255),
            #     1,
            #     cv2.LINE_AA,
            # )

        with frame_lock:
            current_frame = frame

# Video feed server
class VideoFeedHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/video_feed":
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            while True:
                if current_frame is None:
                    continue

                with frame_lock:
                    _, jpeg = cv2.imencode('.jpg', current_frame)

                self.wfile.write(b'--frame\r\n')
                self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
            return

        self.send_error(404, "Not Found")

# Static file server
def run_static_file_server():
    class StaticServer(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self.path = "/landing.html"  # Serve the landing page by default
            super().do_GET()

    os.chdir("static")  # Serve files from the 'static' directory
    server = HTTPServer(('0.0.0.0', 8080), StaticServer)
    print("Static file server started at http://localhost:8080")
    server.serve_forever()

# Video feed server function
def start_video_feed_server():
    server = HTTPServer(('0.0.0.0', 8000), VideoFeedHandler)
    print("Video feed server started at http://localhost:8000/video_feed")
    server.serve_forever()

# Main function
if __name__ == "__main__":
    # Start the static file server in a separate thread
    static_server_thread = threading.Thread(target=run_static_file_server, daemon=True)
    static_server_thread.start()

    # Start the video capture thread
    capture_thread = threading.Thread(target=capture_frames, daemon=True)
    capture_thread.start()

    # Start the video feed server
    try:
        start_video_feed_server()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    finally:
        # cap.release()
        video.release()
        print("Video capture released.")