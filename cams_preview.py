import cv2
import threading
import numpy as np
import time

class CameraStream:
    def __init__(self, stream_url, name="Camera"):
        self.stream_url = stream_url
        self.name = name
        self.cap = None
        self.frame = None
        self.running = False
        self.thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5 # seconds


    def start(self):
        self.cap = cv2.VideoCapture(self.stream_url)
        if not self.cap.isOpened():
            print(f"Error: Could not open stream for {self.name}. Retrying...")
            self.reconnect_attempts += 1
            if self.reconnect_attempts <= self.max_reconnect_attempts:
                time.sleep(self.reconnect_delay)
                self.start() # Recursive call to retry
            else:
                print(f"Failed to open stream for {self.name} after {self.max_reconnect_attempts} attempts.")
                self.running = False
                return
        else:
            self.running = True
            self.thread = threading.Thread(target=self._update, args=())
            self.thread.daemon = True # Thread will close when main program exits
            self.thread.start()
            print(f"Successfully started stream for {self.name}.")

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print(f"Warning: Lost connection to {self.name}. Attempting to reconnect...")
                self.reconnect_attempts = 0
                self.stop()
                self.start() # Attempt to restart the stream
                if not self.running: # If restart failed after max attempts
                    break
            else:
                self.frame = frame
                self.reconnect_attempts = 0 # Reset attempts on successful read
            time.sleep(0.01) # Small delay to prevent busy-waiting

    def read(self):
        return self.frame

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1) # Wait for thread to finish
        if self.cap and self.cap.isOpened():
            self.cap.release()
            print(f"Stream for {self.name} stopped.")

    def is_running(self):
        return self.running and self.cap and self.cap.isOpened()

def main():
    
    CAM_CRED = 'root:admin'
    CAM_IPS = [
        '192.168.86.37',
        '192.168.86.39',
        ]
    camera_urls = [f"rtsp://{CAM_CRED}@{ip}/axis-media/media.amp" for ip in CAM_IPS]
    
    camera_streams = []
    for i, url in enumerate(camera_urls):
        cam = CameraStream(url, name=f"Camera {i+1}")
        cam.start()
        camera_streams.append(cam)

    time.sleep(2)

    try:
        while True:
            frames_to_display = []
            for cam in camera_streams:
                if cam.is_running():
                    frame = cam.read()
                    if frame is not None:
                        # Resize frame for consistent display, e.g., to 640x480
                        frame_resized = cv2.resize(frame, (640, 480))
                        # Add camera name to the frame for identification
                        cv2.putText(frame_resized, cam.name, (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        frames_to_display.append(frame_resized)
                    else:
                        # If a camera is running but hasn't provided a frame yet,
                        # or frame is None, you might want to display a placeholder.
                        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                        cv2.putText(placeholder, f"{cam.name} - No Signal", (50, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                        frames_to_display.append(placeholder)
                else:
                    # If a camera failed to start or stopped, display an error placeholder
                    placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(placeholder, f"{cam.name} - Disconnected", (50, 240),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    frames_to_display.append(placeholder)


            if not frames_to_display:
                print("No active camera streams to display. Exiting.")
                break


            if len(frames_to_display) == 1:
                combined_frame = frames_to_display[0]
            elif len(frames_to_display) == 2:
                combined_frame = np.hstack(frames_to_display)
            else:
                cols = 2
                rows = (len(frames_to_display) + cols - 1) // cols
                
                # Pad frames if not a perfect fit for grid
                while len(frames_to_display) % cols != 0:
                    frames_to_display.append(np.zeros((480, 640, 3), dtype=np.uint8))
                    
                rows_of_frames = []
                for i in range(rows):
                    start_idx = i * cols
                    end_idx = start_idx + cols
                    row_frames = frames_to_display[start_idx:end_idx]
                    if row_frames:
                        rows_of_frames.append(np.hstack(row_frames))
                
                if rows_of_frames:
                    combined_frame = np.vstack(rows_of_frames)
                else:
                    combined_frame = np.zeros((480, 640, 3), dtype=np.uint8)


            cv2.imshow('Multi-Camera Live View', combined_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        # Release all camera streams and close windows
        for cam in camera_streams:
            cam.stop()
        cv2.destroyAllWindows()
        print("All streams released and windows closed.")

if __name__ == '__main__':
    main()
