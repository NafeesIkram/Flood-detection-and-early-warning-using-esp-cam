import os
from twilio.rest import Client

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")


def make_call():
    if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER, TO_NUMBER]):
        raise RuntimeError(
            "Missing Twilio environment variables. "
            "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
            "TWILIO_FROM_NUMBER and TWILIO_TO_NUMBER."
        )

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    call = client.calls.create(
        to=TO_NUMBER,
        from_=FROM_NUMBER,
        twiml="""
<Response>
    <Say voice="alice">
        Warning. Critical Flood Level Detected.
        Please take immediate action.
    </Say>
</Response>
"""
    )

    print(call.sid)


if __name__ == "__main__":
    make_call()
