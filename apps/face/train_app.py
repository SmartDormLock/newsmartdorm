import os
import pickle
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

DATASET_PATH = "data/face/dataset"
OUTPUT_FILE = "data/face/embeddings.pkl"

device = "cpu"

# ?? model
mtcnn = MTCNN(keep_all=False, image_size=160, device=device)
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)


def load_image(img_path):
    try:
        img = Image.open(img_path).convert("RGB")
        return img
    except:
        return None


def train_embeddings():
    embeddings = []
    names = []

    total_images = 0
    processed = 0

    print("\n?? Mulai training embeddings...\n")

    # hitung total image dulu (buat progress)
    for user in os.listdir(DATASET_PATH):
        user_path = os.path.join(DATASET_PATH, user)
        if not os.path.isdir(user_path):
            continue

        for pose in os.listdir(user_path):
            pose_path = os.path.join(user_path, pose)
            total_images += len(os.listdir(pose_path))

    # proses semua image
    for user in os.listdir(DATASET_PATH):
        user_path = os.path.join(DATASET_PATH, user)

        if not os.path.isdir(user_path):
            continue

        print(f"\n?? Processing: {user}")

        for pose in os.listdir(user_path):
            pose_path = os.path.join(user_path, pose)

            for img_name in os.listdir(pose_path):
                img_path = os.path.join(pose_path, img_name)

                img = load_image(img_path)
                if img is None:
                    continue

                # ?? DETECT (fallback kalau belum aligned)
                face = mtcnn(img)

                if face is None:
                    print(f"? Skip (no face): {img_path}")
                    continue

                emb = model(face.unsqueeze(0).to(device)).detach().cpu().numpy()[0]

                embeddings.append(emb)
                names.append(user)

                processed += 1

                # progress bar sederhana
                print(f"[{processed}/{total_images}] {img_path}")

    # simpan
    embeddings = np.array(embeddings)

    with open(OUTPUT_FILE, "wb") as f:
        pickle.dump((embeddings, names), f)

    print("\n? Training selesai!")
    print(f"Total embedding: {len(embeddings)}")
    print(f"Saved ke: {OUTPUT_FILE}")


# ================= ENTRY =================
if __name__ == "__main__":
    train_embeddings()
