import cv2
import os
import threading
import time
from pathlib import Path


class CameraThread(threading.Thread):
    def __init__(self, cam_id, cam_src, output_path, target_fps, target_resolution):
        super().__init__()
        
        self.cam_id = cam_id
        self.cam_src = cam_src
        self.output_path = output_path
        self.fps = target_fps
        self.resolution = target_resolution  # (width, height)

        self.running = threading.Event()

        self.cap = None
        self.writer = None

        print(f"[Camera {self.cam_id}] Initializing camera thread.")
        self.cap = cv2.VideoCapture(self.cam_src)

        if not self.cap.isOpened():
            print(f"[Camera {self.cam_id}] Failed to open source: {self.cam_src}")
            

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_file = os.path.join(self.output_path, f"{self.cam_id}.mp4")
        self.writer = cv2.VideoWriter(out_file, fourcc, self.fps, self.resolution)

        print(f"[Camera {self.cam_id}] Recording started.")
        self.running.set()


    def run(self):
        try:
            while self.running.is_set():
                ret, frame = self.cap.read()

                if not ret:
                    print(f"[Camera {self.cam_id}] Failed to read frame.")
                    break

                resized = cv2.resize(frame, self.resolution)
                self.writer.write(resized)
        except Exception as e:
            print(f"[Camera {self.cam_id}] Exception occurred: {e}")
        finally:
            self.cleanup()
            print(f"[Camera {self.cam_id}] Recording stopped and saved.")

    def stop(self):
        self.running.clear()

    def cleanup(self):
        if self.cap:
            self.cap.release()
        if self.writer:
            self.writer.release()


class CameraManager:
    def __init__(self, root_dir="recordings", target_fps=30, target_resolution=(640, 480)):
        self.root_dir = Path(root_dir)
        self.cameras = {}

        self.recording_id = self._get_init_recording_id()

        self.threads = []
        self.target_fps = target_fps
        self.target_resolution = target_resolution  # (width, height)

    
    def _get_init_recording_id(self):
        if not self.root_dir.exists():
            return 0
        recordings = [d for d in self.root_dir.iterdir() if d.is_dir()]
        if not recordings:
            return 0
        return len(recordings) 


    def add_camera(self, cam_src):
        cam_id = len(self.cameras)
        self.cameras[cam_id] = cam_src
        print(f"[Manager] Added camera {cam_id}: {cam_src}")


    def _prepare_recording_folder(self):
        session_dir = self.root_dir / str(self.recording_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    

    def start_recording(self):
        if not self.cameras:
            print("[Manager] No cameras to record.")
            return

        session_path = self._prepare_recording_folder()
        self.threads.clear()

        for cam_id, cam_src in self.cameras.items():
            thread = CameraThread(cam_id, cam_src, session_path, self.target_fps, self.target_resolution)
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()
            print(f"[Manager] Camera {thread.cam_id} thread started.")

        for thread in self.threads:
            if not thread.running.wait(timeout=5):
                print(f"[Manager] Camera {thread.cam_id} failed to start recording in time. Skipping.")


        print(f"[Manager] Recording session {self.recording_id} started.")


    def stop_recording(self):
        print(f"[Manager] Stopping all camera threads.")
        for thread in self.threads:
            thread.stop()
            print(f"[Manager] Camera {thread.cam_id} thread stopped.")
        print(f"[Manager] Recording session {self.recording_id} finished.")
        self.recording_id += 1

    def set_root_dir(self, new_root):
        self.root_dir = Path(new_root)
        print(f"[Manager] Root directory set to: {self.root_dir.resolve()}")


if __name__ == "__main__":
    cam_manager = CameraManager(root_dir="recordings", target_fps=30, target_resolution=(640, 480))
    
    cam_manager.add_camera("rtsp://root:admin@192.168.86.37/axis-media/media.amp")
    cam_manager.add_camera("rtsp://root:admin@192.168.86.39/axis-media/media.amp")
    # cam_manager.add_camera("rtsp://root:admin@192.186.86.40/axis-media/media.amp")

    print("Starting recording...")
    cam_manager.start_recording()

    print("Stopping recording...")
    cam_manager.stop_recording()

    print("Starting recording...")
    cam_manager.start_recording()

    print("Stopping recording...")
    cam_manager.stop_recording()