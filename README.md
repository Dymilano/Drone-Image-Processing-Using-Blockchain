# Drone-Image-Processing-Using-Blockchain
Drone-Image-Processing-Using-Blockchain

📡 ỨNG DỤNG BLOCKCHAIN PHÁT HIỆN, NHẬN DIỆN, ĐẾM NGƯỜI TRONG KHU VỰC BẰNG DRONE
📌 Giới thiệu chung
Dự án kết hợp công nghệ Drone, trí tuệ nhân tạo (YOLOv8) và Blockchain để phát hiện, nhận diện, đếm số lượng người trong khu vực được giám sát. Kết quả AI (số người, phần trăm, thời gian, vị trí GPS) được ghi lại trên blockchain Ethereum testnet nhằm đảm bảo tính bất biến, minh bạch và xác minh được.

🔒 Mọi kết quả đếm người đều được xác thực bằng hợp đồng thông minh trên Ethereum.

🧭 Sơ đồ hệ thống và chức năng
mermaid
Sao chép
Chỉnh sửa
graph TD
    A[Drone gắn ESP32-CAM] -->|Chụp ảnh/video| B[ESP32 WiFi]
    B -->|Truyền dữ liệu TCP| C[Laptop chạy YOLOv8]
    C -->|Phân tích AI YOLOv8| D[Web Flask Dashboard]
    D -->|Gửi kết quả JSON| E[Smart Contract trên Blockchain]
🔧 Chức năng chính:
📷 Drone thu ảnh/video từ trên cao

🧠 AI YOLOv8 xử lý ảnh → phát hiện và đếm người

📈 Tính phần trăm có người trên khung hình

⏱ Ghi nhận thời gian phân tích

🌐 Giao diện web Flask để tải video, chụp ảnh, xem kết quả

🔗 Ghi dữ liệu lên Blockchain Ethereum testnet

⚙️ Công nghệ sử dụng
Thành phần	Công nghệ
Phần cứng	Drone F450, ESC 30A, động cơ 1000KV, GPS M1018C, ESP32-CAM, ESP32 WiFi, mạch bay F405
AI & xử lý ảnh	Python, YOLOv8 (Ultralytics), OpenCV, NumPy
Web server	Flask, HTML5, Bootstrap, Chart.js
Blockchain	Solidity, Remix IDE, Sepolia Ethereum Testnet, Web3.py
Truyền dữ liệu	TCP Socket ESP32 ↔ Laptop

🧪 Hướng dẫn cài đặt & chạy
1. Cài đặt AI trên laptop
bash
Sao chép
Chỉnh sửa
git clone https://github.com/<your-username>/drone-image-blockchain.git
cd flask_app
pip install -r requirements.txt
2. Chạy web Flask và YOLOv8
bash
Sao chép
Chỉnh sửa
python app.py
Vào http://localhost:5000

Chọn: "Tải video lên", "Phân tích ảnh", hoặc "Xem kết quả"

Kết quả sẽ được lưu vào blockchain khi nhấn Gửi lên blockchain

3. Cấu hình hợp đồng thông minh (Remix IDE)
Tải file PeopleCounter.sol trong thư mục blockchain/

Deploy trên Remix với testnet Sepolia

Copy địa chỉ contract vào Flask (config.py) để kết nối

🖼 Giao diện (Bạn tự thêm hình)
Livestream từ drone

Phân tích video và chụp ảnh

Biểu đồ số người & phần trăm

Lịch sử phân tích + liên kết blockchain

📁 Cấu trúc thư mục
csharp
Sao chép
Chỉnh sửa
drone-image-processing-using-blockchain/
├── esp32_cam/                # Mã ESP32-CAM
├── esp32_wifi/               # Mã ESP32 WiFi truyền ảnh và GPS
├── flask_app/                # Flask web + YOLOv8
│   ├── app.py
│   └── templates/, static/
├── blockchain/
│   └── PeopleCounter.sol     # Hợp đồng thông minh
├── models/
│   └── best.pt               # Mô hình YOLOv8
├── README.md
✅ Kết quả đạt được
Nhận diện chính xác người từ ảnh/video drone ở độ cao 10–20m

Phân tích được cả trong điều kiện ánh sáng yếu

Kết quả được ghi lại trên Blockchain, không thể thay đổi

Giao diện dễ sử dụng, phù hợp mở rộng thương mại hóa

📚 Tài liệu tham khảo
YOLOv8: https://docs.ultralytics.com

Blockchain Remix IDE: https://remix.ethereum.org

Web3.py: https://web3py.readthedocs.io

Drone ESP32-CAM: https://randomnerdtutorials.com
