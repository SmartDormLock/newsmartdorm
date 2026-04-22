import time
import serial
import adafruit_fingerprint
from config.settings import SERIAL_PORT, BAUDRATE

class FingerprintSensor:
    def __init__(self):
        self.uart = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=2)
        time.sleep(2)
        self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.uart)

        if self.finger.verify_password() != adafruit_fingerprint.OK:
            raise RuntimeError("Sensor tidak terdeteksi")
        else:
            print("? Fingerprint sensor siap")

    def read_image(self):
        return self.finger.get_image()

    def convert(self, slot=1):
        return self.finger.image_2_tz(slot)

    def search(self):
        return self.finger.finger_fast_search()

    def create_model(self):
        return self.finger.create_model()

    def store(self, location):
        return self.finger.store_model(location)

    def delete(self, location):
        return self.finger.delete_model(location)

    def empty(self):
        return self.finger.empty_library()

    def get_id(self):
        return self.finger.finger_id

    def get_confidence(self):
        return self.finger.confidence
