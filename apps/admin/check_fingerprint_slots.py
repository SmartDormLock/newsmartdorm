from core.hardware.fingerprint import FingerprintSensor
from core.auth.fingerprint_auth import load_users


def main():

    print("\n========== FINGERPRINT SLOT CHECK ==========\n")

    # load users.txt
    users = load_users()

    try:
        sensor = FingerprintSensor()

    except Exception as e:
        print(f"? Gagal connect sensor: {e}")
        return

    try:
        # baca template internal sensor
        sensor.finger.read_templates()

        templates = sensor.finger.templates

    except Exception as e:
        print(f"? Gagal baca template sensor: {e}")
        return

    if not templates:

        print("?? Tidak ada fingerprint tersimpan")
        return

    print(f"Total slot terpakai: {len(templates)}\n")

    for slot_id in templates:

        if slot_id in users:

            print(f"[OK]       Slot {slot_id} -> {users[slot_id]}")

        else:

            print(f"[ORPHAN]   Slot {slot_id} -> TIDAK ADA DI users.txt")

    print("\n============================================\n")


if __name__ == "__main__":
    main()
