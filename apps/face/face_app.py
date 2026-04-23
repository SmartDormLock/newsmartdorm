from core.auth.face_auth import scan_face
import sys
import time

MAX_ATTEMPT = 3

print("\n=== SCAN FACE ===")

attempt = 0

while attempt < MAX_ATTEMPT:
    result = scan_face()

    if result:
        print(f"?? Akses: {result}")
        sys.exit(0)

    else:
        attempt += 1
        print(f"? Gagal ({attempt}/{MAX_ATTEMPT})")

print("? Akses ditolak")
time.sleep(2)
sys.exit(1)
