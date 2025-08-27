import bpy
import socket
import json
import threading
import math
import mathutils
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Change to INFO or ERROR if needed
logger = logging.getLogger("Maptur_Logger")



# Network Configuration
HOST = "192.168.1.XXX"  # Your Comptuers Local IP Address
PORT = 9000            # Your Computer's Port which will be recieving the Data
REPORTING_RATE = 60    # Reporting Rate in Hz


# Get the Camera within the Scene we would like to use
camera = bpy.data.objects.get("Camera") # Set this to the Camera that you desire to apply the motion data to
if not camera:
    logger.error("Camera not found in the scene!")
    raise ValueError("Camera not found in the scene!")



# Function for Recieiving the IMU Data
def receive_imu_data():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.bind((HOST, PORT))
            logger.info(f"Listening for IMU data on {HOST}:{PORT}...")
        except Exception as e:
            logger.error(f"Failed to bind to port {PORT}. Error: {e}")
            return

        buffer = ""  # Holds fragmented JSON data

        while True:
            try:
                # Receive data
                data, _ = sock.recvfrom(4096)  # Larger buffer to prevent cutting
                received_text = data.decode("utf-8").strip() # Decoding Data from Packets

                # Append new data to the buffer
                buffer += received_text

                # Extract full JSON objects from the buffer
                while "{" in buffer and "}" in buffer:
                    start = buffer.index("{")
                    end = buffer.index("}") + 1  # Ensure we get the full JSON

                    json_string = buffer[start:end]
                    buffer = buffer[end:]  # Remove processed JSON from buffer

                    #logger.debug(f"Extracted JSON: {json_string}") Log the extracted JSON if needed

                    # Parse JSON Data
                    try:
                        imu_data = json.loads(json_string)
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON Decoding Error: {e}")
                        continue

                    # Extract Quaternion Data from Data Stream
                    qw = float(imu_data.get("motionQuaternionW", 1))
                    qx = float(imu_data.get("motionQuaternionX", 0))
                    qy = float(imu_data.get("motionQuaternionY", 0))
                    qz = float(imu_data.get("motionQuaternionZ", 0))

                    # logger.info(f"IMU Quaternion Data: W={qw}, X={qx}, Y={qy}, Z={qz}") (Log Data for Debugging)

                    # Convert Quaternion to Euler
                    quaternion = mathutils.Quaternion((qw, qx, qy, qz))
                    euler_rotation = quaternion.to_euler('XYZ')

                    # Apply Rotation to Blender Camera
                    def update_camera():
                        if camera:
                            camera.rotation_euler = euler_rotation
                            logger.debug(f"Updated Camera Rotation: {camera.rotation_euler}")
                        else:
                            logger.error("Camera object is missing!")

                    bpy.app.timers.register(update_camera, first_interval=(1 / REPORTING_RATE))

            except Exception as e:
                logger.error(f"Error receiving data: {e}")




# Start Network Listener in a Separate Thread (Prevents Performance Issues)
imu_thread = threading.Thread(target=receive_imu_data, daemon=True)
imu_thread.start()

logger.info("Camera Tracking Running...") # Indicates that the script is active
