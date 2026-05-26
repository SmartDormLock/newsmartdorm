import cv2
import time
import pickle
import torch
import numpy as np

from PIL import Image
from facenet_pytorch import (
    MTCNN,
    InceptionResnetV1
)

# ==================================================
# CONFIG
# ==================================================

EMBEDDING_FILE = "data/face/embeddings.pkl"

device = "cpu"

THRESHOLD = 0.85

# ==================================================
# LOAD MTCNN
# ==================================================

mtcnn = MTCNN(
    keep_all=False,
    image_size=160,
    device=device
)

# ==================================================
# LOAD FACENET
# ==================================================

model = (
    InceptionResnetV1(
        pretrained="vggface2"
    )
    .eval()
    .to(device)
)

# ==================================================
# LOAD DATABASE
# ==================================================

print("\n==============================")
print(" LOADING FACE DATABASE ")
print("==============================")

with open(EMBEDDING_FILE, "rb") as f:

    db_embeddings, db_names = pickle.load(f)

print(f"✅ Loaded embeddings : {len(db_embeddings)}")

# ==================================================
# CAMERA
# ==================================================

cap = cv2.VideoCapture(0)

cap.set(3, 640)
cap.set(4, 480)

if not cap.isOpened():

    print("❌ Kamera gagal dibuka")
    exit()

# ==================================================
# FUNCTIONS
# ==================================================

def euclidean_distance(a, b):

    return np.linalg.norm(a - b)


