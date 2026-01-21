# import cv2
# import os
# import sqlite3
# import numpy as np
# import pyttsx3

# # ------------------ INITIAL SETUP ------------------

# CASCADE_PATH = "../haarcascade_frontalface_default.xml"
# DATASET_DIR = "../backend/dataset"
# DB_PATH = "../backend/faces.db"

# engine = pyttsx3.init()
# engine.setProperty("rate", 150)

# face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
# recognizer = cv2.face.LBPHFaceRecognizer_create()

# # ------------------ LOAD DATA FROM DB ------------------

# conn = sqlite3.connect(DB_PATH)
# cursor = conn.cursor()
# cursor.execute("SELECT id, name, relation FROM known_people")
# people = cursor.fetchall()
# conn.close()

# if len(people) == 0:
#     print("❌ No people found in database")
#     exit()

# faces = []
# labels = []
# label_map = {}

# for person_id, name, relation in people:
#     img_path = os.path.join(DATASET_DIR, f"person_{person_id}", "1.jpg")
#     if os.path.exists(img_path):
#         img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
#         faces.append(img)
#         labels.append(person_id)
#         label_map[person_id] = (name, relation)

# recognizer.train(faces, np.array(labels))

# print("✅ Face recognizer trained")

# # ------------------ LIVE CAMERA LOOP ------------------

# cap = cv2.VideoCapture(0)
# spoken_ids = set()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     detected_faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#     for (x, y, w, h) in detected_faces:
#         roi = gray[y:y+h, x:x+w]

#         try:
#             label, confidence = recognizer.predict(roi)
#         except:
#             continue

#         THRESHOLD = 80

#         if confidence < THRESHOLD:
#             name, relation = label_map[label]
#             text = f"This is {name}, your {relation}"

#             # Speak only once per person
#             if label not in spoken_ids:
#                 print(text)
#                 engine.say(text)
#                 engine.runAndWait()
#                 spoken_ids.add(label)

#             cv2.putText(
#                 frame,
#                 f"{name} ",
#                 (x, y - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (0, 255, 0),
#                 2
#             )
#         else:
#             cv2.putText(
#                 frame,
#                 "Unknown",
#                 (x, y - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (0, 0, 255),
#                 2
#             )

#         cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

#     cv2.imshow("Smart Glasses Live Feed", frame)

#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break


# cap.release()
# cv2.destroyAllWindows()


import cv2
import os
import sqlite3
import numpy as np
import face_recognition
import pyttsx3

# ---------------- CONFIG ----------------

DATASET_DIR = "../backend/dataset"
DB_PATH = "../backend/faces.db"
RECOGNITION_THRESHOLD = 0.45   # lower = stricter
TTS_RATE = 150

# ---------------- TTS ----------------

engine = pyttsx3.init()
engine.setProperty("rate", TTS_RATE)

# ---------------- LOAD PEOPLE FROM DB ----------------

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT id, name, relation FROM known_people")
people = cur.fetchall()
conn.close()

if not people:
    print("❌ No people found in database")
    exit()

# ---------------- LOAD DATASET & ENCODINGS ----------------

known_encodings = []
known_ids = []
id_to_info = {}

print("🔄 Loading known faces...")

for person_id, name, relation in people:
    person_dir = os.path.join(DATASET_DIR, f"person_{person_id}")
    if not os.path.isdir(person_dir):
        continue

    for img_file in os.listdir(person_dir):
        img_path = os.path.join(person_dir, img_file)

        image = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(image)

        if encodings:
            known_encodings.append(encodings[0])
            known_ids.append(person_id)
            id_to_info[person_id] = (name, relation)

print(f"✅ Loaded {len(known_encodings)} face samples")

if len(known_encodings) == 0:
    print("❌ No valid face encodings found")
    exit()

# ---------------- LIVE CAMERA ----------------

cap = cv2.VideoCapture(0)
spoken_ids = set()

print("🎥 Camera started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    for (top, right, bottom, left), face_enc in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_encodings, face_enc)

        best_match_index = np.argmin(distances)
        best_distance = distances[best_match_index]

        if best_distance < RECOGNITION_THRESHOLD:
            person_id = known_ids[best_match_index]
            name, relation = id_to_info[person_id]
            label = f"{name} ({relation})"

            if person_id not in spoken_ids:
                engine.say(f"This is {name}, your {relation}")
                engine.runAndWait()
                spoken_ids.add(person_id)

            color = (0, 255, 0)
        else:
            label = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(
            frame,
            label,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    cv2.imshow("ALZEYE – Smart Glasses Live Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

