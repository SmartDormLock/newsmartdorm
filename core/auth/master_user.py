import os

MASTER_FILE = "data/users/master_users.txt"


# ================= LOAD MASTER USERS =================
def load_master_users():
    users = {}

    try:
        # auto create folder kalau belum ada
        os.makedirs(os.path.dirname(MASTER_FILE), exist_ok=True)

        # auto create file kalau belum ada
        if not os.path.exists(MASTER_FILE):
            open(MASTER_FILE, "w").close()

        with open(MASTER_FILE, "r") as f:

            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    name, uid, fid = line.split(",")

                    users[name] = {
                        "rfid": uid,
                        "finger": int(fid)
                    }

                except ValueError:
                    print(f"⚠️ Format data invalid: {line}")

    except Exception as e:
        print(f"❌ Gagal load master users: {e}")

    return users


# ================= ADD MASTER USER =================
def add_master_user(name, uid, fid):

    try:
        # auto create folder
        os.makedirs(os.path.dirname(MASTER_FILE), exist_ok=True)

        # auto create file
        if not os.path.exists(MASTER_FILE):
            open(MASTER_FILE, "w").close()

        with open(MASTER_FILE, "a") as f:
            f.write(f"{name},{uid},{fid}\n")

        print("✅ Master user berhasil disimpan")

    except Exception as e:
        print(f"❌ Gagal simpan master user: {e}")


# ================= LIST MASTER USERS =================
def list_master_users():

    users = load_master_users()

    print("\n===== MASTER USERS =====")

    if not users:
        print("Belum ada user terdaftar")
        return

    for name, data in users.items():
        print(f"Nama   : {name}")
        print(f"RFID   : {data['rfid']}")
        print(f"Finger : {data['finger']}")
        print("------------------------")