def cosine_similarity(a, b):

    return np.dot(a, b) / (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

# ==================================================
# STAGE CONTROL
# ==================================================

stage = 1

auto_mode = False

stage_start = time.time()

# ==================================================
# CACHE VARIABLE
# ==================================================

face_box = None
aligned_face = None
embedding = None

best_match = "Unknown"
best_distance = 999
best_similarity = -1

recognized = False

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

        if elapsed < 3:
            stage = 1

        elif elapsed < 6:
            stage = 2

        elif elapsed < 9:
            stage = 3

        elif elapsed < 12:
            stage = 4

        else:
            stage = 5

            if elapsed > 15:
                stage_start = time.time()

    # ==================================================
    # HEADER
    # ==================================================

    cv2.putText(
        display,
        "FaceNet Step-by-Step Visualization",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    # ==================================================
    # STEP 1 : FACE DETECTION
    # ==================================================

    if stage >= 1:

        cv2.putText(
            display,
            "[1] FACE DETECTION",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

        boxes, probs = mtcnn.detect(img)

        if boxes is not None:

            box = boxes[0]

            x1, y1, x2, y2 = map(int, box)

            face_box = (x1, y1, x2, y2)

            cv2.rectangle(
                display,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                3
            )

            cv2.putText(
                display,
                "Face Detected",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2
            )

    # ==================================================
    # STEP 2 : FACE ALIGNMENT
    # ==================================================

    if stage >= 2 and face_box is not None:

        cv2.putText(
            display,
            "[2] FACE ALIGNMENT",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        face_tensor = mtcnn(img)

        if face_tensor is not None:

            aligned_face = face_tensor

            # ==================================================
            # TENSOR -> IMAGE
            # ==================================================

            aligned_img = (
                aligned_face
                .permute(1, 2, 0)
                .cpu()
                .numpy()
            )

            # ==================================================
            # DENORMALIZATION
            # ==================================================

            aligned_img = (
                (aligned_img + 1) / 2
            )

            aligned_img = np.clip(
                aligned_img,
                0,
                1
            )

            aligned_img = (
                aligned_img * 255
            ).astype(np.uint8)

            # RGB -> BGR
            aligned_img = cv2.cvtColor(
                aligned_img,
                cv2.COLOR_RGB2BGR
            )

            # smoothing biar natural
            aligned_img = cv2.GaussianBlur(
                aligned_img,
                (3, 3),
                0
            )

            # ==================================================
            # TEXT
            # ==================================================

            cv2.putText(
                aligned_img,
                "Aligned Face",
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                aligned_img,
                "160 x 160",
                (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1
            )

            cv2.imshow(
                "Aligned Face",
                aligned_img
            )

    # ==================================================
    # STEP 3 : EMBEDDING EXTRACTION
    # ==================================================

    if stage >= 3 and aligned_face is not None:

        cv2.putText(
            display,
            "[3] FACENET EMBEDDING",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        with torch.no_grad():

            embedding = (
                model(
                    aligned_face
                    .unsqueeze(0)
                    .to(device)
                )
                .cpu()
                .numpy()[0]
            )

        # ==================================================
        # EMBEDDING WINDOW
        # ==================================================

        vector_panel = np.zeros(
            (500, 400, 3),
            dtype=np.uint8
        )

        cv2.putText(
            vector_panel,
            "FACENET EMBEDDING VECTOR",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

        for i in range(20):

            value = embedding[i]

            text = f"[{i}] : {value:.4f}"

            cv2.putText(
                vector_panel,
                text,
                (10, 60 + i * 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

        cv2.imshow(
            "Embedding Vector",
            vector_panel
        )

    # ==================================================
    # STEP 4 : DATABASE COMPARISON
    # ==================================================

    if stage >= 4 and embedding is not None:

        cv2.putText(
            display,
            "[4] DATABASE COMPARISON",
            (20, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 100, 255),
            2
        )

        compare_panel = np.zeros(
            (500, 500, 3),
            dtype=np.uint8
        )

        cv2.putText(
            compare_panel,
            "TOP DATABASE MATCH",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        matches = []

        for i, db_emb in enumerate(db_embeddings):

            dist = euclidean_distance(
                embedding,
                db_emb
            )

            sim = cosine_similarity(
                embedding,
                db_emb
            )

            name = db_names[i]

            matches.append(
                (
                    name,
                    dist,
                    sim
                )
            )

        matches = sorted(
            matches,
            key=lambda x: x[2],
            reverse=True
        )

        best_match = matches[0][0]
        best_distance = matches[0][1]
        best_similarity = matches[0][2]

        y_offset = 70

        for i in range(min(5, len(matches))):

            name, dist, sim = matches[i]

            text = (
                f"{i+1}. {name} | "
                f"Dist:{dist:.2f} | "
                f"Cos:{sim:.2f}"
            )

            cv2.putText(
                compare_panel,
                text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1
            )

            y_offset += 40

        cv2.imshow(
            "Database Comparison",
            compare_panel
        )

    # ==================================================
    # STEP 5 : RECOGNITION RESULT
    # ==================================================

    if stage >= 5 and embedding is not None:

        cv2.putText(
            display,
            "[5] FACE RECOGNITION RESULT",
            (20, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        recognized = (
            best_similarity > THRESHOLD
        )

        result_panel = np.zeros(
            (300, 500, 3),
            dtype=np.uint8
        )

        if recognized:

            status = "MATCH FOUND"

            color = (0, 255, 0)

            access = "ACCESS GRANTED"

        else:

            status = "UNKNOWN FACE"

            color = (0, 0, 255)

            access = "ACCESS DENIED"

        cv2.putText(
            result_panel,
            status,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            3
        )

        cv2.putText(
            result_panel,
            f"User : {best_match}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            result_panel,
            f"Euclidean : {best_distance:.4f}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            result_panel,
            f"Cosine Similarity : {best_similarity:.4f}",
            (20, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            result_panel,
            access,
            (20, 250),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        cv2.imshow(
            "Recognition Result",
            result_panel
        )

        if face_box is not None:

            x1, y1, x2, y2 = face_box

            label = (
                best_match
                if recognized
                else "UNKNOWN"
            )

            cv2.putText(
                display,
                label,
                (x1, y1 - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
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
        "1:Detect 2:Align 3:Embedding 4:Compare 5:Result A:Auto",
        (20, 470),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1
    )

    # ==================================================
    # SHOW
    # ==================================================

    cv2.imshow(
        "FaceNet Step Visualization",
        display
    )

    # ==================================================
    # KEYBOARD CONTROL
    # ==================================================

    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break

    elif key == ord("1"):

        auto_mode = False
        stage = 1

    elif key == ord("2"):

        auto_mode = False
        stage = 2

    elif key == ord("3"):

        auto_mode = False
        stage = 3

    elif key == ord("4"):

        auto_mode = False
        stage = 4

    elif key == ord("5"):

        auto_mode = False
        stage = 5

    elif key == ord("a"):

        auto_mode = True
        stage_start = time.time()

# ==================================================
# RELEASE
# ==================================================

cap.release()

cv2.destroyAllWindows()
