import os
import cv2
import time
import sys

from PIL import Image
from facenet_pytorch import MTCNN

DATASET_PATH = "data/face/dataset"

# ================= FACE DETECTOR =================
mtcnn = MTCNN(
    keep_all=False,
    image_size=160,
    device="cpu"
)

# ================= CONFIG =================
conditions = [
    "Normal",
    "Kacamata",
    "Masker"
]

poses = [
    "Lurus",
    "Kanan",
    "Kiri",
    "Atas",
    "Bawah"
]

photos_per_pose = 10

prepare_time = 2
cooldown_time = 2
condition_prepare_time = 5

frame_skip = 3

TEXT_COLOR = (255, 255, 255)

FONT = cv2.FONT_HERSHEY_SIMPLEX


# ================= UI =================
def draw_info(
    frame,
    user,
    condition,
    pose,
    count,
    total,
    status=""
):

    cv2.putText(
        frame,
        f"User       : {user}",
        (20, 35),
        FONT,
        0.65,
        TEXT_COLOR,
        2
    )

    cv2.putText(
        frame,
        f"Condition  : {condition}",
        (20, 70),
        FONT,
        0.65,
        TEXT_COLOR,
        2
    )

    cv2.putText(
        frame,
        f"Pose       : {pose}",
        (20, 105),
        FONT,
        0.65,
        TEXT_COLOR,
        2
    )

    cv2.putText(
        frame,
        f"Capture    : {count}/{total}",
        (20, 140),
        FONT,
        0.65,
        TEXT_COLOR,
        2
    )

    if status:

        cv2.putText(
            frame,
            status,
            (20, 190),
            FONT,
            0.7,
            TEXT_COLOR,
            2
        )

    cv2.putText(
        frame,
        "Press S to Start | ESC to Exit",
        (20, 440),
        FONT,
        0.55,
        TEXT_COLOR,
        1
    )


# ================= SAVE FACE =================
def save_face(face_tensor, save_path):

    face_img = (
        face_tensor.permute(1, 2, 0).numpy() * 255
    )

    face_img = face_img.astype("uint8")

    cv2.imwrite(
        save_path,
        cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR)
    )

    cv2.imshow(
        "Aligned Face",
        face_img
    )


