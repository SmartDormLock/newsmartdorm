import os

from core.auth.rfid_auth import (
    load_cards
)

from core.auth.fingerprint_auth import (
    load_users
)

from core.auth.master_user import (
    MASTER_FILE
)


def rebuild_master_users():

    print("\n================================")
    print("     REBUILD MASTER USERS")
    print("================================")

    cards = load_cards()
    fingers = load_users()

    # uid -> name
    rfid_users = {}

    for uid, name in cards.items():

        rfid_users[name] = uid

    # fid -> name
    finger_users = {}

    for fid, name in fingers.items():

        finger_users[name] = fid

    all_names = sorted(

        set(rfid_users.keys())

        |

        set(finger_users.keys())

    )

    os.makedirs(

        os.path.dirname(MASTER_FILE),

        exist_ok=True
    )

    with open(

        MASTER_FILE,

        "w"

    ) as f:

        for name in all_names:

            uid = rfid_users.get(

                name,

                0
            )

            fid = finger_users.get(

                name,

                0
            )

            f.write(

                f"{name},{uid},{fid}\n"
            )

            print(

                f"? {name}"
                f" | RFID={uid}"
                f" | FID={fid}"
            )

    print("\n================================")
    print(" REBUILD COMPLETED")
    print("================================")


if __name__ == "__main__":

    rebuild_master_users()
