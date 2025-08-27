# Maptur Free Edition (Blender)

A Blender script for real-time camera motion tracking using mobile device IMU (Inertial Measurement Unit) data over local network connection.

## Features

- **Real-time Motion Tracking**: Process rotation data from iOS device IMU sensors
- **High Reporting Rate**: Supports high-frequency data updates (device dependent)
- **Wireless Connection**: Connects via local WiFi network
- **Blender Integration**: Direct camera object manipulation in Blender scenes

## Requirements

- **iOS Device**: Running iOS 18 or newer
- **Computer**: Running Blender
- **Network**: Local WiFi connection with low latency capabilities

> **Important**: Both mobile device and computer must be on the same network. Peer-to-peer connectivity is not supported.

## Recommended iOS App

### SensorLog - Log and Stream Sensor Data

![SensorLog Logo](../Assets/sensor-log-logo.png)

We highly recommend using **SensorLog** - a professional-grade sensor data streaming app designed specifically for applications like motion tracking and real-time data transmission.

#### Why SensorLog?

- **High-Frequency Data**: Supports the high reporting rates needed for smooth motion tracking
- **Reliable Network Streaming**: Built-in UDP broadcasting with stable connection handling
- **Professional Features**: Comprehensive sensor data access and customizable streaming options

#### Download SensorLog

**[App Store Link](https://apps.apple.com/us/app/sensorlog/id388014573?platform=iphone)**

#### Quick Setup with SensorLog

1. Install SensorLog from the App Store
2. Configure SensorLog to broadcast IMU data to your computer's IP address
3. Set the same PORT number in both SensorLog and the Maptur script
4. Adjust the reporting rate to match your REPORTING_RATE setting
5. Start streaming and enjoy real-time camera tracking!


##  Quick Start

1. Configure your network settings in the script (HOST, PORT, REPORTING_RATE)
2. Ensure your iOS device and computer are connected to the same WiFi network
3. Open Blender and load your scene
4. Run the Maptur script in Blender
5. Start your iOS IMU data broadcasting app
6. Begin real-time camera tracking!

## How It Works

### Core Components

#### 1. Library Imports
```python
import bpy
import socket
import json
import threading
import math
import mathutils
import logging
```

#### 2. Logging Setup
The script uses a comprehensive logging system to monitor status and troubleshoot issues:
```python
logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger("Maptur_Logger")
```

#### 3. Network Configuration
Configure your computer's network settings:
```python
HOST = "192.168.1.XXX"  # Your computer's IP address
PORT = 9000             # Choose an available port
REPORTING_RATE = 60     # Update frequency in Hz
```

> 💡 **Configuration Tips**: 
> - Replace `192.168.1.XXX` with your computer's actual IP address
> - Ensure the PORT is not currently in use by another application
> - Adjust REPORTING_RATE based on your network capacity and device performance

#### 4. Camera Object Selection
```python
camera = bpy.data.objects.get("Camera")
if not camera:
    logger.error("Camera not found in the scene!")
    raise ValueError("Camera not found in the scene!")
```
> **Tip**: Change `"Camera"` to match your specific camera object name (case-sensitive)

### Data Processing Pipeline

#### Network Receiver Function
Creates UDP socket connection and handles incoming data:
```python
def receive_imu_data():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.bind((HOST, PORT))
            logger.info(f"Listening for IMU data on {HOST}:{PORT}...")
        except Exception as e:
            logger.error(f"Failed to bind to port {PORT}. Error: {e}")
            return
```

#### Buffer Management
Initialize buffer and process incoming data:
```python
buffer = ""

while True:
    try:
        data, _ = sock.recvfrom(4096) 
        received_text = data.decode("utf-8").strip()
        buffer += received_text
```

#### JSON Data Extraction
Extract complete JSON objects from the buffer:
```python
while "{" in buffer and "}" in buffer:
    start = buffer.index("{")
    end = buffer.index("}") + 1

    json_string = buffer[start:end]
    buffer = buffer[end:]  
```

#### JSON Parsing with Error Handling
Parse the extracted JSON data:
```python
try:
    imu_data = json.loads(json_string)
except json.JSONDecodeError as e:
    logger.warning(f"JSON Decoding Error: {e}")
    continue
```

#### Quaternion Data Parsing
Extract quaternion components from JSON data:
```python
qw = float(imu_data.get("motionQuaternionW", 1))
qx = float(imu_data.get("motionQuaternionX", 0))
qy = float(imu_data.get("motionQuaternionY", 0))
qz = float(imu_data.get("motionQuaternionZ", 0))
```

#### Coordinate System Conversion
Convert quaternions to Euler angles for Blender:
```python
quaternion = mathutils.Quaternion((qw, qx, qy, qz))
euler_rotation = quaternion.to_euler('XYZ')
```

> **Alternative**: Blender can operate in different modes. The default is `XYZ Euler`, but you can use quaternion mode to apply rotations directly with `.rotation_quaternion` (requires slightly more computational power but minimal on modern computers).

#### Camera Updates
Apply rotation data to the camera object:
```python
def update_camera():
    if camera:
        camera.rotation_euler = euler_rotation
        logger.debug(f"Updated Camera Rotation: {camera.rotation_euler}")
    else:
        logger.error("Camera object is missing!")
```

#### Update Timer
Control the update frequency using the configured reporting rate:
```python
bpy.app.timers.register(update_camera, first_interval=(1 / REPORTING_RATE))
```

> **Performance Note**: Scale the REPORTING_RATE according to how fast you're sending data to the receiver for optimal performance.

#### Error Handling
Catch and handle loop errors:
```python
    except Exception as e:
        logger.error(f"Error receiving data: {e}")
```

### Threading & Performance

#### Thread Creation and Startup
```python
# Create network listener on separate thread to prevent performance issues
imu_thread = threading.Thread(target=receive_imu_data, daemon=True)
imu_thread.start()

# Script ready indication
logger.info("Camera Tracking Running...")  # Indicates script is active
```

- **Separate Thread**: Network listening runs on dedicated thread to prevent UI blocking
- **Update Timer**: Respects `REPORTING_RATE` variable for optimal performance
- **Daemon Thread**: Automatically closes when main program exits

## Configuration

### Key Variables to Adjust

- **HOST**: Your computer's IP address on the local network
- **PORT**: Network port for data reception (ensure it's available)
- **REPORTING_RATE**: Update frequency in Hz (balance performance vs. smoothness)
- **Camera Name**: Modify the camera object name in the script to match your scene

### Network Considerations

- Ensure your WiFi network can handle low-latency, high-frequency data transmission
- Consider network congestion and bandwidth limitations
- Test different reporting rates to find optimal performance
- Use a stable, high-quality WiFi connection for best results

## Troubleshooting

### Common Issues

- **Camera Not Found**: Verify camera object name matches exactly (case-sensitive)
- **Network Binding Errors**: Check if port is already in use or HOST IP is correct
- **Performance Issues**: Reduce reporting rate or improve network connection
- **Data Loss**: Increase buffer size or improve network stability
- **Connection Failed**: Verify both devices are on the same network

### Logging

Monitor the console output for detailed information about:
- Connection status and network binding
- Data reception and parsing
- Camera updates and rotation values
- Error conditions and troubleshooting info

## Notes

- This free version processes rotation data only
- Performance depends on device capabilities and network conditions
- Requires stable local network connection
- The script uses a large 4096-byte buffer to prevent data cutting issues

