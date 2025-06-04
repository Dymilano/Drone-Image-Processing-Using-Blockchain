![image](https://github.com/user-attachments/assets/3a839658-edf4-4284-ae42-f8cc9ba1c0fb)


#

📡 BLOCKCHAIN ​​APPLICATION TO DETECTING, IDENTIFYING, COUNTING PEOPLE IN AREA BY DRONE
----------------------------------------------------------------------------------


📡 ỨNG DỤNG BLOCKCHAIN PHÁT HIỆN, NHẬN DIỆN, ĐẾM NGƯỜI TRONG KHU VỰC BẰNG DRONE  
🔍 Giới thiệu  
Dự án là một hệ thống tích hợp giữa Drone, AI (YOLOv8) và công nghệ Blockchain, nhằm giám sát khu vực từ trên cao, nhận diện và đếm số lượng người, sau đó ghi kết quả lên Blockchain để đảm bảo minh bạch, không thể chỉnh sửa.  
#
Hệ thống bao gồm:    
Drone: quay video từ trên cao, truyền về máy tính.  

YOLOv8 (AI): xử lý ảnh/video để nhận diện và đếm người.  

Flask Web App: giao diện cho phép tải video/livestream, xem kết quả phân tích.  

Blockchain (Ethereum Smart Contract): lưu trữ kết quả đếm người (số lượng, % nhận diện, thời gian, hash ảnh/video).  

#
🧠 Công nghệ sử dụng  

Drone: ESP32-CAM, F405 flight controller, GPS M1018C.  

AI: YOLOv8 (Ultralytics), Python, OpenCV, Flask.  

Blockchain: Solidity Smart Contract, Remix IDE, Ethereum Testnet (Sepolia).  

Giao tiếp: TCP/IP giữa ESP32 WiFi và laptop.  

#
⚙️ Chức năng chính  

✅ Nhận diện người trong ảnh hoặc video từ drone.  

✅ Đếm số lượng người trong mỗi khung hình.  

✅ Tính phần trăm người xuất hiện trong vùng quan sát.  
 
✅ Ghi lại kết quả (số người, % nhận diện, timestamp, hash ảnh/video) lên Blockchain.  

✅ Hiển thị kết quả trực quan trên giao diện Flask Web.  

✅ Cho phép sử dụng video tải lên hoặc livestream từ điện thoại qua RTMP (Larix).  

#
🖥️ Giao diện web Flask  

 Phân tích ảnh hoặc video.  
 
 Livestream từ điện thoại qua RTMP (Larix).  
 
 Nút chụp ảnh từ livestream.  
 
 Hiển thị kết quả AI.  
 
 Tự động ghi dữ liệu lên Blockchain.  
 
#
🧪 Mục tiêu thực nghiệm  

Phát hiện và đếm người trong khu vực quan sát từ độ cao 10–20m.  

Phân tích độ chính xác nhận diện trong điều kiện ánh sáng khác nhau.  

Ghi nhận kết quả, thời gian, hash video lên Ethereum blockchain.  

#
📦 Cấu trúc dự án  

bash  

Sao chép  

Chỉnh sửa  

📂 droneviewpeoplecounteryolov8/  

├── app.py              # Web Flask  

├── main.py             # Phân tích video YOLOv8  

├── tracker.py          # Theo dõi đối tượng  

├── static/             # Frontend assets  

├── templates/          # HTML giao diện  

├── contracts/          # Smart contract (Solidity)  

├── uploads/            # Ảnh/video đầu vào  

└── README.md           # (file này)  
#
🛠️ Công nghệ và kỹ thuật sử dụng  

#
🧱 Phần cứng:  
| Thành phần                                    | Mô tả chức năng                                                                      |
| --------------------------------------------- | ------------------------------------------------------------------------------------ |
| **ESP32-CAM**                                 | Module tích hợp camera OV2640, gắn lên drone để chụp ảnh hoặc quay video từ trên cao |
| **ESP32 WiFi**                                | Nhận ảnh từ ESP32-CAM qua UART hoặc TCP, sau đó truyền về laptop qua mạng WiFi       |
| **F405 Flight Controller**                    | Điều khiển drone, truyền dữ liệu GPS, độ cao, khoảng cách cho ESP32 WiFi             |
| **GPS M1018C**                                | Cung cấp tọa độ vị trí thực tế cho kết quả AI                                        |
| **Drone Kit F450**                            | Khung máy bay với 4 động cơ không chổi than 1000KV, ESC 30A, pin LiPo 3S/4S          |
| **Điện thoại + Larix Broadcaster** (tuỳ chọn) | Truyền livestream video từ drone về Flask Web App qua RTMP                           |

#
🧠 Phần mềm:  

| Thành phần               | Mục đích sử dụng                                                                          |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| **YOLOv8 (Ultralytics)** | Mô hình AI học sâu dùng để phát hiện và đếm người trong ảnh/video từ drone                |
| **Python**               | Ngôn ngữ chính điều khiển xử lý ảnh, socket TCP, web backend và kết nối blockchain        |
| **OpenCV**               | Thư viện xử lý ảnh: đọc ảnh, hiển thị, annotate kết quả (bounding box, nhãn người)        |
| **Flask**                | Web framework nhẹ dùng để xây dựng giao diện người dùng, upload video, nhận ảnh từ stream |
| **Chart.js**             | Hiển thị biểu đồ số lượng người, phần trăm nhận diện, theo thời gian                      |
| **web3.py**              | Thư viện Python kết nối với Ethereum Blockchain và gọi Smart Contract                     |
| **ffmpeg / RTMP**        | Hỗ trợ streaming video từ điện thoại (hoặc camera IP) về server Flask                     |
| **Remix IDE**            | IDE dùng để viết, biên dịch và triển khai Smart Contract trên Ethereum testnet (Sepolia)  |
| **Solidity**             | Ngôn ngữ dùng để viết hợp đồng thông minh (Smart Contract) lưu dữ liệu AI lên blockchain  |

#
Blockchain  
| Thành phần                   | Mô tả                                                                                                          |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Ethereum Sepolia Testnet** | Mạng blockchain thử nghiệm dùng để lưu kết quả phân tích AI (số người, thời gian, % nhận diện, hash ảnh/video) |
| **Smart Contract Solidity**  | Hợp đồng thông minh được viết để ghi dữ liệu phân tích, đảm bảo minh bạch và không chỉnh sửa                   |
| **Dữ liệu ghi lại**          | Timestamp, số người, phần trăm nhận diện, kiểu dữ liệu (ảnh/video), mã hash ảnh/video (SHA256/IPFS tùy chọn)   |



#
Sơ đồ hệ thống  

![image](https://github.com/user-attachments/assets/0e0c2e92-94e6-4b6c-b470-b5cb6bbdac81)

#
Thư viện đã sử dụng   trong dự án của:  
- Smart Contract (Solidity):    
+ Solidity phiên bản ^0.8.0    
+ Contract PeopleCounter.sol để lưu trữ và quản lý dữ liệu phân tích  
- Python Libraries:  
+ flask: Framework web để xây dựng API và giao diện web  
+ opencv-python: Xử lý hình ảnh và video  
+ ultralytics: Thư viện YOLOv8 cho việc phát hiện đối tượng  
+ pandas: Xử lý và phân tích dữ liệu  
+ numpy: Tính toán số học và xử lý mảng  
+ cvzone: Thư viện hỗ trợ xử lý hình ảnh và video  
+ web3: Tương tác với blockchain Ethereum  
+ eth-account: Quản lý tài khoản Ethereum  
- Các file và tài nguyên khác:  
+ yolov8s.pt: Model YOLOv8 đã được train  
+ coco.txt: File chứa các class labels cho model  
+ Các file Python chính:  
+ app.py: File chính của ứng dụng Flask  
+ blockchain.py: Xử lý tương tác với blockchain  
+ tracker.py: Theo dõi và đếm người  
+ main.py: File khởi động chính  
- Cấu trúc thư mục:  
+ templates/: Chứa các file template HTML  
+ static/: Chứa các file tĩnh (CSS, JS, images)  
+ contracts/: Chứa các smart contract  
+ .venv/: Môi trường ảo Python  

#
GIAO DIỆN
![image](https://github.com/user-attachments/assets/eddb8bac-453f-4d6a-b762-10f3a614fe1e)
![image](https://github.com/user-attachments/assets/c8d1d452-8054-4a29-a54e-b1243d1e6a53)
![image](https://github.com/user-attachments/assets/0918d658-9094-4f38-8e63-85dfab2b9377)
![image](https://github.com/user-attachments/assets/36bbb0a7-84f9-44d1-893f-567225462ac1)
![image](https://github.com/user-attachments/assets/2deeae2c-bc17-4583-9fa1-5bebf700ec49)
![image](https://github.com/user-attachments/assets/d73f61b4-2bda-4e79-ab99-2a8b0513697a)
![image](https://github.com/user-attachments/assets/8d50c6ed-56f3-4166-9919-335282130be7)



#
📈 Kết quả  

Hệ thống đã được thử nghiệm ngoài thực tế, cho phép nhận diện chính xác người trong video drone quay từ trên cao, và xác thực kết quả qua Ethereum blockchain.  
