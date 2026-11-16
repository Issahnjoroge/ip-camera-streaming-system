# Real-Time IP Camera Video Streaming System Using Python and OpenCV

## 1. Project Overview

This project implements a real-time IP camera video streaming application using Python and OpenCV. It connects to an authorized IP camera, displays live video, processes each frame, and provides screenshot and video recording functionality.

The application also includes camera disconnection detection, automatic reconnection attempts, and safe shutdown.

## 2. Features

- Real-time video streaming from an IP camera.
- Frame resizing for display.
- Camera name overlay.
- Current date and time overlay.
- Video resolution display.
- Estimated frames-per-second (FPS) display.
- Screenshot capture.
- Video recording in AVI format using the MJPG codec.
- Recording status indicator.
- Camera disconnection detection and automatic reconnection.
- Resource cleanup during application shutdown.

## 3. Technologies Used

- Python 3.12
- OpenCV
- NumPy
- Requests
- python-dotenv
- Android IP Webcam application

## 4. Project Structure

```text
IP_Camera_Project/
├── main.py
├── requirements.txt
├── .env
├── .gitignore
├── screenshots/
├── recordings/
└── README.md
```

The `.venv/` virtual environment is also used locally but is excluded from version control.

## 5. Installation

### Prerequisites

- Python 3.10 or later.
- An IP camera or Android phone running an IP camera application.
- Computer and camera connected to the same network.
- Git (optional, for version control).

### Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd IP_Camera_Project
```

### Create a virtual environment

```bash
python3 -m venv .venv
```

### Activate the virtual environment

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Camera Configuration

1. Open the IP Webcam application on the Android phone.
2. Start the camera server.
3. Identify the camera's video streaming URL.
4. Create a `.env` file in the project directory.
5. Configure the application using the following example:

```text
CAMERA_URL=http://YOUR_CAMERA_IP:8080/video
CAMERA_NAME=Android IP Webcam
DISPLAY_WIDTH=960
RECORDING_FPS=20
RECONNECT_ATTEMPTS=5
RECONNECT_DELAY=2
HTTP_TIMEOUT=10
```

Replace `YOUR_CAMERA_IP` with the address displayed by your camera application.

**Security:** Do not commit your `.env` file or publish your private camera URL.

## 7. Running the Application

Activate the virtual environment and execute:

```bash
python main.py
```

The application should connect to the camera and display the live video stream.

## 8. Keyboard Controls

| Key | Function |
|---|---|
| S | Capture a screenshot |
| R | Start or stop video recording |
| Q | Quit the application |

Screenshots are saved in the `screenshots/` directory, while video recordings are saved in the `recordings/` directory.

## 9. Error Handling

The application includes mechanisms to:

- Detect unsuccessful camera connections.
- Detect camera stream disconnections.
- Attempt automatic reconnection.
- Display connection and error messages.
- Finalize video recordings during shutdown.
- Release resources and close application windows safely.

## 10. Testing

The application was tested using an Android IP Webcam camera source connected over the same Wi-Fi network.

Testing included:

- Establishing a camera connection.
- Displaying live video.
- Checking video overlays.
- Capturing screenshots.
- Starting and stopping video recordings.
- Playing back saved AVI recordings.
- Disconnecting and restoring the camera connection.
- Checking application shutdown behavior.

## 11. Limitations

- Video performance depends on network quality and camera settings.
- Streaming delays may occur depending on Wi-Fi conditions.
- Recording uses AVI format with the MJPG codec for compatibility with the tested environment.
- Camera availability depends on the phone's IP camera server being active.

