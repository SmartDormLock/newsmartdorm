import os
import pickle
import numpy as np

from PIL import Image
from facenet_pytorch import (
    MTCNN,
    InceptionResnetV1
)

import torch

DATASET_PATH = "data/face/dataset"
OUTPUT_FILE = "data/face/embeddings.pkl"

device = "cpu"

# ================= MODEL =================
mtcnn = MTCNN(
    keep_all=False,
    image_size=160,
    device=device
)

model = (
    InceptionResnetV1(
        pretrained="vggface2"
    )
    .eval()
    .to(device)
)


# ================= LOAD IMAGE =================
def load_image(img_path):

    try:

        img = Image.open(img_path).convert("RGB")

        return img

    except Exception as e:

        print(f"❌ Error load image: {img_path}")
        print(e)

        return None


# ================= GET ALL IMAGES =================
def get_all_images():

    image_paths = []

    for user in os.listdir(DATASET_PATH):

        user_path = os.path.join(
            DATASET_PATH,
            user
        )

        if not os.path.isdir(user_path):
            continue

        for root, dirs, files in os.walk(user_path):

            for file in files:

                if file.lower().endswith((
                    ".jpg",
                    ".jpeg",
                    ".png"
                )):

                    image_paths.append(
                        (
                            user,
                            os.path.join(root, file)
                        )
                    )

    return image_paths


# ================= TRAIN =================
def train_embeddings():

    embeddings = []
    names = []

    print("\n==============================")
    print(" SmartDormLock Face Training")
    print("==============================")

    image_data = get_all_images()

    total_images = len(image_data)

    print(f"\n📦 Total images found: {total_images}")

    if total_images == 0:

        print("\n❌ Dataset kosong")

        return

    processed = 0
    success = 0
    skipped = 0

    current_user = None

    # ================= PROCESS =================
    for user, img_path in image_data:

        # tampilkan header user
        if current_user != user:

            current_user = user

            print("\n------------------------------")
            print(f"👤 Processing: {user}")
            print("------------------------------")

        processed += 1

        print(f"\n[{processed}/{total_images}]")

        print(img_path)

        img = load_image(img_path)

        if img is None:

            skipped += 1

            continue

        # ================= FACE DETECTION =================
        face = mtcnn(img)

        if face is None:

            print("⚠️ Skip (No face detected)")

            skipped += 1

            continue

        # ================= EMBEDDING =================
        try:

            emb = (
                model(
                    face
                    .unsqueeze(0)
                    .to(device)
                )
                .detach()
                .cpu()
                .numpy()[0]
            )

            embeddings.append(emb)

            names.append(user)

            success += 1

            print("✅ Embedding extracted")

        except Exception as e:

            print("❌ Embedding failed")
            print(e)

            skipped += 1

    # ================= SAVE =================
    embeddings = np.array(embeddings)

    with open(OUTPUT_FILE, "wb") as f:

        pickle.dump(
            (
                embeddings,
                names
            ),
            f
        )

    # ================= SUMMARY =================
    print("\n==============================")
    print(" Training Finished")
    print("==============================")

    print(f"📦 Total Images : {total_images}")
    print(f"✅ Success      : {success}")
    print(f"⚠️ Skipped      : {skipped}")
    print(f"🧠 Embeddings   : {len(embeddings)}")

    print(f"\n💾 Saved to:")
    print(OUTPUT_FILE)

    print("==============================")


# ================= ENTRY =================
if __name__ == "__main__":
    train_embeddings()
