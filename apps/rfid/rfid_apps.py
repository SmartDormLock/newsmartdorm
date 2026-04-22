from core.auth.rfid_auth import scan_rfid
from core.hardware.relay import open_door
import sys
import time

MAX_ATTEMPT = 3

print("\n=== SCAN RFID ===")

attempt = 0

while attempt < MAX_ATTEMPT:
    result = scan_rfid()

    if result:
        print(f"?? Akses: {result}")
        
        open_door()  # ?? BUKA PINTU
        
        sys.exit(0)

    else:
        attempt += 1
        print(f"? Kartu tidak dikenal ({attempt}/{MAX_ATTEMPT})")

print("? Akses ditolak (3x gagal)")
time.sleep(2)
sys.exit(1)
