import cv2
import numpy as np
import call
import threading
import json
import os
import time
import urllib.request


class FloodDetector:

    def __init__(self):

        # =====================================
        # Camera
        # =====================================

        self.connected = False

        self.stream_url = None

        self.capture_thread = None

        self.stop_capture = threading.Event()

        self.frame_lock = threading.Lock()

        self.stream_response = None


        # =====================================
        # Latest Frames
        # =====================================

        self.latest_frame = None

        self.latest_mask = None


        # =====================================
        # Detection Values
        # =====================================

        self.display_flood = 0

        self.percentage = 0

        self.status = "Disconnected"

        self.color = (255, 255, 255)


        # =====================================
        # Detection Settings
        # =====================================

        self.black_threshold = 60

        self.min_area = 1500

        self.critical_level = 95


        # =====================================
        # Call Options
        # =====================================

        self.twilio_enabled = False

        self.gsm_enabled = False


        # =====================================
        # GSM Settings
        # =====================================

        self.gsm_phone_number = "YOUR_PHONE_NUMBER"

        self.gsm_port = "COM6"

        self.gsm_baudrate = 115200

        self.gsm_settings_file = "gsm_settings.json"

        self.load_gsm_settings()


        # =====================================
        # Call Status
        # =====================================

        self.call_sent = False

        self.call_in_progress = False


    # =====================================
    # Load GSM Settings
    # =====================================

    def load_gsm_settings(self):

        try:

            if os.path.exists(
                self.gsm_settings_file
            ):

                with open(
                    self.gsm_settings_file,
                    "r"
                ) as file:

                    settings = json.load(file)


                self.gsm_phone_number = settings.get(
                    "phone",
                    self.gsm_phone_number
                )


                self.gsm_port = settings.get(
                    "port",
                    self.gsm_port
                )


                self.gsm_baudrate = int(
                    settings.get(
                        "baudrate",
                        self.gsm_baudrate
                    )
                )


                print(
                    "[GSM] Saved settings loaded."
                )

                print(
                    "[GSM] Phone:",
                    self.gsm_phone_number
                )

                print(
                    "[GSM] Port:",
                    self.gsm_port
                )

                print(
                    "[GSM] Baudrate:",
                    self.gsm_baudrate
                )


        except Exception as e:

            print(
                "[GSM] Could not load saved settings:",
                e
            )


    # =====================================
    # Save GSM Settings
    # =====================================

    def save_gsm_settings(self):

        settings = {

            "phone":
                self.gsm_phone_number,

            "port":
                self.gsm_port,

            "baudrate":
                self.gsm_baudrate

        }


        try:

            with open(
                self.gsm_settings_file,
                "w"
            ) as file:

                json.dump(
                    settings,
                    file,
                    indent=4
                )


            print(
                "[GSM] Settings saved."
            )

            return True


        except Exception as e:

            print(
                "[GSM] Could not save settings:",
                e
            )

            return False


    # =====================================
    # Connect ESP32 Camera
    # =====================================

    def connect(self, stream_url):

        # ---------------------------------
        # Stop previous stream
        # ---------------------------------

        self.stop_capture.set()


        # ---------------------------------
        # Close previous HTTP connection
        # ---------------------------------

        try:

            if self.stream_response is not None:

                self.stream_response.close()

        except Exception:

            pass


        self.stream_response = None


        # ---------------------------------
        # Reset
        # ---------------------------------

        self.connected = False

        self.stream_url = stream_url

        self.stop_capture.clear()


        # ---------------------------------
        # Test camera connection
        # ---------------------------------

        try:

            test_request = urllib.request.Request(

                stream_url,

                headers={
                    "User-Agent":
                        "FloodMonitoring/1.0"
                }

            )


            test_response = urllib.request.urlopen(

                test_request,

                timeout=5

            )


            test_response.close()


        except Exception as e:

            print(
                "[CAMERA] Cannot connect:",
                e
            )

            self.connected = False

            return False


        # ---------------------------------
        # Start ONE capture thread
        # ---------------------------------

        self.capture_thread = threading.Thread(

            target=self._capture_loop,

            daemon=True

        )


        self.capture_thread.start()


        print(
            "[CAMERA] Camera connected."
        )

        print(
            "[CAMERA] HTTP capture thread started."
        )


        return True


    # =====================================
    # Open Camera HTTP Stream
    # =====================================

    def _open_stream(self):

        try:

            request = urllib.request.Request(

                self.stream_url,

                headers={
                    "User-Agent":
                        "FloodMonitoring/1.0",
                    "Connection":
                        "keep-alive"
                }

            )


            response = urllib.request.urlopen(

                request,

                timeout=10

            )


            self.stream_response = response

            self.connected = True


            print(
                "[CAMERA] HTTP stream opened."
            )


            return response


        except Exception as e:

            print(
                "[CAMERA] Stream open error:",
                e
            )

            self.stream_response = None

            self.connected = False

            return None


    # =====================================
    # Read JPEG Frame
    # =====================================

    def _read_jpeg_frame(self, response):

        buffer = bytearray()

        chunk_size = 4096

        while not self.stop_capture.is_set():

            try:

                chunk = response.read(
                    chunk_size
                )

            except Exception as e:

                print(
                    "[CAMERA] Stream read error:",
                    e
                )

                return None


            if not chunk:

                print(
                    "[CAMERA] Stream ended."
                )

                return None


            buffer.extend(chunk)


            # ---------------------------------
            # Find JPEG start
            # ---------------------------------

            start = buffer.find(
                b"\xff\xd8"
            )


            if start == -1:

                # Prevent unlimited buffer growth

                if len(buffer) > 1024 * 1024:

                    buffer.clear()

                continue


            # Remove everything before JPEG

            if start > 0:

                del buffer[:start]


            # ---------------------------------
            # Find JPEG end
            # ---------------------------------

            end = buffer.find(

                b"\xff\xd9",

                2

            )


            if end == -1:

                # Wait for rest of JPEG

                if len(buffer) > 5 * 1024 * 1024:

                    print(
                        "[CAMERA] Invalid JPEG frame. Resetting buffer."
                    )

                    buffer.clear()

                continue


            # ---------------------------------
            # Extract JPEG
            # ---------------------------------

            jpeg_data = bytes(

                buffer[:end + 2]

            )


            # Remove processed frame

            del buffer[:end + 2]


            return jpeg_data


        return None


    # =====================================
    # Camera Capture Loop
    # =====================================

    def _capture_loop(self):

        while not self.stop_capture.is_set():

            response = None


            # =================================
            # Open stream
            # =================================

            response = self._open_stream()


            if response is None:

                if self.stop_capture.is_set():

                    break


                print(
                    "[CAMERA] Reconnecting in 2 seconds..."
                )

                time.sleep(2)

                continue


            # =================================
            # Read stream
            # =================================

            while not self.stop_capture.is_set():

                jpeg_data = (
                    self._read_jpeg_frame(
                        response
                    )
                )


                if jpeg_data is None:

                    break


                # =================================
                # Decode JPEG
                # =================================

                try:

                    frame_array = np.frombuffer(

                        jpeg_data,

                        dtype=np.uint8

                    )


                    frame = cv2.imdecode(

                        frame_array,

                        cv2.IMREAD_COLOR

                    )


                except Exception as e:

                    print(
                        "[CAMERA] JPEG decode error:",
                        e
                    )

                    continue


                if frame is None:

                    print(
                        "[CAMERA] Invalid JPEG frame."
                    )

                    continue


                # =================================
                # Run existing detection
                # =================================

                try:

                    self.process_frame_data(
                        frame
                    )

                except Exception as e:

                    print(
                        "[CAMERA] Detection error:",
                        e
                    )

                    continue


            # =================================
            # Close broken stream
            # =================================

            try:

                response.close()

            except Exception:

                pass


            self.stream_response = None

            self.connected = False


            # =================================
            # Reconnect
            # =================================

            if not self.stop_capture.is_set():

                print(
                    "[CAMERA] Stream lost."
                )

                print(
                    "[CAMERA] Reconnecting..."
                )

                time.sleep(2)


        self.connected = False


        try:

            if self.stream_response is not None:

                self.stream_response.close()

        except Exception:

            pass


        self.stream_response = None


        print(
            "[CAMERA] Capture thread stopped."
        )


    # =====================================
    # Risk Level
    # =====================================

    def calculate_risk(self):

        if self.display_flood < 20:

            self.status = "SAFE"

            self.color = (
                0,
                255,
                0
            )


        elif self.display_flood < 40:

            self.status = "LOW"

            self.color = (
                0,
                255,
                255
            )


        elif self.display_flood < 60:

            self.status = "MEDIUM"

            self.color = (
                0,
                165,
                255
            )


        elif self.display_flood < 80:

            self.status = "HIGH"

            self.color = (
                0,
                0,
                255
            )


        else:

            self.status = "CRITICAL"

            self.color = (
                0,
                0,
                180
            )


    # =====================================
    # Background Twilio Call
    # =====================================

    def _make_twilio_call(self):

        try:

            print("")

            print(
                "======================================"
            )

            print(
                "[CALL] TWILIO THREAD STARTED"
            )

            print(
                "======================================"
            )


            call.make_call()


            print(
                "[CALL] Twilio call finished."
            )


        except Exception as e:

            print(
                "[CALL] Twilio error:",
                e
            )

            self.call_sent = False


        finally:

            self.call_in_progress = False


    # =====================================
    # Background GSM Call
    # =====================================

    def _make_gsm_call(self):

        try:

            print("")

            print(
                "======================================"
            )

            print(
                "[GSM] GSM THREAD STARTED"
            )

            print(
                "======================================"
            )


            print(
                "[GSM] Phone:",
                self.gsm_phone_number
            )


            print(
                "[GSM] Port:",
                self.gsm_port
            )


            print(
                "[GSM] Baudrate:",
                self.gsm_baudrate
            )


            import gsm_call


            result = gsm_call.make_call(

                phone_number=
                    self.gsm_phone_number,

                port=
                    self.gsm_port,

                baudrate=
                    self.gsm_baudrate

            )


            if result:

                print(
                    "[GSM] CALL SUCCESS"
                )


            else:

                print(
                    "[GSM] CALL FAILED"
                )

                self.call_sent = False


        except Exception as e:

            print(
                "[GSM] GSM THREAD ERROR:",
                e
            )

            self.call_sent = False


        finally:

            self.call_in_progress = False


    # =====================================
    # Process Frame Data
    # =====================================

    def process_frame_data(self, frame):

        # ======================================
        # FULL CAMERA VIEW
        # ======================================

        roi = frame


        # ======================================
        # HSV
        # ======================================

        hsv = cv2.cvtColor(

            roi,

            cv2.COLOR_BGR2HSV

        )


        # ======================================
        # Detect ONLY BLACK
        # ======================================

        lower_black = np.array([

            0,

            0,

            0

        ])


        upper_black = np.array([

            180,

            255,

            self.black_threshold

        ])


        mask = cv2.inRange(

            hsv,

            lower_black,

            upper_black

        )


        # ======================================
        # Remove Noise
        # ======================================

        kernel = np.ones(

            (5, 5),

            np.uint8

        )


        mask = cv2.morphologyEx(

            mask,

            cv2.MORPH_OPEN,

            kernel

        )


        mask = cv2.morphologyEx(

            mask,

            cv2.MORPH_CLOSE,

            kernel

        )


        # ======================================
        # Ignore Small Objects
        # ======================================

        contours, _ = cv2.findContours(

            mask,

            cv2.RETR_EXTERNAL,

            cv2.CHAIN_APPROX_SIMPLE

        )


        clean = np.zeros_like(mask)


        for cnt in contours:

            area = cv2.contourArea(cnt)


            if area > self.min_area:

                cv2.drawContours(

                    clean,

                    [cnt],

                    -1,

                    255,

                    -1

                )


        mask = clean


        # ======================================
        # Percentage
        # ======================================

        black_pixels = cv2.countNonZero(

            mask

        )


        total_pixels = (

            mask.shape[0] *

            mask.shape[1]

        )


        flood = (

            black_pixels /

            total_pixels

        ) * 100


        # ======================================
        # Smooth Value
        # ======================================

        self.display_flood = (

            self.display_flood * 0.90 +

            flood * 0.10

        )


        if self.display_flood > 99:

            self.display_flood = 100


        self.percentage = round(

            self.display_flood,

            1

        )


        # ======================================
        # Risk
        # ======================================

        self.calculate_risk()


        # ======================================
        # Emergency Call
        # ======================================

        if self.display_flood >= self.critical_level:

            if (

                not self.call_sent

                and

                not self.call_in_progress

            ):

                print("")

                print(
                    "======================================"
                )

                print(
                    "[EMERGENCY] CRITICAL LEVEL REACHED"
                )


                print(
                    "[EMERGENCY] Flood:",
                    self.display_flood
                )


                print(
                    "[EMERGENCY] Critical:",
                    self.critical_level
                )


                print(
                    "[EMERGENCY] Twilio:",
                    self.twilio_enabled
                )


                print(
                    "[EMERGENCY] GSM:",
                    self.gsm_enabled
                )


                print(
                    "======================================"
                )


                # ==================================
                # Twilio
                # ==================================

                if self.twilio_enabled:

                    print(
                        "[EMERGENCY] Starting Twilio thread..."
                    )


                    self.call_sent = True

                    self.call_in_progress = True


                    threading.Thread(

                        target=
                            self._make_twilio_call,

                        daemon=True

                    ).start()


                # ==================================
                # GSM
                # ==================================

                elif self.gsm_enabled:

                    print(
                        "[EMERGENCY] Starting GSM thread..."
                    )


                    self.call_sent = True

                    self.call_in_progress = True


                    threading.Thread(

                        target=
                            self._make_gsm_call,

                        daemon=True

                    ).start()


                # ==================================
                # No Call Method
                # ==================================

                else:

                    print(
                        "[EMERGENCY] No call method enabled."
                    )


                    self.call_sent = False

                    self.call_in_progress = False


        else:

            self.call_sent = False


        # ======================================
        # Show Text
        # ======================================

        cv2.putText(

            frame,

            f"Flood: {self.display_flood:.1f}%",

            (20, 50),

            cv2.FONT_HERSHEY_SIMPLEX,

            1.2,

            (0, 0, 255),

            3

        )


        cv2.putText(

            frame,

            self.status,

            (20, 100),

            cv2.FONT_HERSHEY_SIMPLEX,

            1.2,

            self.color,

            3

        )


        # ======================================
        # Prepare Mask
        # ======================================

        latest_mask = cv2.cvtColor(

            mask,

            cv2.COLOR_GRAY2BGR

        )


        # ======================================
        # Thread-Safe Frame Update
        # ======================================

        with self.frame_lock:

            self.latest_frame = (
                frame.copy()
            )

            self.latest_mask = (
                latest_mask.copy()
            )


        return True


    # =====================================
    # Compatibility Function
    # =====================================

    def process_frame(self):

        # This function is kept for compatibility.

        # Actual streaming now uses
        # process_frame_data() from the
        # single camera capture thread.

        return False


    # =====================================
    # Processed Video Stream
    # =====================================

    def video_stream(self):

        while True:

            with self.frame_lock:

                if self.latest_frame is not None:

                    frame = (
                        self.latest_frame.copy()
                    )

                else:

                    frame = None


            if frame is None:

                time.sleep(0.05)

                continue


            ret, buffer = cv2.imencode(

                ".jpg",

                frame

            )


            if not ret:

                time.sleep(0.05)

                continue


            frame_bytes = buffer.tobytes()


            yield (

                b'--frame\r\n'

                b'Content-Type: image/jpeg\r\n\r\n' +

                frame_bytes +

                b'\r\n'

            )


            time.sleep(0.03)


    # =====================================
    # Black Mask Stream
    # =====================================

    def mask_stream(self):

        while True:

            with self.frame_lock:

                if self.latest_mask is not None:

                    frame = (
                        self.latest_mask.copy()
                    )

                else:

                    frame = None


            if frame is None:

                time.sleep(0.05)

                continue


            ret, buffer = cv2.imencode(

                ".jpg",

                frame

            )


            if not ret:

                time.sleep(0.05)

                continue


            frame_bytes = buffer.tobytes()


            yield (

                b'--frame\r\n'

                b'Content-Type: image/jpeg\r\n\r\n' +

                frame_bytes +

                b'\r\n'

            )


            time.sleep(0.03)