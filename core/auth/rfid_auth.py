from core.hardware.rfid import RFIDReader

DATA_FILE = "data/rfid/cards.txt"

reader = None


def init_reader():
    global reader
    if reader is None:
        reader = RFIDReader()


def load_cards():
    cards = {}
    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                uid, name = line.strip().split(",")
                cards[uid] = name
    except:
        pass
    return cards


def save_cards(cards):
    with open(DATA_FILE, "w") as f:
        for uid, name in cards.items():
            f.write(f"{uid},{name}\n")


def uid_to_string(uid):
    return "".join(str(x) for x in uid)


# ================= SCAN =================
def scan_rfid():
    init_reader()
    cards = load_cards()

    print("?? Tempelkan kartu...")

    uid = reader.read_uid()
    uid_str = uid_to_string(uid)

    print(f"UID: {uid_str}")

    if uid_str in cards:
        return cards[uid_str]

    return None


# ================= ENROLL =================
def enroll_rfid():
    init_reader()
    cards = load_cards()

    print("?? Tempelkan kartu untuk didaftarkan...")
    uid = reader.read_uid()
    uid_str = uid_to_string(uid)

    if uid_str in cards:
        print("?? Kartu sudah terdaftar")
        return

    name = input("Masukkan nama: ")

    cards[uid_str] = name
    save_cards(cards)

    print("?? Kartu berhasil didaftarkan!")
    print(f"UID  : {uid_str}")
    print(f"Nama : {name}")


# ================= DELETE =================
def delete_rfid():
    cards = load_cards()

    uid = input("Masukkan UID yang mau dihapus: ")

    if uid in cards:
        del cards[uid]
        save_cards(cards)
        print("??? Kartu dihapus")
    else:
        print("? UID tidak ditemukan")


# ================= LIST =================
def list_rfid():
    cards = load_cards()

    print("\n===== DATA RFID =====")
    for uid, name in cards.items():
        print(f"{uid} : {name}")
