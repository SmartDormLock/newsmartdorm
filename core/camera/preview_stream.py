from flask import Flask, Response
import cv2
import time

from core.camera import camera_state

app = Flask(__name__)

camera = None


# ====================================
# START CAMERA
# ====================================

def start_camera():

    global camera

    if camera is None:

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():

            print("? Camera gagal dibuka")

            return

        camera_state.preview_active = True

        camera_state.camera_mode = "PREVIEW"

        print("?? Camera started")

        print(camera_state.camera_mode)


# ====================================
# STOP CAMERA
# ====================================

def stop_camera():

    global camera

    if camera is not None:

        print("?? Releasing camera...")

        camera.release()

        cv2.destroyAllWindows()

        camera = None

        time.sleep(2)

        camera_state.preview_active = False

        camera_state.camera_mode = "IDLE"

        print("?? Camera stopped")

        print(camera_state.camera_mode)


# ====================================
# GENERATE FRAMES
# ====================================

def generate_frames():

    global camera

    while camera is not None:

        # ================= SAFETY CHECK =================

        if camera is None:
            break

        success, frame = camera.read()

        if not success:

            print("? Failed read frame")

            break

        # ================= RESIZE =================

        frame = cv2.resize(
            frame,
            (960, 540)
        )

        # ================= JPEG ENCODE =================

        _, buffer = cv2.imencode(

            '.jpg',

            frame,

            [cv2.IMWRITE_JPEG_QUALITY, 70]
        )

        frame = buffer.tobytes()

        # ================= MJPEG STREAM =================

        yield (

            b'--frame\r\n'

            b'Content-Type: image/jpeg\r\n\r\n'

            + frame +

            b'\r\n'
        )


# ====================================
# VIDEO FEED
# ====================================

@app.route('/video_feed')
def video_feed():

    start_camera()

    return Response(

        generate_frames(),

        mimetype=
            'multipart/x-mixed-replace; boundary=frame'
    )


# ====================================
# STOP CAMERA ROUTE
# ====================================

@app.route('/stop')
def stop():

    stop_camera()

    return "Camera Stopped"


# ====================================
# START SERVER
# ====================================

def start_preview_server():

    app.run(

        host='0.0.0.0',

        port=5000,

        threaded=True,
        
        use_reloader=False
    )


# ====================================
# MAIN
# ====================================

if __name__ == "__main__":

    start_preview_server()
