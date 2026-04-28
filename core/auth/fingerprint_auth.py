import time
import adafruit_fingerprint
from core.hardware.fingerprint import FingerprintSensor

DATA_FILE = "data/fingerprint/users.txt"

sensor = None


def init():
    global sensor
    if sensor is None:
        sensor = FingerprintSensor()


def load_users():
    users = {}
    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                id, name = line.strip().split(",")
                users[int(id)] = name
    except:
        pass
    return users


def wait_finger():
    while True:
        i = sensor.read_image()

        if i == adafruit_fingerprint.OK:
            return True
        elif i == adafruit_fingerprint.NOFINGER:
            time.sleep(0.1)
        else:
            return False


def scan_fingerprint():
    init()
    users = load_users()

    print("?? Tempelkan jari...")

    if not wait_finger():
        return None

    if sensor.convert(1) != adafruit_fingerprint.OK:
        return None

    if sensor.search() != adafruit_fingerprint.OK:
        print("? Tidak dikenali")
        return None

    fid = sensor.get_id()
    confidence = sensor.get_confidence()

    print(f"ID: {fid} | Confidence: {confidence}")

    if fid in users:
        return {
            "name": users[fid],
            "fid": fid
        }
        
    return f"ID_{fid}"
