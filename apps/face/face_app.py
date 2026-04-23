from core.auth.face_auth import scan_face
import sys
import time

# ================= MODE DETECTION =================
# default: standalone
USE_RELAY = True

# kalau dipanggil dari unified ? pakai flag --no-relay
if "--no-relay" in sys.argv:
    USE_RELAY = False

# optional relay
open_door = None
if USE_RELAY:
    try:
        from core.hardware.relay import open_door
    except Exception:
        open_door = None

MAX_ATTEMPT = 3

print("\n=== SCAN FACE ===")

attempt = 0

while attempt < MAX_ATTEMPT:
    result = scan_face()

    if result:
        print(f"?? Akses: {result}")

        # hanya standalone yang buka pintu
        if open_door:
            open_door()

        sys.exit(0)
    else:
        attempt += 1
        print(f"? Gagal ({attempt}/{MAX_ATTEMPT})")

print("? Akses ditolak")
time.sleep(2)
sys.exit(1)
