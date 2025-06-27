import rtde_receive
import rtde_control
import time
import numpy as np

IP = '127.0.0.1'

rtde_c = rtde_control.RTDEControlInterface(IP, 50.0)
rtde_r = rtde_receive.RTDEReceiveInterface(IP)

START_Q = q = rtde_r.getTargetQ()
print(f"Start Q: {q}")

START_POSE = pose = rtde_r.getTargetTCPPose()
START_POSE = np.array(START_POSE)


print(f"Start Pose: {pose}")

input()
pose[-2] = 0
rtde_c.moveJ(pose, .3, .5)

pose = rtde_r.getTargetTCPPose()
pose = np.array(pose)

print(pose - START_POSE) 
