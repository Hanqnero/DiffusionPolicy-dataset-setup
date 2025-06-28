import numpy as np
import time

import rtde_control
import rtde_receive

import controller
import zarr_logger
import camera


class ControllerTeleop:
    def __init__(self, IP):
        print('Connecting to robot at', IP)
        self.rtde_c = rtde_control.RTDEControlInterface(IP)
        self.rtde_r = rtde_receive.RTDEReceiveInterface(IP)

        self.velocityMultiplier = 0.1  # speed in meters per second with ful stick deflection
        self.velocityChangePerTick = 0.0005

        self.controller = controller.ControllerHIDAdapter()
        self.controller.start()

        self.epTick = 0
        self.zarrWriter = zarr_logger.RealTimeZarrWriter(overwrite=False)

        self.stageBtnFlag = False
        self.telemetryStage = 0

        self.cameraManager = camera.CameraManager(
            'recordings', target_fps=30, target_resolution=(640, 480))
        self.recording_running = False

        print('init finished')

    def stop(self):
        self.rtde_c.stopL()

        self.rtde_c.disconnect()
        self.rtde_r.disconnect()
        self.controller.stop()
        self.cameraManager.stop_recording()

    def statusLine(self):
        print(f"Stage: {self.telemetryStage}, Velocity: {
              self.velocityMultiplier:.4f}, Tick: {self.epTick:6d} ", end='\r')

    def handleBtns(self):
        if not self.controller.btnState()[0]:
            self.stageBtnFlag = False
        if not self.controller.btnState()[3]:
            self.endEpFlag = False

        if self.controller.btnState()[0]:
            if not self.stageBtnFlag:
                self.stageBtnFlag = True
                self.telemetryStage = (self.telemetryStage + 1) % 4

        elif self.controller.btnState()[1]:
            self.velocityMultiplier += self.velocityChangePerTick

        elif self.controller.btnState()[2]:
            self.velocityMultiplier -= self.velocityChangePerTick

        elif self.controller.btnState()[3]:
            if not self.endEpFlag:
                self.endEpFlag = True
                self.telemetryStage = 0
                self.epTick = 0
                self.zarrWriter.end_episode()

                if self.recording_running:
                    self.cameraManager.stop_recording()
                    self.recording_running = False
                else:
                    self.cameraManager.start_recording()
                    self.recording_running = True

    def handleTelemetry(self):
        telemetry = {
            'action': self.rtde_r.getTargetTCPPose(),
            'robot_eef_pose': self.rtde_r.getActualTCPPose(),
            'robot_eef_pose_vel': self.rtde_r.getActualTCPSpeed(),
            'robot_joint': self.rtde_r.getActualQ(),
            'robot_joint_vel': self.rtde_r.getActualQd(),
            'stage': np.array([self.telemetryStage]),
            'timestamp': np.array([time.time()])
        }

        if self.recording_running:
            self.zarrWriter.append_data(telemetry)

    def loop(self, target_time=.05):

        while True:
            dt = time.time()

            self.handleBtns()
            self.handleTelemetry()

            self.statusLine()

            left_stick = self.controller.leftStickPos()
            sp = np.zeros(6)
            sp[0] = -left_stick[0] * self.velocityMultiplier
            sp[1] = -left_stick[1] * self.velocityMultiplier

            self.rtde_c.speedL(sp, 1.0)

            dt = time.time() - dt
            if dt > target_time:
                print("WARN cycle time too high")
            else:
                sleep_time = max(0, target_time - dt)
                time.sleep(sleep_time)
            self.epTick += 1


if __name__ == '__main__':
    ROBOT_IP = '192.168.86.5'
    # ROBOT_IP = 'localhost'
    t = ControllerTeleop(ROBOT_IP)

    t.cameraManager.add_camera(
        "rtsp://root:admin@192.168.86.37/axis-media/media.amp")
    t.cameraManager.add_camera(
        "rtsp://root:admin@192.168.86.39/axis-media/media.amp")

    try:
        t.loop()
    except KeyboardInterrupt:
        ...
    finally:
        t.stop()
