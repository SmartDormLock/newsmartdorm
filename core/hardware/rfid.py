from core.hardware.rc522_spi_library import RC522SPILibrary, StatusCodes

class RFIDReader:
    def __init__(self):
        self.reader = RC522SPILibrary()

    def read_uid(self):
        while True:
            status, _ = self.reader.request()

            if status == StatusCodes.OK:
                status, uid = self.reader.anticoll()

                if status == StatusCodes.OK:
                    return uid
