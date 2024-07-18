# KidPicsSorter

## 應用說明
你想要開發一個應用來分類相簿中的小朋友照片，依據每個小朋友的名字將照片歸類到相應的資料夾中。如果一張照片中出現了多個小朋友的臉，這張照片會被複製並放入每個相關小朋友的資料夾。

## 使用 InsightFace 進行人臉辨識

### 模型訓練
InsightFace 提供的預訓練模型已經具備很強的人臉辨識能力，你不需要再重新訓練模型。你只需要準備每個小朋友的幾張樣本照片，用於建立他們的特徵向量。

## 準備工作

- 準備每個小朋友的幾張樣本照片（例如，每人5-10張），這些照片會用來生成每個小朋友的特徵向量。
- 安裝所需的 Python 庫，包括 InsightFace 和 OpenCV。

## 注意事項

- **樣本照片**：確保每個小朋友的樣本照片清晰且多樣，以提高辨識的準確度。
- **依賴庫**：安裝所需的 Python 庫：
`pip install insightface opencv-python numpy`
- **特徵向量閾值**：`threshold` 值可以根據實際情況調整，以平衡辨識的精度與召回率。


## 架構設計

### iOS App 前端
- 負責用戶交互，提供照片選擇、標註、分類等功能。
- 使用 Swift 或 SwiftUI 進行開發。
- 通過 RESTful API 與後端進行通信。

### 後端服務
- 使用 Python 開發，主要處理照片上傳、特徵向量生成、人臉識別與分類等功能。
- 部署在雲端（如 AWS、GCP）或本地服務器上。
- 使用 Flask 或 FastAPI 搭建 RESTful API。

### 數據存儲
- 使用 Google Photos API 進行相片存儲與管理。
- 使用資料庫（如 PostgreSQL 或 MySQL）存儲用戶信息、照片標籤等元數據。

## 詳細步驟

### iOS App 開發
1. 權限請求
- 請求存取相簿的權限。
- 請求 Google Photos 授權，使用 OAuth 進行用戶認證與授權。

2. 照片選擇與標註
- 使用 UIImagePickerController 或 PHPickerViewController 選擇照片。
- 提供照片標註界面，讓用戶輸入每個小朋友的名字。

3. 照片上傳
- 將選擇並標註好的照片上傳至後端。
- 使用 Multipart Form Data 進行照片上傳。

4. 分類結果顯示
- 從後端獲取分類結果，顯示給用戶。

### 後端開發
1. API 設計
- 設計 RESTful API，提供照片上傳、特徵向量生成、人臉識別與分類等功能。
- 使用 Flask 或 FastAPI 實現 API。

2. 特徵向量生成
- 使用 InsightFace 提取上傳照片的人臉特徵向量。

3. 人臉識別與分類
- 對上傳的照片進行人臉識別，並將照片分類到對應的小朋友資料夾。
- 使用 Google Photos API 創建並管理相簿。

4. 數據存儲與管理
- 使用資料庫存儲用戶信息、照片標籤等元數據。

## 核心代碼示例

```swift
import UIKit
import Photos
import GoogleSignIn

class PhotoPickerViewController: UIViewController, UIImagePickerControllerDelegate, UINavigationControllerDelegate {

    func pickPhoto() {
        let picker = UIImagePickerController()
        picker.delegate = self
        picker.sourceType = .photoLibrary
        present(picker, animated: true, completion: nil)
    }

    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        if let image = info[.originalImage] as? UIImage {
            // Handle image selection
        }
        picker.dismiss(animated: true, completion: nil)
    }

    func uploadPhoto(image: UIImage, childName: String) {
        // Convert image to Data
        guard let imageData = image.jpegData(compressionQuality: 0.8) else { return }
        
        // Prepare the URL request
        let url = URL(string: "http://your-backend-api/upload")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // Prepare the body data
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        var body = Data()
        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"childName\"\r\n\r\n")
        body.append("\(childName)\r\n")
        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"photo.jpg\"\r\n")
        body.append("Content-Type: image/jpeg\r\n\r\n")
        body.append(imageData)
        body.append("\r\n")
        body.append("--\(boundary)--\r\n")
        request.httpBody = body
        
        // Send the request
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error: \(error)")
                return
            }
            print("Upload success")
        }.resume()
    }
}
```

```python
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import insightface

app = Flask(__name__)
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id=0, det_size=(640, 640))

UPLOAD_FOLDER = '/path/to/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        child_name = request.form['childName']
        
        # Process the image and extract features
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img = insightface.app.common.imread(img_path)
        faces = model.get(img)
        for face in faces:
            print(face.normed_embedding)
        
        # Save to Google Photos or classify into folders
        # Your classification and Google Photos code here
        
        return "File uploaded and processed", 200

if __name__ == '__main__':
    app.run(debug=True)

```

## 部屬與運行
1. 後端服務部署
- 將後端服務部署在雲端服務器上，確保有足夠的計算資源進行人臉識別和分類。
- 配置域名與 SSL 證書，確保 API 的安全性。

2. iOS App 上架
- 確保 App 符合 App Store 的規範與要求，完成測試後上架。
- 提供詳細的使用說明，指導用戶進行照片選擇、標註與分類。