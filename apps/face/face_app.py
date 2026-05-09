from core.auth.face_auth import scan_face
import sys
import time

# ================= MODE DETECTION =================
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


print("\n=== SCAN FACE ===")

# ================= SINGLE FACE SESSION =================
result = scan_face()

# ================= SUCCESS =================
if result:

    print(f"? Akses: {result}")

    # standalone mode buka pintu langsung
    if open_door:
        open_door()

    sys.exit(0)

# ================= FAILED =================
else:

    print("? Akses ditolak")

    time.sleep(1)

    sys.exit(1)
