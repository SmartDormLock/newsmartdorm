import time
import adafruit_fingerprint
from core.hardware.fingerprint import FingerprintSensor
from core.auth.rfid_auth import enroll_rfid, delete_rfid, list_rfid

DATA_FILE = "data/fingerprint/users.txt"

sensor = None


# ================= INIT =================
def init_sensor():
    global sensor
    if sensor is None:
        sensor = FingerprintSensor()


# ================= FILE =================
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


def save_users(users):
    with open(DATA_FILE, "w") as f:
        for id, name in users.items():
            f.write(f"{id},{name}\n")


# ================= WAIT =================
def wait_finger():
    while True:
        i = sensor.read_image()

        if i == adafruit_fingerprint.OK:
            return True
        elif i == adafruit_fingerprint.NOFINGER:
            time.sleep(0.1)
        else:
            return False


def wait_release():
    while sensor.read_image() != adafruit_fingerprint.NOFINGER:
        time.sleep(0.1)
    time.sleep(1)


# ================= ENROLL =================
def enroll_fingerprint(location, name=None):

    init_sensor()

    if location < 1 or location > 127:
        print("❌ ID tidak valid")
        return

    if name is None:
        name = input("Masukkan nama: ")

    users = load_users()

    max_attempt = 3
    attempt = 0

    while attempt < max_attempt:

        print("\n👉 Tempelkan sidik jari 1...")
        if not wait_finger():
            print("❌ Sensor error")
            return

        if sensor.convert(1) != adafruit_fingerprint.OK:
            print("❌ Gagal baca jari")
            attempt += 1
            wait_release()
            continue

        wait_release()

        print("👉 Tempelkan sidik jari 2...")
        if not wait_finger():
            print("❌ Sensor error")
            return

        if sensor.convert(2) != adafruit_fingerprint.OK:
            print("❌ Gagal baca jari kedua")
            attempt += 1
            wait_release()
            continue

        if sensor.create_model() == adafruit_fingerprint.OK:

            if sensor.store(location) == adafruit_fingerprint.OK:

                users[location] = name
                save_users(users)

                print("\n🎉 ENROLL BERHASIL!")
                print(f"ID   : {location}")
                print(f"Nama : {name}")

            else:
                print("❌ Gagal simpan ke sensor")

            wait_release()
            return

        else:
            attempt += 1
            print(f"❌ Sidik jari tidak cocok ({attempt}/{max_attempt})")
            wait_release()

    print("❌ Enroll gagal 3x")


# ================= DELETE =================
def delete_fingerprint():
    init_sensor()

    users = load_users()
    location = int(input("ID yang mau dihapus: "))

    if sensor.delete(location) == adafruit_fingerprint.OK:
        print("🗑️ Berhasil dihapus")

        if location in users:
            del users[location]
            save_users(users)

    else:
        print("❌ Gagal hapus")


# ================= LIST =================
def list_users():
    users = load_users()
    print("\n===== USER FINGERPRINT =====")
    for id, name in users.items():
        print(f"{id} : {name}")


# ================= MENU =================
def menu():
    print("\n========== ADMIN PANEL ==========")
    print("=== FINGERPRINT ===")
    print("[1] Enroll Fingerprint")
    print("[2] Hapus Fingerprint")
    print("[3] Lihat User Fingerprint")

    print("\n=== RFID ===")
    print("[4] Enroll RFID")
    print("[5] Hapus RFID")
    print("[6] Lihat RFID")

    print("\n[q] Keluar")


# ================= MAIN =================
if __name__ == "__main__":
    while True:
        menu()
        cmd = input("Pilih: ")

        # ===== FINGERPRINT =====
        if cmd == "1":
            users = load_users()
            new_id = max(users.keys(), default=0) + 1
            name = input("Nama: ")
            enroll_fingerprint(new_id, name)

        elif cmd == "2":
            delete_fingerprint()

        elif cmd == "3":
            list_users()

        # ===== RFID =====
        elif cmd == "4":
            enroll_rfid()

        elif cmd == "5":
            delete_rfid()

        elif cmd == "6":
            list_rfid()

        elif cmd.lower() == "q":
            print("Keluar...")
            break
