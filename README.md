# Cmp4221-Project: Multi-Stream Video Analytics and RTSP Streaming Server

This project is a Python application that performs real-time person detection on video streams and broadcasts the processed or raw video streams via RTSP. The system can be managed through a REST API built with FastAPI.

## Key Features

* **Real-time Person Detection:** Utilizes the YOLOv8 model to detect persons in video streams.
* **Multiple Video Stream Support:** Can process and stream multiple video sources (e.g., video files) simultaneously.
* **RTSP Streaming:** Serves processed (annotated with detections) or raw video streams over the standard RTSP protocol.
* **REST API Control:**
    * Start new video streams.
    * Stop existing video streams.
    * List all active streams.
* **GPU Acceleration:** Uses a CUDA-enabled GPU for model inference performance.
* **Flexible Stream Configuration:** Offers options for different video sources (e.g., `people_1.mp4`, `people_2.mp4`) and stream types ("annotated" or raw).

## Technology Stack

* **Python 3.x**
* **OpenCV (cv2):** For video processing, frame reading, and resizing.
* **Ultralytics YOLOv8:** For object (person) detection.
* **GStreamer:** For creating and managing multimedia pipelines.
* **GstRtspServer:** For building the RTSP server.
* **FastAPI:** For creating and managing the REST API.
* **GLib:** For asynchronous event loops for GStreamer and FastAPI.
* **CUDA (optional, recommended):** For running the YOLOv8 model on a GPU.

## Installation

### Prerequisites

1.  **Python 3.7+**
2.  **GStreamer Libraries:**
    * Ensure GStreamer and relevant plugins (gst-plugins-base, gst-plugins-good, gst-plugins-bad, gst-plugins-ugly, gst-libav, etc.) are installed on your system.
    * For Debian/Ubuntu-based systems:
        ```bash
        sudo apt-get update
        sudo apt-get install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-rtspclientserver gir1.2-gst-rtsp-server-1.0
        ```
3.  **NVIDIA Drivers and CUDA (for GPU usage):**
    * If you intend to run the YOLO model on a GPU, ensure you have compatible NVIDIA drivers, CUDA Toolkit, and cuDNN libraries installed.
4.  **Video Files:** Make sure video files like `people_1.mp4` and `people_2.mp4` are present in the project directory or update the file paths in `multi_stream_rest.py` accordingly.

### Python Dependencies

Create a `requirements.txt` file in the project root with the following content (you can adjust versions based on your environment):

opencv-python
ultralytics
fastapi
uvicorn[standard]
PyGObject


Then, install the dependencies:
   ``bash
pip install -r requirements.txt
YOLOv8 Model Download
The line model = YOLO("yolov8n.pt") in analytics_engine.py will automatically download the yolov8n.pt model on its first run. Ensure you have an active internet connection.

Usage
To start the application, run multi_stream_rest.py using uvicorn:

Bash

uvicorn multi_stream_rest:app --host 0.0.0.0 --port 8000
This command will start the FastAPI application on port 8000 and the RTSP server (as defined in the code, typically) on port 8554.

API Endpoints
You can manage video streams using the following API endpoints (e.g., via a web browser, curl, or Postman):

Start Stream: POST /start_stream/{stream_name}
Example values for stream_name: cam1, cam1_annotated, cam2, cam2_annotated
Example request: curl -X POST http://localhost:8000/start_stream/cam1_annotated
Successful response:
JSON

{
  "status": "started",
  "url": "rtsp://localhost:8554/cam1_annotated"
}
Stop Stream: POST /stop_stream/{stream_name}
Example request: curl -X POST http://localhost:8000/stop_stream/cam1_annotated
Successful response:
JSON

{
  "status": "stopped"
}
List Active Streams: GET /active_streams
Example request: curl http://localhost:8000/active_streams
Successful response:
JSON

{
  "active_streams": ["cam1_annotated", "cam2"]
}
Viewing RTSP Streams
You can view the started RTSP streams using an RTSP-compatible video player like VLC Media Player. Simply enter the rtsp://... URL returned by the API into the player.

Project Structure
.
├── analytics_engine.py   # Person detection and annotation logic using YOLOv8
├── multi_stream_rest.py  # FastAPI application, RTSP server, and stream management
├── people_1.mp4          # Example video file 1 (ensure it's available)
├── people_2.mp4          # Example video file 2 (ensure it's available)
├── requirements.txt      # Python dependencies (to be created)
└── README.md             # This file