# ================= MAIN =================
def capture_dataset():

    # ================= USER NAME =================
    if len(sys.argv) > 1:

        user_name = sys.argv[1].strip()

        print(f"\n👤 User : {user_name}")

    else:

        user_name = input("Masukkan nama user : ").strip()

    if not user_name:

        print("\n❌ Nama user tidak boleh kosong")

        return

    # ================= CREATE FOLDER =================
    user_path = os.path.join(
        DATASET_PATH,
        user_name
    )

    for condition in conditions:

        for pose in poses:

            os.makedirs(
                os.path.join(
                    user_path,
                    condition.lower(),
                    pose.lower()
                ),
                exist_ok=True
            )

    # ================= CAMERA =================
    cap = cv2.VideoCapture(0)

    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():

        print("\n❌ Kamera tidak bisa dibuka")

        return

    print("\n==============================")
    print(" SmartDormLock Dataset Capture")
    print("==============================")
    print(" Press S   : Start")
    print(" Press ESC : Exit")
    print("==============================")

    # ================= PREVIEW =================
    while True:

        ret, frame = cap.read()

        if not ret:
            continue

        frame = cv2.flip(frame, 1)

        draw_info(
            frame,
            user_name,
            "-",
            "-",
            0,
            photos_per_pose
        )

        cv2.imshow(
            "SmartDormLock Dataset",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            break

        elif key == 27:

            cap.release()
            cv2.destroyAllWindows()

            return

    print("\n[INFO] Memulai capture dataset...\n")

    # ================= CONDITION LOOP =================
    for condition in conditions:

        print("\n==============================")
        print(f" CONDITION : {condition}")
        print("==============================")

        # ================= CONDITION PREPARE =================
        start_condition = time.time()

        while time.time() - start_condition < condition_prepare_time:

            ret, frame = cap.read()

            if not ret:
                continue

            frame = cv2.flip(frame, 1)

            countdown = (
                int(
                    condition_prepare_time -
                    (time.time() - start_condition)
                ) + 1
            )

            draw_info(
                frame,
                user_name,
                condition,
                "-",
                0,
                photos_per_pose,
                f"Siapkan kondisi {condition} ({countdown}s)"
            )

            cv2.imshow(
                "SmartDormLock Dataset",
                frame
            )

            if cv2.waitKey(1) & 0xFF == 27:

                cap.release()
                cv2.destroyAllWindows()

                return

        # ================= POSE LOOP =================
        for idx, pose in enumerate(poses):

            print(f"\n👉 Pose : {pose}")

            start_prepare = time.time()

            # ================= PREPARE =================
            while time.time() - start_prepare < prepare_time:

                ret, frame = cap.read()

                if not ret:
                    continue

                frame = cv2.flip(frame, 1)

                countdown = (
                    int(
                        prepare_time -
                        (time.time() - start_prepare)
                    ) + 1
                )

                draw_info(
                    frame,
                    user_name,
                    condition,
                    pose,
                    0,
                    photos_per_pose,
                    f"Siapkan pose {pose} ({countdown}s)"
                )

                cv2.imshow(
                    "SmartDormLock Dataset",
                    frame
                )

                if cv2.waitKey(1) & 0xFF == 27:

                    cap.release()
                    cv2.destroyAllWindows()

                    return

            count = 0
            frame_count = 0

            # ================= CAPTURE LOOP =================
            while count < photos_per_pose:

                ret, frame = cap.read()

                if not ret:
                    continue

                frame = cv2.flip(frame, 1)

                draw_info(
                    frame,
                    user_name,
                    condition,
                    pose,
                    count,
                    photos_per_pose
                )

                # ================= FACE DETECTION =================
                if frame_count % frame_skip == 0:

                    small = cv2.resize(
                        frame,
                        (320, 240)
                    )

                    img = Image.fromarray(
                        cv2.cvtColor(
                            small,
                            cv2.COLOR_BGR2RGB
                        )
                    )

                    face = mtcnn(img)

                    if face is not None:

                        save_path = os.path.join(
                            user_path,
                            condition.lower(),
                            pose.lower(),
                            f"{condition.lower()}_{pose.lower()}_{count}.jpg"
                        )

                        save_face(
                            face,
                            save_path
                        )

                        print(f"✅ Saved : {save_path}")

                        count += 1

                frame_count += 1

                cv2.imshow(
                    "SmartDormLock Dataset",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                if key == 27:

                    cap.release()
                    cv2.destroyAllWindows()

                    return

            # ================= COOLDOWN =================
            if idx < len(poses) - 1:

                start_cd = time.time()

                while time.time() - start_cd < cooldown_time:

                    ret, frame = cap.read()

                    if not ret:
                        continue

                    frame = cv2.flip(frame, 1)

                    countdown = (
                        int(
                            cooldown_time -
                            (time.time() - start_cd)
                        ) + 1
                    )

                    draw_info(
                        frame,
                        user_name,
                        condition,
                        pose,
                        photos_per_pose,
                        photos_per_pose,
                        f"Pose berikutnya ({countdown}s)"
                    )

                    cv2.imshow(
                        "SmartDormLock Dataset",
                        frame
                    )

                    if cv2.waitKey(1) & 0xFF == 27:

                        cap.release()
                        cv2.destroyAllWindows()

                        return

    # ================= FINISH =================
    cap.release()

    cv2.destroyAllWindows()

    total_images = (
        len(conditions)
        * len(poses)
        * photos_per_pose
    )

    print("\n==============================")
    print(" Dataset Selesai")
    print("==============================")
    print(f" User         : {user_name}")
    print(f" Conditions   : {len(conditions)}")
    print(f" Poses        : {len(poses)}")
    print(f" Total Images : {total_images}")
    print("==============================")


# ================= ENTRY =================
if __name__ == "__main__":
    capture_dataset()
