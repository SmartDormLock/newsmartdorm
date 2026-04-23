import os
import cv2
import time
from PIL import Image
from facenet_pytorch import MTCNN

DATASET_PATH = "data/face/dataset"

# 🔥 ringan + tetap aligned
mtcnn = MTCNN(keep_all=False, image_size=160, device="cpu")


# ================= UI =================
def draw_info(frame, user, pose, count, total, status=""):
    cv2.putText(frame, f"User: {user}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.putText(frame, f"Pose: {pose}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.putText(frame, f"Capture: {count}/{total}", (10, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    if status:
        cv2.putText(frame, status, (10, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

    cv2.putText(frame, "Press S to start | ESC to exit", (10, 135),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)


# ================= MAIN =================
def capture_dataset():
    poses = ["lurus", "kanan", "kiri", "atas", "bawah"]
    photos_per_pose = 10

    prepare_time = 2      # ⏳ waktu siap sebelum capture pose
    cooldown_time = 2     # ⏳ jeda antar pose
    frame_skip = 3        # 🔥 detect tiap N frame (biar ringan)

    user_name = input("Masukkan nama user: ").strip()
    if not user_name:
        print("❌ Nama tidak boleh kosong")
        return

    user_path = os.path.join(DATASET_PATH, user_name)
    for pose in poses:
        os.makedirs(os.path.join(user_path, pose), exist_ok=True)

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():
        print("❌ Kamera tidak bisa dibuka")
        return

    print("\n[INFO] Tekan 'S' untuk mulai capture | ESC untuk keluar")

    # ================= PREVIEW =================
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        draw_info(frame, user_name, "-", 0, photos_per_pose)

        cv2.imshow("Capture", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            break
        elif key == 27:
            cap.release()
            cv2.destroyAllWindows()
            return

    print("\n[INFO] Mulai capture dataset...")

    # ================= CAPTURE =================
    for idx, pose in enumerate(poses):
        print(f"\n👉 Pose: {pose}")
        cv2.setWindowTitle("Capture", f"Capture - {pose}")

        # ===== PREPARE =====
        start = time.time()
        while time.time() - start < prepare_time:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)

            draw_info(
                frame,
                user_name,
                pose,
                0,
                photos_per_pose,
                f"Siapkan pose ({int(prepare_time - (time.time() - start)) + 1}s)"
            )

            cv2.imshow("Capture", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                cap.release()
                cv2.destroyAllWindows()
                return

        count = 0
        frame_count = 0

        # ===== CAPTURE LOOP =====
        while count < photos_per_pose:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            draw_info(frame, user_name, pose, count, photos_per_pose)

            # 🔥 DETECT TIDAK SETIAP FRAME
            if frame_count % frame_skip == 0:
                small = cv2.resize(frame, (320, 240))
                img = Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))
                face = mtcnn(img)

                if face is not None:
                    face_img = face.permute(1, 2, 0).numpy() * 255
                    face_img = face_img.astype("uint8")

                    filename = os.path.join(user_path, pose, f"{count}.jpg")
                    cv2.imwrite(filename, cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR))

                    print(f"Saved: {filename}")
                    count += 1

                    cv2.imshow("Aligned Face", face_img)

            frame_count += 1

            cv2.imshow("Capture", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                cap.release()
                cv2.destroyAllWindows()
                return

        # ===== COOLDOWN (antar pose) =====
        if idx < len(poses) - 1:
            print(f"[INFO] Pindah ke pose berikutnya dalam {cooldown_time} detik...")

            start_cd = time.time()
            while time.time() - start_cd < cooldown_time:
                ret, frame = cap.read()
                if not ret:
                    continue

                frame = cv2.flip(frame, 1)

                draw_info(
                    frame,
                    user_name,
                    pose,
                    photos_per_pose,
                    photos_per_pose,
                    f"Next pose in {int(cooldown_time - (time.time() - start_cd)) + 1}s"
                )

                cv2.imshow("Capture", frame)

                if cv2.waitKey(1) & 0xFF == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    return

    cap.release()
    cv2.destroyAllWindows()

    print("\n✅ Dataset selesai (smooth + cooldown + aligned)")


# ================= ENTRY =================
if __name__ == "__main__":
    capture_dataset()
