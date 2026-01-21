# #backend code

# from flask import Flask, request, jsonify
# import sqlite3
# import cv2
# import os

# app = Flask(__name__)

# # Paths
# DATASET_DIR = "dataset"
# CASCADE_PATH = "../haarcascade_frontalface_default.xml"

# # Ensure dataset folder exists
# os.makedirs(DATASET_DIR, exist_ok=True)

# # Load Haar Cascade
# face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

# @app.route("/add_person", methods=["POST"])
# def add_person():
#     name = request.form.get("name")
#     relation = request.form.get("relation")
#     image = request.files.get("image")

#     if not name or not relation or not image:
#         return jsonify({"error": "name, relation, and image are required"}), 400

#     # Save person to DB
#     conn = sqlite3.connect("faces.db")
#     c = conn.cursor()
#     c.execute(
#         "INSERT INTO known_people (name, relation) VALUES (?, ?)",
#         (name, relation)
#     )
#     person_id = c.lastrowid
#     conn.commit()
#     conn.close()

#     # Create folder for this person
#     person_dir = os.path.join(DATASET_DIR, f"person_{person_id}")
#     os.makedirs(person_dir, exist_ok=True)

#     # Save uploaded image
#     img_path = os.path.join(person_dir, "1.jpg")
#     image.save(img_path)

#     # Verify face exists in image
#     img = cv2.imread(img_path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#     if len(faces) == 0:
#         # No face found → cleanup
#         os.remove(img_path)
#         os.rmdir(person_dir)
#         return jsonify({"error": "No face detected in image"}), 400

#     return jsonify({
#         "message": "Person added successfully with face image",
#         "person_id": person_id
#     }), 201

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_PATH = "faces.db"
DATASET_DIR = "dataset"

os.makedirs(DATASET_DIR, exist_ok=True)

@app.route("/add_person", methods=["POST"])
def add_person():
    name = request.form.get("name")
    relation = request.form.get("relation")
    image = request.files.get("image")

    if not name or not relation or not image:
        return jsonify({"error": "name, relation, and image are required"}), 400

    # Insert into DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO known_people (name, relation) VALUES (?, ?)",
        (name, relation)
    )
    person_id = c.lastrowid
    conn.commit()
    conn.close()

    # Create dataset folder
    person_dir = os.path.join(DATASET_DIR, f"person_{person_id}")
    os.makedirs(person_dir, exist_ok=True)

    # Save image
    img_path = os.path.join(person_dir, "1.jpg")
    image.save(img_path)

    return jsonify({
        "message": "Person added successfully",
        "person_id": person_id
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
