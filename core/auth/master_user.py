MASTER_FILE = "data/users/master_users.txt"

def load_master_users():
    users = {}
    try:
        with open(MASTER_FILE, "r") as f:
            for line in f:
                name, uid, fid = line.strip().split(",")
                users[name] = {
                    "rfid": uid,
                    "finger": int(fid)
                }
    except:
        pass
    return users

def add_master_user(name, uid, fid):
    with open(MASTER_FILE, "a") as f:
        f.write(f"{name},{uid},{fid}\n")
