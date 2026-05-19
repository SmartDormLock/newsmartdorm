import sys
sys.stdout.reconfigure(encoding='utf-8')

import time

from core.hardware.rfid import RFIDReader

DATA_FILE = "data/rfid/cards.txt"

reader = None

# ================= INIT =================
def init_reader():

    global reader

    try:

        if reader is None:

            reader = RFIDReader()

    except Exception as e:

        print(f"❌ RFID init error: {e}")

        reader = None

# ================= RESET READER =================
def reset_reader():

    global reader

    try:

        reader = RFIDReader()

        print("🔄 RFID reader reconnected")

    except Exception as e:

        print(f"❌ RFID reconnect gagal: {e}")

        reader = None

# ================= LOAD =================
def load_cards():

    cards = {}

    try:

        with open(DATA_FILE, "r") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                uid, name = line.split(",", 1)

                cards[uid] = name

    except FileNotFoundError:

        pass

    except Exception as e:

        print(f"❌ Gagal load cards: {e}")

    return cards

# ================= SAVE =================
def save_cards(cards):

    try:

        with open(DATA_FILE, "w") as f:

            for uid, name in cards.items():

                f.write(f"{uid},{name}\n")

    except Exception as e:

        print(f"❌ Gagal save cards: {e}")

# ================= UID CONVERT =================
def uid_to_string(uid):

    return "".join(str(x) for x in uid)

# ================= SAFE READ UID =================
def safe_read_uid(timeout=10):

    global reader

    start_time = time.time()

    while True:

        # ================= TIMEOUT =================
        if time.time() - start_time > timeout:

            print("⏰ RFID timeout")

            return None

        try:

            if reader is None:

                init_reader()

                if reader is None:

                    time.sleep(1)
                    continue

            uid = reader.read_uid(timeout=2)

            # ================= INVALID =================
            if not uid:

                time.sleep(0.1)
                continue

            return uid

        except Exception as e:

            print(f"❌ RFID read error: {e}")

            reset_reader()

            time.sleep(0.5)

# ================= SCAN LOGIN =================
def scan_rfid(timeout=10):

    cards = load_cards()

    print("📡 Tempelkan kartu...")

    uid = safe_read_uid(timeout)

    # ================= TIMEOUT =================
    if uid is None:

        return None

    try:

        uid_str = uid_to_string(uid)

        print(f"UID: {uid_str}")

        if uid_str in cards:

            print("✅ RFID dikenali")

            return {

                "name": cards[uid_str],
                "uid": uid_str
            }

        print("❌ RFID tidak terdaftar")

        return None

    except Exception as e:

        print(f"❌ Error RFID: {e}")

        return None

# ================= SCAN NEW RFID =================
def scan_new_rfid(timeout=10):

    cards = load_cards()

    print("📡 Tempelkan kartu baru...")

    uid = safe_read_uid(timeout)

    # ================= TIMEOUT =================
    if uid is None:

        return None

    try:

        uid_str = uid_to_string(uid)

        print(f"UID: {uid_str}")

        # ================= DUPLICATE =================
        if uid_str in cards:

            print("⚠️ Kartu sudah terdaftar")

            return None

        print("✅ Kartu baru berhasil dibaca")

        return {

            "uid": uid_str
        }

    except Exception as e:

        print(f"❌ Error RFID baru: {e}")

        return None

# ================= ENROLL MANUAL =================
def enroll_rfid():

    cards = load_cards()

    print("📡 Tempelkan kartu untuk didaftarkan...")

    uid = safe_read_uid(timeout=15)

    # ================= TIMEOUT =================
    if uid is None:

        print("❌ RFID timeout")

        return

    try:

        uid_str = uid_to_string(uid)

        print(f"UID: {uid_str}")

        # ================= DUPLICATE =================
        if uid_str in cards:

            print("⚠️ Kartu sudah terdaftar")

            return

        name = input("Masukkan nama: ").strip()

        if not name:

            print("❌ Nama tidak boleh kosong")

            return

        cards[uid_str] = name

        save_cards(cards)

        print("✅ Kartu berhasil didaftarkan!")

        print(f"UID  : {uid_str}")

        print(f"Nama : {name}")

    except Exception as e:

        print(f"❌ Error enroll RFID: {e}")

# ================= DELETE =================
def delete_rfid():

    cards = load_cards()

    uid = input(
        "Masukkan UID yang mau dihapus: "
    ).strip()

    if uid in cards:

        del cards[uid]

        save_cards(cards)

        print("🗑️ Kartu dihapus")

    else:

        print("❌ UID tidak ditemukan")

# ================= LIST =================
def list_rfid():

    cards = load_cards()

    print("\n===== DATA RFID =====")

    if not cards:

        print("Belum ada kartu terdaftar")

        return

    for uid, name in cards.items():

        print(f"{uid} : {name}")
