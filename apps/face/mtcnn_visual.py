import cv2
import time
import numpy as np

from PIL import Image
from facenet_pytorch import MTCNN

# ==================================================
# CONFIG
# ==================================================

device = "cpu"

mtcnn = MTCNN(
    keep_all=True,
    image_size=160,
    device=device
)

# ==================================================
# CAMERA
# ==================================================

cap = cv2.VideoCapture(0)

cap.set(3, 640)
cap.set(4, 480)

if not cap.isOpened():

    print("❌ Kamera gagal dibuka")
    exit()

print("\n==============================")
print(" MTCNN CASCADE VISUALIZATION ")
print("==============================")
print(" 1 = P-NET")
print(" 2 = R-NET")
print(" 3 = O-NET")
print(" A = AUTO MODE")
print(" ESC = EXIT")
print("==============================")

# ==================================================
# STAGE CONTROL
# ==================================================

stage = 1

auto_mode = False

stage_start = time.time()

# ==================================================
# MAIN LOOP
# ==================================================

while True:

    ret, frame = cap.read()

    if not ret:
        continue

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    img = Image.fromarray(rgb)

    display = frame.copy()

    # ==================================================
    # AUTO MODE
    # ==================================================

    if auto_mode:

        elapsed = time.time() - stage_start

        # P-NET
        if elapsed < 3:
            stage = 1

        # R-NET
        elif elapsed < 6:
            stage = 2

        # O-NET
        else:
            stage = 3

            # restart cycle
            if elapsed > 9:
                stage_start = time.time()

    # ==================================================
    # DETECTION
    # ==================================================

    boxes, probs, landmarks = mtcnn.detect(
        img,
        landmarks=True
    )

    # ==================================================
    # STAGE 1 : P-NET
    # ==================================================

    if stage == 1:

        cv2.putText(
            display,
            "[P-NET] Proposal Network",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 0, 0),
            3
        )

        cv2.putText(
            display,
            "Scanning seluruh frame untuk mencari kandidat wajah",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )

        if boxes is not None:

            for box in boxes:

                x1, y1, x2, y2 = map(int, box)

                # box kasar / lebih besar
                padding = 60

                cv2.rectangle(
                    display,
                    (
                        max(0, x1 - padding),
                        max(0, y1 - padding)
                    ),
                    (
                        min(frame.shape[1], x2 + padding),
                        min(frame.shape[0], y2 + padding)
                    ),
                    (255, 0, 0),
                    3
                )

    # ==================================================
    # STAGE 2 : R-NET
    # ==================================================

    elif stage == 2:

        cv2.putText(
            display,
            "[R-NET] Refine Network",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 255),
            3
        )

        cv2.putText(
            display,
            "Menyaring false positive & memperbaiki bounding box",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        if boxes is not None:

            for box in boxes:

                x1, y1, x2, y2 = map(int, box)

                # refine box
                padding = 25

                cv2.rectangle(
                    display,
                    (
                        max(0, x1 - padding),
                        max(0, y1 - padding)
                    ),
                    (
                        min(frame.shape[1], x2 + padding),
                        min(frame.shape[0], y2 + padding)
                    ),
                    (0, 255, 255),
                    3
                )

    # ==================================================
    # STAGE 3 : O-NET
    # ==================================================

    elif stage == 3:

        cv2.putText(
            display,
            "[O-NET] Output Network",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            3
        )

        cv2.putText(
            display,
            "Final face detection + landmark wajah",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        if boxes is not None:

            for i, box in enumerate(boxes):

                x1, y1, x2, y2 = map(int, box)

                # final precise box
                cv2.rectangle(
                    display,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    4
                )

                # confidence
                conf = probs[i]

                cv2.putText(
                    display,
                    f"Face {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                # LANDMARK
                if landmarks is not None:

                    points = landmarks[i]

                    labels = [
                        "Left Eye",
                        "Right Eye",
                        "Nose",
                        "Mouth L",
                        "Mouth R"
                    ]

                    for j, point in enumerate(points):

                        px, py = map(int, point)

                        cv2.circle(
                            display,
                            (px, py),
                            5,
                            (0, 0, 255),
                            -1
                        )

                        cv2.putText(
                            display,
                            labels[j],
                            (px + 5, py - 5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.45,
                            (0, 0, 255),
                            1
                        )

        # ==================================================
        # ALIGNED FACE
        # ==================================================

        face_tensor = mtcnn(img)

        if face_tensor is not None:

            if len(face_tensor.shape) == 4:
                aligned = face_tensor[0]
            else:
                aligned = face_tensor

            aligned_face = (
                aligned
                .permute(1, 2, 0)
                .cpu()
                .numpy()
            )

            # normalize tensor -> image
            aligned_face = (
                (aligned_face - aligned_face.min()) /
                (aligned_face.max() - aligned_face.min())
            ) * 255

            aligned_face = aligned_face.astype(np.uint8)

            aligned_face = cv2.cvtColor(
                aligned_face,
                cv2.COLOR_RGB2BGR
            )

            cv2.putText(
                aligned_face,
                "Aligned Face",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                aligned_face,
                "160 x 160",
                (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

            cv2.imshow(
                "Aligned Face",
                aligned_face
            )

    # ==================================================
    # MODE INFO
    # ==================================================

    mode_text = (
        "AUTO MODE"
        if auto_mode
        else "MANUAL MODE"
    )

    cv2.putText(
        display,
        mode_text,
        (20, 440),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.putText(
        display,
        "1:P-NET  2:R-NET  3:O-NET  A:AUTO",
        (20, 470),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    # ==================================================
    # SHOW
    # ==================================================

    cv2.imshow(
        "MTCNN Cascade Visualization",
        display
    )

    # ==================================================
    # KEYBOARD
    # ==================================================

    key = cv2.waitKey(1) & 0xFF

    # ESC
    if key == 27:
        break

    # MANUAL STAGE
    elif key == ord("1"):

        auto_mode = False
        stage = 1

    elif key == ord("2"):

        auto_mode = False
        stage = 2

    elif key == ord("3"):

        auto_mode = False
        stage = 3

    # AUTO MODE
    elif key == ord("a"):

        auto_mode = True
        stage_start = time.time()

# ==================================================
# RELEASE
# ==================================================

cap.release()

cv2.destroyAllWindows()
