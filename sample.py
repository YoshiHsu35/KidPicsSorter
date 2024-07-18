import os
import cv2
import insightface
from insightface.app import FaceAnalysis
import shutil

# 初始化 InsightFace
app = FaceAnalysis()
app.prepare(ctx_id=0, det_size=(640, 640))

# 載入小朋友的樣本照片並生成特徵向量
def load_known_faces(known_faces_dir):
    known_faces = {}
    for child_name in os.listdir(known_faces_dir):
        child_dir = os.path.join(known_faces_dir, child_name)
        if os.path.isdir(child_dir):
            embeddings = []
            for img_name in os.listdir(child_dir):
                img_path = os.path.join(child_dir, img_name)
                img = cv2.imread(img_path)
                faces = app.get(img)
                if faces:
                    embeddings.append(faces[0].embedding)
            if embeddings:
                known_faces[child_name] = np.mean(embeddings, axis=0)
    return known_faces

# 比對臉部特徵向量
def recognize_faces(img, known_faces, threshold=0.6):
    faces = app.get(img)
    recognized_faces = []
    for face in faces:
        embedding = face.embedding
        for name, known_embedding in known_faces.items():
            dist = np.linalg.norm(embedding - known_embedding)
            if dist < threshold:
                recognized_faces.append(name)
    return recognized_faces

# 主程式
def classify_photos(input_dir, output_dir, known_faces_dir):
    known_faces = load_known_faces(known_faces_dir)
    for img_name in os.listdir(input_dir):
        img_path = os.path.join(input_dir, img_name)
        img = cv2.imread(img_path)
        recognized_faces = recognize_faces(img, known_faces)
        for name in recognized_faces:
            child_dir = os.path.join(output_dir, name)
            os.makedirs(child_dir, exist_ok=True)
            shutil.copy(img_path, child_dir)

# 目錄設定
input_dir = "path/to/your/photo/album"
output_dir = "path/to/output/folders"
known_faces_dir = "path/to/known/faces"

# 開始分類
classify_photos(input_dir, output_dir, known_faces_dir)
