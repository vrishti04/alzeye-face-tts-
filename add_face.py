# import requests
# import os

# BACKEND_URL = "http://127.0.0.1:5000/add_person"

# def add_face():
#     print("=== Add a New Person to Smart Glasses ===")
#     print("Make sure backend is running: python backend/app.py\n")

#     # 1. Take name
#     name = input("Enter Name (e.g., Alice): ").strip()
#     if not name:
#         print("❌ Name is required.")
#         return

#     # 2. Take relation
#     relation = input("Enter Relation (e.g., Daughter, Son): ").strip()
#     if not relation:
#         print("❌ Relation is required.")
#         return

#     # 3. Take image path
#     image_path = input(
#         "Enter ABSOLUTE path to face image (e.g., C:/Users/hp/Desktop/face.jpg): "
#     ).strip().replace('"', '')

#     if not os.path.exists(image_path):
#         print(f"❌ Image not found at: {image_path}")
#         return

#     print("\nUploading data to backend...")

#     try:
#         with open(image_path, "rb") as img:
#             files = {"image": img}
#             data = {
#                 "name": name,
#                 "relation": relation
#             }

#             response = requests.post(BACKEND_URL, data=data, files=files)

#         if response.status_code == 201:
#             print("\n✅ SUCCESS!")
#             print(response.json())
#         else:
#             print("\n❌ FAILED")
#             print("Status Code:", response.status_code)
#             print("Response:", response.text)

#     except requests.exceptions.ConnectionError:
#         print("\n❌ ERROR: Cannot connect to backend.")
#         print("Is backend running?")
#     except Exception as e:
#         print("\n❌ Unexpected error:", e)

# if __name__ == "__main__":
#     add_face()


import os
import shutil
import sqlite3

DB_PATH = "backend/faces.db"
DATASET_DIR = "backend/dataset"


def add_person():
    print("\n=== Add Person to ALZEYE ===")

    name = input("Enter name: ").strip()
    relation = input("Enter relation: ").strip()
    image_path = input("Enter image path: ").strip().replace('"', '')

    if not name or not relation or not image_path:
        print("❌ All fields are required")
        return

    if not os.path.exists(image_path):
        print("❌ Image file not found")
        return

    # ---- Insert into DB ----
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO known_people (name, relation) VALUES (?, ?)",
        (name, relation)
    )
    person_id = cur.lastrowid
    conn.commit()
    conn.close()

    # ---- Create dataset folder ----
    person_dir = os.path.join(DATASET_DIR, f"person_{person_id}")
    os.makedirs(person_dir, exist_ok=True)

    # ---- Save image as 1.jpg ----
    dest_image = os.path.join(person_dir, "1.jpg")
    shutil.copy(image_path, dest_image)

    print(f"\n✅ Person added successfully")
    print(f"ID       : {person_id}")
    print(f"Name     : {name}")
    print(f"Relation : {relation}")
    print(f"Image    : {dest_image}")


def add_more_images():
    person_id = input("\nEnter person ID to add more images: ").strip()

    person_dir = os.path.join(DATASET_DIR, f"person_{person_id}")
    if not os.path.exists(person_dir):
        print("❌ Person folder not found")
        return

    images = sorted(
        [f for f in os.listdir(person_dir) if f.endswith(".jpg")],
        key=lambda x: int(x.split(".")[0])
    )

    next_index = len(images) + 1

    image_path = input("Enter new image path: ").strip().replace('"', '')
    if not os.path.exists(image_path):
        print("❌ Image file not found")
        return

    dest = os.path.join(person_dir, f"{next_index}.jpg")
    shutil.copy(image_path, dest)

    print(f"✅ Image added as {next_index}.jpg")


# ---------------- MAIN ----------------

print("\n1. Add new person")
print("2. Add more images to existing person")

choice = input("Choose option (1/2): ").strip()

if choice == "1":
    add_person()
elif choice == "2":
    add_more_images()
else:
    print("❌ Invalid option")
