import time

from core.hardware.rc522_spi_library import (
    RC522SPILibrary,
    StatusCodes
)

class RFIDReader:

    def __init__(self):

        self.reader = RC522SPILibrary()

    def read_uid(self, timeout=5):

        start = time.time()

        while True:

            if time.time() - start > timeout:

                return None

            try:

                status, _ = self.reader.request()

                if status == StatusCodes.OK:

                    status, uid = self.reader.anticoll()

                    if status == StatusCodes.OK:

                        return uid

            except Exception as e:

                print(f"RFID SPI ERROR: {e}")

                return None

            time.sleep(0.05)
