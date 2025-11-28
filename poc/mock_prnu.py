import hashlib
import time

class MockPRNU:
    """
    Simulates the Hardware Root of Trust and PRNU (Photo Response Non-Uniformity) logic.
    In a real implementation, this would interface with the TEE and hardware sensor.
    """
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id

    def generate_zk_proof(self, video_path, timestamp):
        """
        Simulates generating a Zero-Knowledge Proof binding the sensor ID,
        video content, and timestamp.
        """
        # SIMULATION: In reality, this uses a ZK-SNARK library
        # Combines Sensor ID + Timestamp + Video Hash
        data_to_sign = f"{self.sensor_id}{timestamp}{video_path}"
        return hashlib.sha256(data_to_sign.encode()).hexdigest()

    def check_liveness(self):
        """
        Simulates the Passive Liveness / Anti-Matrix Check.
        Real implementation would analyze Optical Flow and Moire patterns.
        """
        # SIMULATION: Returns True if "3D Parallax" is detected
        return True
