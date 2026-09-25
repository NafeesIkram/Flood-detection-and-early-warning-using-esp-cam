import serial
import time

PORT = "COM"
BAUDRATE = 115200

PHONE_NUMBER = "01735581445"

try:
    gsm = serial.Serial(
        port=PORT,
        baudrate=BAUDRATE,
        timeout=1
    )

    print("SIM900L connected on", PORT)

    # Wait after opening serial port
    time.sleep(2)

    # Clear old data
    gsm.reset_input_buffer()
    gsm.reset_output_buffer()

    # Test AT command
    print("Sending AT...")

    gsm.write(b"AT\r")
    gsm.flush()

    # Give SIM900 time to respond
    time.sleep(2)

    response = gsm.read_all().decode("utf-8", errors="ignore")

    print("SIM900 response:")
    print(repr(response))

    # Don't stop just because response was empty
    # Try the call anyway
    print("Starting call...")

    command = f"ATD{PHONE_NUMBER};\r"

    gsm.write(command.encode())
    gsm.flush()

    time.sleep(3)

    response = gsm.read_all().decode("utf-8", errors="ignore")

    print("Call response:")
    print(repr(response))

    print("Call should now be active.")

    # Keep call active for 20 seconds
    time.sleep(20)

    print("Hanging up...")

    gsm.write(b"ATH\r")
    gsm.flush()

    time.sleep(2)

    response = gsm.read_all().decode("utf-8", errors="ignore")

    print("Hangup response:")
    print(repr(response))

    gsm.close()

except serial.SerialException as e:
    print("Serial error:", e)

except Exception as e:
    print("Error:", e)