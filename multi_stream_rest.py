import gi
import cv2
import time
import threading
from fastapi import FastAPI
from cmp4221.analytics_engine import process_frame
from gi.repository import Gst, GstRtspServer, GLib
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')

Gst.init(None)

app = FastAPI()
loop = GLib.MainLoop()
stream_threads = {}
stream_factories = {}
stream_caps = {}
mounts = None

class FrameStreamer(GstRtspServer.RTSPMediaFactory):
    def __init__(self, get_frame_func):
        super(FrameStreamer, self).__init__()
        self.get_frame = get_frame_func
        self.number_frames = 0
        self.duration = 1 / 30 * Gst.SECOND  # 30 fps
        self.launch_string = (
            "appsrc name=source is-live=true block=true format=TIME "
            "caps=video/x-raw,format=BGR,width=640,height=360,framerate=30/1 "
            "! videoconvert ! video/x-raw,format=I420 "
            "! x264enc tune=zerolatency speed-preset=superfast bitrate=512 "
            "! rtph264pay config-interval=1 name=pay0 pt=96"
        )

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        appsrc = rtsp_media.get_element().get_child_by_name("source")
        appsrc.connect("need-data", self.on_need_data)

    def on_need_data(self, src, length):
        frame = self.get_frame()
        if frame is None:
            return
        data = frame.tobytes()
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        buf.duration = self.duration
        buf.pts = buf.dts = int(self.number_frames * self.duration)
        self.number_frames += 1
        retval = src.emit("push-buffer", buf)
        if retval != Gst.FlowReturn.OK:
            print("Push buffer error:", retval)


def make_frame_generator(name):
    if "cam1" in name:
        video = "people_1.mp4"
    elif "cam2" in name:
        video = "people_2.mp4"
    else:
        raise ValueError(f"Unknown stream name: {name}")

    cap = cv2.VideoCapture(video)

    def get_frame():
        nonlocal cap
        if not cap.isOpened():
            cap.open(video)

        ret, frame = cap.read()

        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()

        if frame is None:
            return None

        frame = cv2.resize(frame, (640, 360))

        if "annotated" in name:
            return process_frame(frame)

        return frame

    return get_frame


@app.on_event("startup")
def start_rtsp_server():
    global mounts
    server = GstRtspServer.RTSPServer()
    mounts = server.get_mount_points()
    server.attach(None)
    print("RTSP Server started on port 8554")

    t = threading.Thread(target=loop.run)
    t.daemon = True
    t.start()


@app.post("/start_stream/{stream_name}")
def start_stream(stream_name: str):
    if stream_name in stream_factories:
        return {"status": "already running"}

    frame_func = make_frame_generator(stream_name)
    factory = FrameStreamer(frame_func)
    factory.set_shared(True)
    stream_factories[stream_name] = factory

    mount_path = f"/{stream_name}"
    GLib.idle_add(mounts.add_factory, mount_path, factory)

    return {"status": "started", "url": f"rtsp://localhost:8554{mount_path}"}


@app.post("/stop_stream/{stream_name}")
def stop_stream(stream_name: str):
    if stream_name not in stream_factories:
        return {"status": "not found"}

    mount_path = f"/{stream_name}"
    GLib.idle_add(mounts.remove_factory, mount_path)

    # Clean up
    del stream_factories[stream_name]
    return {"status": "stopped"}


@app.get("/active_streams")
def list_streams():
    return {"active_streams": list(stream_factories.keys())}