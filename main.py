
import cv2
import numpy as np
import requests
import os
import time

from datetime import datetime
from dotenv import load_dotenv

# Load application configuration
load_dotenv()

CAMERA_URL = os.getenv("CAMERA_URL")
CAMERA_NAME = os.getenv("CAMERA_NAME", "Android IP Webcam")

DISPLAY_WIDTH = int(os.getenv("DISPLAY_WIDTH", "960"))
RECORDING_FPS = float(os.getenv("RECORDING_FPS", "20"))

RECONNECT_ATTEMPTS = int(os.getenv("RECONNECT_ATTEMPTS", "5"))
RECONNECT_DELAY = float(os.getenv("RECONNECT_DELAY", "2"))
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10"))

WINDOW_NAME = "IP Camera Streaming System"
SCREENSHOT_FOLDER = "screenshots"
RECORDING_FOLDER = "recordings"


def add_overlays(frame, fps, is_recording):
    """Add camera information to each frame."""

    height, width = frame.shape[:2]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cv2.putText(frame, f"Camera: {CAMERA_NAME}",
                (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 255, 0), 2)

    cv2.putText(frame, timestamp,
                (20, 60), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2)

    cv2.putText(frame, f"Resolution: {width} x {height}",
                (20, 90), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 2)

    cv2.putText(frame, f"FPS: {fps:.2f}",
                (20, 120), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 255, 255), 2)

    if is_recording:
        cv2.circle(frame, (30, 155), 8, (0, 0, 255), -1)
        cv2.putText(frame, "RECORDING",
                    (50, 162), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2)

    return frame


def save_screenshot(frame):
    """Save a screenshot."""

    os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(
        SCREENSHOT_FOLDER,
        f"camera_{timestamp}.jpg"
    )

    if cv2.imwrite(filepath, frame):
        print("Screenshot saved:", filepath)
    else:
        print("ERROR: Screenshot could not be saved.")


def start_recording(frame):
    """Initialize AVI recording using MJPG."""

    os.makedirs(RECORDING_FOLDER, exist_ok=True)

    height, width = frame.shape[:2]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(
        RECORDING_FOLDER,
        f"recording_{timestamp}.avi"
    )

    fourcc = cv2.VideoWriter_fourcc(*"MJPG")

    writer = cv2.VideoWriter(
        filepath,
        fourcc,
        RECORDING_FPS,
        (width, height)
    )

    if not writer.isOpened():
        writer.release()
        print("ERROR: Could not start video recording.")
        return None

    print("Recording started:", filepath)
    return writer


def connect_camera():
    """Connect to the Android camera."""

    response = requests.get(
        CAMERA_URL,
        stream=True,
        timeout=(HTTP_TIMEOUT, 30)
    )

    response.raise_for_status()

    return response


def process_stream(response, writer, is_recording):
    """Receive, decode and display camera frames."""

    buffer = bytearray()

    frame_count = 0
    fps = 0.0
    start_time = time.time()

    for chunk in response.iter_content(chunk_size=4096):

        if not chunk:
            continue

        buffer.extend(chunk)

        while True:

            start = buffer.find(b"\xff\xd8")

            if start == -1:
                if len(buffer) > 1:
                    del buffer[:-1]
                break

            if start > 0:
                del buffer[:start]

            end = buffer.find(b"\xff\xd9", 2)

            if end == -1:
                break

            jpg_data = bytes(buffer[:end + 2])
            del buffer[:end + 2]

            frame = cv2.imdecode(
                np.frombuffer(jpg_data, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )

            if frame is None:
                continue

            height, width = frame.shape[:2]

            new_height = int(height * DISPLAY_WIDTH / width)

            frame = cv2.resize(
                frame,
                (DISPLAY_WIDTH, new_height)
            )

            frame_count += 1
            elapsed = time.time() - start_time

            if elapsed >= 1:
                fps = frame_count / elapsed
                frame_count = 0
                start_time = time.time()

            frame = add_overlays(frame, fps, is_recording)

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("s"):
                save_screenshot(frame)

            elif key == ord("r"):
                return "toggle_recording", frame

            elif key == ord("q") or key == 27:
                return "quit", frame

    return "disconnected", None


def main():

    print("Starting IP Camera Streaming System...")

    writer = None
    is_recording = False
    running = True

    reconnect_count = 0

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    try:

        while running:

            response = None

            try:
                print("Connecting to camera...")

                response = connect_camera()

                print("Camera connected successfully!")

                reconnect_count = 0

                while running:

                    action, frame = process_stream(
                        response,
                        writer,
                        is_recording
                    )

                    if action == "quit":
                        running = False

                    elif action == "toggle_recording":

                        if not is_recording:
                            writer = start_recording(frame)

                            if writer is not None:
                                is_recording = True

                        else:
                            writer.release()
                            writer = None
                            is_recording = False
                            print("Recording stopped and saved.")

                    elif action == "disconnected":
                        raise ConnectionError(
                            "Camera stream disconnected."
                        )

            except (
                requests.exceptions.RequestException,
                ConnectionError,
                OSError
            ) as error:

                print("Camera error:", error)

                if not running:
                    break

                reconnect_count += 1

                if reconnect_count > RECONNECT_ATTEMPTS:
                    print("Maximum reconnection attempts reached.")
                    break

                print(
                    f"Reconnecting in {RECONNECT_DELAY} seconds... "
                    f"Attempt {reconnect_count}/{RECONNECT_ATTEMPTS}"
                )

                time.sleep(RECONNECT_DELAY)

            finally:

                if response is not None:
                    response.close()

    except KeyboardInterrupt:
        print("Application interrupted by user.")

    finally:

        if writer is not None:
            writer.release()
            print("Recording file finalized.")

        cv2.destroyAllWindows()

        print("Application shut down safely.")


if __name__ == "__main__":
    main()
