import zarr
import numpy as np
import os
import shutil
import time

DATA_ARRAY_SPECS = {
    'action': ((0, 6), 'float32'),              # getTargetT
    'robot_eef_pose': ((0, 6), 'float32'),      # getActualT
    'robot_eef_pose_vel': ((0, 6), 'float32'),  # getActualTCPSpeed
    'robot_joint': ((0, 6), 'float32'),         # getActualQ
    'robot_joint_vel': ((0, 6), 'float32'),     # getActualQd
    'stage': ((0,), 'int8'),
    'timestamp': ((0,), 'int64')
}

ZARR_PATH = "new_replay_buffer.zarr"

class RealTimeZarrWriter:
    def __init__(self, zarr_path=ZARR_PATH, data_specs=DATA_ARRAY_SPECS, overwrite=False):
        self.zarr_path = zarr_path

        if overwrite and os.path.exists(zarr_path):
            shutil.rmtree(zarr_path)

        self.root = zarr.open(zarr_path, mode='a') # Use append mode

        # Create main groups if they don't exist
        self.data_group = self.root.require_group('data')
        self.meta_group = self.root.require_group('meta')

        # Create data arrays based on the provided specifications
        for name, (shape, dtype) in data_specs.items():
            if name not in self.data_group:
                chunks = (100,) + shape[1:] if len(shape) > 1 else (100,)
                self.data_group.create_array(name, shape=shape, chunks=chunks, dtype=dtype)

        # Create metadata arrays
        if 'episode_ends' not in self.meta_group:
            self.meta_group.create_array('episode_ends', shape=(0,), chunks=(100,), dtype='i8')


    def append_data(self, timestep_data):
        for name, data in timestep_data.items():
            if name in self.data_group:
                # print(f"Appending to `{name}` data {data}")
                if isinstance(data, list):
                    data = np.array(data).reshape((1,6))
                self.data_group[name].append(data)
            else:
                print(f"Warning: Array '{name}' not found in data specifications.")


    def end_episode(self):
        """
        Marks the end of an episode by recording the current number of data points.
        """
        # Use the 'action' array's length as the reference for the total number of timesteps
        current_len = self.data_group['action'].shape[0]
        self.meta_group['episode_ends'].append([current_len])



if __name__ == '__main__':
    ZARR_PATH = "new_replay_buffer_oop.zarr"

    # --- Example Usage ---
    print(f"Creating and populating Zarr dataset at: {ZARR_PATH}")
    writer = RealTimeZarrWriter(ZARR_PATH, DATA_ARRAY_SPECS, overwrite=False)

    print("Initial structure:")
    writer.root.tree()

    # Simulate logging two episodes in real-time
    for episode_idx in range(2):
        print(f"\n--- Logging Episode {episode_idx + 1} ---")
        episode_length = 50 + episode_idx * 10  # Make episodes different lengths
        for i in range(episode_length):
            # In a real application, this data would come from your robot sensors/controller
            timestep_data = {
                'action': np.random.rand(1, 6),
                'robot_eef_pose': np.random.rand(1, 6),
                'robot_eef_pose_vel': np.random.rand(1, 6),
                'robot_joint': np.random.rand(1, 6),
                'robot_joint_vel': np.random.rand(1, 6),
                'stage': np.array([episode_idx]),
                'timestamp': np.array([time.time()])
            }
            writer.append_data(timestep_data)

        # Mark the end of the episode
        writer.end_episode()
        print(f"Episode {episode_idx + 1} finished and marked.")

    print("\n--- Finished Logging ---")
    print("\nFinal dataset structure:")
    writer.root.tree()

    # Verification
    print("\nVerification:")
    final_episode_ends = list(writer.root['meta/episode_ends'])
    print(f"Episode end markers: {final_episode_ends}")
    assert final_episode_ends[0] == 50
    assert final_episode_ends[1] == 110
    print("Verification successful!")
    writer.root.tree()