from flask import Flask, render_template, Response, request, jsonify
from detector import FloodDetector

app = Flask(__name__)
detector = FloodDetector()


# ======================================
# Home
# ======================================

@app.route("/")
def home():
    return render_template("index.html")


# ======================================
# Connect Camera
# ======================================

@app.route("/connect", methods=["POST"])
def connect():

    url = request.form.get("url")

    success = detector.connect(url)

    return jsonify({
        "success": success
    })


# ======================================
# Twilio Call
# ======================================

@app.route("/set_twilio", methods=["POST"])
def set_twilio():

    detector.twilio_enabled = (
        request.form.get("enabled") == "true"
    )

    if detector.twilio_enabled:
        detector.gsm_enabled = False

    return jsonify(
        success=True
    )


# ======================================
# GSM Call
# ======================================

@app.route("/set_gsm", methods=["POST"])
def set_gsm():

    detector.gsm_enabled = (
        request.form.get("enabled") == "true"
    )

    if detector.gsm_enabled:
        detector.twilio_enabled = False

    return jsonify(
        success=True
    )


# ======================================
# GSM Settings
# ======================================

@app.route("/set_gsm_settings", methods=["POST"])
def set_gsm_settings():

    phone = request.form.get("phone")
    port = request.form.get("port")
    baudrate = request.form.get("baudrate")

    try:

        if phone:
            detector.gsm_phone_number = phone.strip()

        if port:
            detector.gsm_port = port.strip()

        if baudrate:
            detector.gsm_baudrate = int(
                baudrate.strip()
            )

        # Save permanently
        detector.save_gsm_settings()

        return jsonify({

            "success": True,

            "phone":
                detector.gsm_phone_number,

            "port":
                detector.gsm_port,

            "baudrate":
                detector.gsm_baudrate

        })

    except ValueError:

        return jsonify({

            "success": False,

            "message":
                "Invalid baud rate"

        })


# ======================================
# Video
# ======================================

@app.route("/video")
def video():

    return Response(

        detector.video_stream(),

        mimetype=
        "multipart/x-mixed-replace; boundary=frame"

    )


# ======================================
# Mask
# ======================================

@app.route("/mask")
def mask():

    return Response(

        detector.mask_stream(),

        mimetype=
        "multipart/x-mixed-replace; boundary=frame"

    )


# ======================================
# Black Threshold
# ======================================

@app.route("/set_threshold", methods=["POST"])
def set_threshold():

    detector.black_threshold = int(
        request.form.get("value")
    )

    return jsonify(
        success=True
    )


# ======================================
# Contour Area
# ======================================

@app.route("/set_area", methods=["POST"])
def set_area():

    detector.min_area = int(
        request.form.get("value")
    )

    return jsonify(
        success=True
    )


# ======================================
# Critical Level
# ======================================

@app.route("/set_critical", methods=["POST"])
def set_critical():

    detector.critical_level = int(
        request.form.get("value")
    )

    return jsonify(
        success=True
    )


# ======================================
# Status
# ======================================

@app.route("/status")
def status():

    return jsonify({

        "percentage":
            detector.percentage,

        "risk":
            detector.status,

        "connected":
            detector.connected,

        "twilio":
            detector.twilio_enabled,

        "gsm":
            detector.gsm_enabled,

        "threshold":
            detector.black_threshold,

        "area":
            detector.min_area,

        "critical":
            detector.critical_level,

        "gsm_phone":
            detector.gsm_phone_number,

        "gsm_port":
            detector.gsm_port,

        "gsm_baudrate":
            detector.gsm_baudrate

    })


# ======================================
# Run
# ======================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False,
        threaded=True


    )