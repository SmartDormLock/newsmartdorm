from core.utils.firebase_logger import db


def get_user_room_data(user_name):

    try:

        users = (
            db.collection("users")
            .where(
                "name",
                "==",
                user_name
            )
            .limit(1)
            .stream()
        )

        for doc in users:

            data = doc.to_dict()

            return {

                "building":
                    data.get(
                        "building",
                        "UNKNOWN"
                    ),

                "room":
                    data.get(
                        "room",
                        "UNKNOWN"
                    )
            }

    except Exception as e:

        print(
            f"[USER ROOM ERROR] {e}"
        )

    return {

        "building": "UNKNOWN",
        "room": "UNKNOWN"
    }
