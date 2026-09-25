import serial
import time


# ==========================================
# DEFAULT SIM900L SETTINGS
# ==========================================

GSM_PORT = "COM6"
GSM_BAUDRATE = 115200
GSM_PHONE_NUMBER = "01735581445"


# ==========================================
# READ RESPONSE
# ==========================================

def read_response(gsm, timeout=5):

    start_time = time.time()

    response = ""

    while time.time() - start_time < timeout:

        if gsm.in_waiting:

            data = gsm.read(
                gsm.in_waiting
            ).decode(
                "utf-8",
                errors="ignore"
            )

            response += data

            print(
                "[GSM] Response:",
                repr(data)
            )

            if "OK" in response:

                return response

            if "ERROR" in response:

                return response

        time.sleep(0.1)

    return response


# ==========================================
# GSM CALL FUNCTION
# ==========================================

def make_call(
    phone_number=None,
    port=None,
    baudrate=None
):

    if phone_number is None:
        phone_number = GSM_PHONE_NUMBER

    if port is None:
        port = GSM_PORT

    if baudrate is None:
        baudrate = GSM_BAUDRATE

    gsm = None

    try:

        print("")
        print(
            "======================================"
        )
        print("[GSM] Connecting...")
        print("[GSM] Port:", port)
        print("[GSM] Baudrate:", baudrate)
        print("[GSM] Number:", phone_number)
        print(
            "======================================"
        )

        # ==================================
        # OPEN SERIAL PORT
        # ==================================

        gsm = serial.Serial(

            port=port,

            baudrate=baudrate,

            timeout=0.5,

            write_timeout=2

        )

        time.sleep(2)

        # ==================================
        # CLEAR BUFFERS
        # ==================================

        gsm.reset_input_buffer()

        gsm.reset_output_buffer()

        time.sleep(0.5)


        # ==================================
        # TEST MODULE
        # ==================================

        print("[GSM] Testing module...")

        response = ""

        for attempt in range(3):

            print(
                "[GSM] AT test attempt:",
                attempt + 1
            )

            gsm.reset_input_buffer()

            gsm.write(
                b"AT\r\n"
            )

            gsm.flush()

            response = read_response(
                gsm,
                timeout=3
            )

            if "OK" in response:

                break

            time.sleep(1)


        if "OK" not in response:

            print(
                "[GSM] Module did not respond."
            )

            gsm.close()

            return False


        print("[GSM] Module OK")


        # ==================================
        # MAKE CALL
        # ==================================

        print(
            "[GSM] Calling:",
            phone_number
        )

        command = (
            f"ATD{phone_number};\r\n"
        )

        gsm.reset_input_buffer()

        gsm.write(
            command.encode()
        )

        gsm.flush()

        time.sleep(2)

        response = ""

        start_time = time.time()

        while time.time() - start_time < 5:

            if gsm.in_waiting:

                data = gsm.read(
                    gsm.in_waiting
                ).decode(
                    "utf-8",
                    errors="ignore"
                )

                response += data

                print(
                    "[GSM] Call response:",
                    repr(data)
                )

                if "ERROR" in response:

                    print(
                        "[GSM] Call command failed."
                    )

                    gsm.close()

                    return False

                if "NO CARRIER" in response:

                    print(
                        "[GSM] Call failed."
                    )

                    gsm.close()

                    return False

                if (
                    "OK" in response
                    or
                    "CONNECT" in response
                ):

                    break

            time.sleep(0.1)


        print(
            "[GSM] Call initiated."
        )


        # ==================================
        # MONITOR CALL
        # ==================================

        call_timeout = 30

        start_time = time.time()

        while (
            time.time() - start_time
            < call_timeout
        ):

            if gsm.in_waiting:

                data = gsm.read(
                    gsm.in_waiting
                ).decode(
                    "utf-8",
                    errors="ignore"
                )

                if data:

                    print(
                        "[GSM]",
                        repr(data)
                    )

                    if "NO CARRIER" in data:

                        print(
                            "[GSM] Call ended."
                        )

                        gsm.close()

                        return True

                    if "ERROR" in data:

                        print(
                            "[GSM] GSM error during call."
                        )

                        gsm.close()

                        return False

            time.sleep(0.5)


        # ==================================
        # TIMEOUT → HANG UP
        # ==================================

        print(
            "[GSM] Timeout. Hanging up..."
        )

        gsm.reset_input_buffer()

        gsm.write(
            b"ATH\r\n"
        )

        gsm.flush()

        time.sleep(1)

        response = ""

        if gsm.in_waiting:

            response = gsm.read(
                gsm.in_waiting
            ).decode(
                "utf-8",
                errors="ignore"
            )

        print(
            "[GSM] Hangup:",
            repr(response)
        )

        gsm.close()

        return True


    except serial.SerialException as e:

        print(
            "[GSM] Serial error:",
            e
        )

        if (
            gsm is not None
            and gsm.is_open
        ):

            gsm.close()

        return False


    except Exception as e:

        print(
            "[GSM] Error:",
            e
        )

        if (
            gsm is not None
            and gsm.is_open
        ):

            gsm.close()

        return False