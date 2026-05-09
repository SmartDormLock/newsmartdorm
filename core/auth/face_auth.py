import torch
import numpy as np
import pickle
import cv2
import time
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

DATA_FILE = "data/face/embeddings.pkl"

mtcnn = MTCNN(keep_all=True)
model = InceptionResnetV1(pretrained='vggface2').eval()

with open(DATA_FILE, "rb") as f:
    known_embeddings, names = pickle.load(f)


def scan_face():

    cap = cv2.VideoCapture(0)

    print("?? Scan wajah...")

    MAX_VERIFY = 7
    REQUIRED_SUCCESS = 3

    verify_count = 0
    success_count = 0

    FRAME_DELAY = 0.5

    while verify_count < MAX_VERIFY:

        ret, frame = cap.read()

        if not ret:
            continue

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(rgb)

        boxes, _ = mtcnn.detect(img)

        detected_name = None

        name = "Unknown"
        color = (0, 0, 255)

        confidence = 999

        # ================= FACE DETECTED =================
        if boxes is not None:

            box = boxes[0]

            x1, y1, x2, y2 = map(int, box)

            face = img.crop((x1, y1, x2, y2))

            face = face.resize((160, 160))

            face_tensor = (
                torch.tensor(np.array(face))
                .permute(2, 0, 1) / 255.0
            )

            face_tensor = face_tensor.unsqueeze(0).float()

            emb = model(face_tensor).detach().numpy()

            distances = np.linalg.norm(
                known_embeddings - emb,
                axis=1
            )

            idx = np.argmin(distances)

            confidence = distances[idx]

            # semakin kecil = semakin mirip
            if confidence < 0.7:

                name = names[idx]

                color = (0, 255, 0)

                success_count += 1

                detected_name = name

            else:

                success_count = 0

            # 1 wajah = 1 verification
            verify_count += 1

            # ================= BOUNDING BOX =================
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )

            label = f"{name} ({confidence:.2f})"

            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        # ================= STATUS =================
        cv2.putText(
            frame,
            f"Verifying... ({verify_count}/{MAX_VERIFY})",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        cv2.imshow("Face Recognition", frame)

        # ================= SUCCESS =================
        if success_count >= REQUIRED_SUCCESS:

            print(f"? Face verified: {detected_name}")

            cap.release()

            cv2.destroyAllWindows()

            return detected_name

        # ================= ESC =================
        if cv2.waitKey(1) & 0xFF == 27:
            break

        time.sleep(FRAME_DELAY)

    print("? Wajah tidak dikenali")

    cap.release()

    cv2.destroyAllWindows()

    return None
