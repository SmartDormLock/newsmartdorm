import subprocess
import time

from core.auth.fingerprint_auth import scan_fingerprint
from core.auth.rfid_auth import scan_rfid
from core.hardware.relay import open_door


MAX_ATTEMPT = 3

# ?? path python face_env (WAJIB SESUAIIN KALO PATH BEDA)
FACE_PY = "/home/raspi5/newsmartdorm/envs/face_env/bin/python"


# ================= FACE VIA SUBPROCESS =================
def scan_face_external():
    print("\n?? Menjalankan Face Recognition...")

    try:
        result = subprocess.run(
            [FACE_PY, "-m", "apps.face.face_app", "--no-relay"],  # ?? penting
            capture_output=True,
            text=True
        )

        output = (result.stdout or "") + "\n" + (result.stderr or "")
        output = output.strip()

        print("----- FACE OUTPUT -----")
        print(output)
        print("-----------------------")

        # ?? parsing hasil
        for line in output.splitlines():
            if "Akses:" in line:
                name = line.split("Akses:")[-1].strip()
                return name

        # kalau process error
        if result.returncode != 0:
            print("? Face process failed")

    except Exception as e:
        print("? Face error:", e)

    return None


# ================= RFID VERIFY =================
def rfid_verify():
    print("\n?? Verifikasi RFID...")

    for attempt in range(MAX_ATTEMPT):
        result = scan_rfid()

        if result:
            print(f"? RFID valid: {result}")
            return True
        else:
            print(f"? RFID gagal ({attempt+1}/{MAX_ATTEMPT})")

    return False


# ================= MODE 1: FACE =================
def mode_face():
    print("\n=== MODE 1: FACE + RFID ===")

    for attempt in range(MAX_ATTEMPT):
        result = scan_face_external()

        if result:
            print(f"?? Face dikenali: {result}")

            if rfid_verify():
                open_door()
                return True
            else:
                print("? RFID gagal setelah face")
                return False

        else:
            print(f"? Face gagal ({attempt+1}/{MAX_ATTEMPT})")

    return False


# ================= MODE 2: FINGERPRINT =================
def mode_fingerprint():
    print("\n=== MODE 2: FINGERPRINT + RFID ===")

    for attempt in range(MAX_ATTEMPT):
        result = scan_fingerprint()

        if result:
            print(f"?? Fingerprint dikenali: {result}")

            if rfid_verify():
                open_door()
                return True
            else:
                print("? RFID gagal setelah fingerprint")
                return False

        else:
            print(f"? Fingerprint gagal ({attempt+1}/{MAX_ATTEMPT})")

    return False


# ================= MAIN =================
def main():
    print("\n?? SMART DOOR SYSTEM STARTED")

    # MODE 1: FACE
    if mode_face():
        return

    print("\n?? Pindah ke mode fingerprint...")

    # MODE 2: FINGERPRINT
    if mode_fingerprint():
        return

    print("\n? AKSES DITOLAK TOTAL")


# ================= ENTRY =================
if __name__ == "__main__":
    main()
