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

    success_counter = 0
    REQUIRED_SUCCESS = 7
    FRAME_DELAY = 0.2  # lebih santai  # ?? delay per frame biar gak terlalu cepat

    while True:
        start_time = time.time()

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)

        boxes, _ = mtcnn.detect(img)

        detected_name = None

        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)

                face = img.crop((x1, y1, x2, y2))
                face = face.resize((160, 160))

                face_tensor = torch.tensor(np.array(face)).permute(2, 0, 1) / 255.0
                face_tensor = face_tensor.unsqueeze(0).float()

                emb = model(face_tensor).detach().numpy()

                distances = np.linalg.norm(known_embeddings - emb, axis=1)
                idx = np.argmin(distances)

                confidence = distances[idx]

                if confidence < 0.9:
                    name = names[idx]
                    color = (0, 255, 0)
                    success_counter += 1
                    detected_name = name
                else:
                    name = "Unknown"
                    color = (0, 0, 255)
                    success_counter = 0

                # bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                label = f"{name} ({confidence:.2f})"
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # status verifikasi
        cv2.putText(frame, f"Verifying... ({success_counter}/{REQUIRED_SUCCESS})",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow("Face Recognition", frame)

        # kalau sukses stabil
        if success_counter >= REQUIRED_SUCCESS:
            cap.release()
            cv2.destroyAllWindows()
            return detected_name

        if cv2.waitKey(1) & 0xFF == 27:
            break

        # ?? adaptive delay (biar smooth, gak nge-lag)
        elapsed = time.time() - start_time
        if elapsed < FRAME_DELAY:
            time.sleep(FRAME_DELAY - elapsed)

    cap.release()
    cv2.destroyAllWindows()
    return None
