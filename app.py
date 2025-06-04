from flask import Flask, render_template, Response, request, redirect, url_for, send_from_directory, jsonify, send_file
import cv2
import os
from datetime import datetime
import time
import json
from ultralytics import YOLO
import pandas as pd
import numpy as np
import hashlib
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['CAPTURE_FOLDER'] = 'static/captures'

HISTORY_FILE = 'history.json'

# Dictionary tạm để lưu kết quả phân tích video sau khi stream xong
vide_analysis_results_cache = {}

# Biến toàn cục để quản lý ghi video
recording = False
video_writer = None
recorded_frames = []

def save_history(entry):
    try:
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = []
    # Giới hạn số lượng lịch sử để tránh file quá lớn
    if len(data) >= 50:
        data = data[1:] # Giữ lại 49 entry cuối
    data.append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_history():
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Trang chủ: chọn nguồn dữ liệu
@app.route('/')
def index():
    return render_template('index.html')

# Livestream camera (cam_id: 0, 1, ...)
@app.route('/video_feed/<int:cam_id>')
def video_feed(cam_id):
    def gen():
        cap = cv2.VideoCapture(cam_id)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        cap.release()
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Chụp ảnh từ camera
@app.route('/capture/<int:cam_id>')
def capture(cam_id):
    cap = cv2.VideoCapture(cam_id)
    ret, frame = cap.read()
    if ret:
        filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '.jpg'
        filepath = os.path.join(app.config['CAPTURE_FOLDER'], filename)
        try:
            cv2.imwrite(filepath, frame)
             # Redirect sang analyze_image để phân tích ngay sau khi chụp
            return redirect(url_for('analyze_image', filename=filename))
        except Exception as e:
            print(f"Error saving captured image: {e}")
            return "Error saving captured image", 500
    cap.release()
    return 'Capture failed', 500

# Upload video
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filename = datetime.now().strftime('%Y%m%d_%H%M%S_') + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            # Redirect sang trang view_analyzed_video để xem stream
            return redirect(url_for('view_analyzed_video', filename=filename))
        except Exception as e:
            print(f"Error saving uploaded video: {e}")
            return "Error uploading video", 500
    return redirect(url_for('index'))

# Route để hiển thị stream video đang phân tích và kết quả sau
@app.route('/view_analyzed_video/<filename>')
def view_analyzed_video(filename):
    history_data = load_history()
    # Lấy kết quả phân tích từ history.json dựa vào filename
    # Không cần kiểm tra kết quả cuối cùng ở đây nữa, vì analyze.html sẽ hiển thị kết quả cuối
    # Trang này chỉ đơn thuần hiển thị stream và lịch sử
    return render_template('view_analyzed_video.html', filename=filename, history=history_data)

# Route để stream video đang phân tích
@app.route('/analyzed_video_feed/<filename>')
def analyzed_video_feed(filename):
    def gen_analyzed_video(filename):
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cap = cv2.VideoCapture(video_path)
        # Kiểm tra file video tồn tại
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return

        model = YOLO('yolov8s.pt') # Load model ở đây
        class_list = []
        with open('coco.txt', 'r') as f:
            class_list = f.read().splitlines()

        frame_count = 0
        people_counts = [] # Để tính avg và max
        percent_levels = [10, 20, 30, 40, 50, 70, 90, 100]
        max_people = 0
        start_time = time.time() # Import time
        boxed_image_url = None # Lưu URL frame đầu tiên có box
        boxed_image_path_full = None # Lưu đường dẫn full để kiểm tra tồn tại

        while True:
            try:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1

                # Thực hiện phân tích và vẽ bounding box
                results = model.predict(frame, verbose=False)
                a = results[0].boxes.data
                px = pd.DataFrame(a).astype("float")
                count = 0
                for index, row in px.iterrows():
                    d = int(row[5])
                    c = class_list[d]
                    if 'person' in c:
                        count += 1
                        x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(frame, str(c), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

                people_counts.append(count)
                if count > max_people:
                    max_people = count

                # Lưu frame đầu tiên có box và tạo URL
                if frame_count == 1:
                     boxed_image_path_relative = f'uploads/{os.path.splitext(filename)[0]}_boxed.jpg'
                     boxed_image_path_full = os.path.join(app.config['UPLOAD_FOLDER'], os.path.splitext(filename)[0] + '_boxed.jpg')
                     try:
                         cv2.imwrite(boxed_image_path_full, frame)
                         boxed_image_url = url_for('static', filename=boxed_image_path_relative)
                         boxed_image_url = boxed_image_url.replace('\\', '/')
                         print(f"Successfully saved first boxed frame for {filename} at {boxed_image_path_full}")
                     except Exception as e:
                         print(f"Error saving boxed image frame: {e}")
                         boxed_image_url = None

                # Mã hóa frame đã xử lý và yield
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                print(f"Error processing video frame for {filename}: {e}")
                # Có thể thêm logic để dừng stream hoặc hiển thị lỗi trên frontend
                break # Thoát khỏi vòng lặp nếu có lỗi

        # ---- Sau khi stream xong, tính toán kết quả cuối cùng và lưu ----
        print(f"Video processing finished for {filename}. Calculating final results...")
        cap.release()
        end_time = time.time()
        duration = end_time - start_time
        # Import numpy mean
        avg_people = np.mean(people_counts) if people_counts else 0
        # Tính phần trăm cho từng mức (dựa trên max_people)
        percent_results = [int(100 * max_people / lvl) if lvl > 0 else 0 for lvl in percent_levels]
        percent_results = [min(100, p) for p in percent_results]
        # Tính hash file
        import hashlib
        video_path_full = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_hash = '' # Default empty hash
        try:
            with open(video_path_full, 'rb') as f:
                 file_hash = hashlib.sha256(f.read()).hexdigest()
            print(f"Successfully calculated hash for {filename}")
        except Exception as e:
             print(f"Error calculating file hash for {filename}: {e}")

        # Chuẩn bị kết quả cuối cùng
        final_result = {
             'filename': filename,
             'max_people': int(max_people),
             'avg_people': float(avg_people),
             'frame_count': frame_count,
             'duration': duration,
             'percent_levels': percent_levels,
             'percent_results': percent_results,
             'people_counts': people_counts, # Lưu cả list count để vẽ biểu đồ
             'file_hash': file_hash,
             'boxed_image': boxed_image_url, # URL ảnh box đầu tiên
         }

        # Lưu kết quả cuối cùng vào cache tạm
        global vide_analysis_results_cache
        vide_analysis_results_cache[filename] = final_result
        print(f"Final analysis results cached for {filename}")

        # Cập nhật history.json với kết quả cuối cùng
        history_data = load_history()
        found_entry = None
        for entry in history_data:
            if entry.get('filename') == filename and entry.get('type') == 'video':
                found_entry = entry
                break

        if found_entry:
             # Cập nhật entry đã tìm thấy
             found_entry.update(final_result) # Cập nhật tất cả từ final_result
             print(f"Updated history entry for {filename}")
        else:
            # Nếu không tìm thấy entry (trường hợp khẩn cấp), tạo mới và thêm link view
             new_entry = final_result
             new_entry['type'] = 'video'
             new_entry['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
             new_entry['link'] = url_for('view_analyzed_video', filename=filename)
             save_history(new_entry) # save_history đã thêm logic append và giới hạn size
             print(f"Created new history entry for {filename}")

        print(f"Finished calculating and saving results for {filename}")

    return Response(gen_analyzed_video(filename), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route API để lấy kết quả phân tích video cuối cùng
@app.route('/get_video_analysis_results/<filename>')
def get_video_analysis_results(filename):
    print(f"Received request for analysis results for {filename}")
    global vide_analysis_results_cache
    result = vide_analysis_results_cache.get(filename)
    if result:
        # Có kết quả, trả về JSON và xóa khỏi cache (tùy chọn)
        # del vide_analysis_results_cache[filename]
        print(f"Returning cached results for {filename}")
        return jsonify(result)
    else:
        # Chưa có kết quả (đang xử lý hoặc lỗi)
        print(f"Results not ready for {filename}. Returning processing status.")
        return jsonify({'status': 'processing'}), 202 # 202 Accepted

# Upload image route
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    files = request.files.getlist('image')
    if not files or files[0].filename == '':
        return redirect(url_for('index'))
    filenames = []
    for file in files:
        if file and file.filename:
            filename = datetime.now().strftime('%Y%m%d_%H%M%S_') + file.filename
            filepath = os.path.join(app.config['CAPTURE_FOLDER'], filename)
            try:
                file.save(filepath)
                filenames.append(filename)
            except Exception as e:
                print(f"Error saving uploaded image: {e}")
    # Nếu chỉ 1 ảnh thì redirect như cũ
    if len(filenames) == 1:
        return redirect(url_for('analyze_image', filename=filenames[0]))
    # Nếu nhiều ảnh thì phân tích lần lượt và render kết quả
    results = []
    for fname in filenames:
        result = analyze_image_backend(fname)
        results.append(result)
    history_data = load_history()
    return render_template('analyze.html', multi_results=results, history=history_data)

# Hàm backend để phân tích ảnh (không render template)
def analyze_image_backend(filename):
    image_path = os.path.join(app.config['CAPTURE_FOLDER'], filename)
    if not os.path.exists(image_path):
        return None
    model = YOLO('yolov8s.pt')
    class_list = []
    with open('coco.txt', 'r') as f:
        class_list = f.read().splitlines()
    frame = cv2.imread(image_path)
    if frame is None:
        return None
    results = model.predict(frame, verbose=False)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")
    count = 0
    for index, row in px.iterrows():
        d = int(row[5])
        c = class_list[d]
        if 'person' in c:
            count += 1
            x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, str(c), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    boxed_image_path_relative = f'captures/{os.path.splitext(filename)[0]}_boxed.jpg'
    boxed_image_path_full = os.path.join(app.config['CAPTURE_FOLDER'], os.path.splitext(filename)[0] + '_boxed.jpg')
    boxed_image_url = None
    try:
        cv2.imwrite(boxed_image_path_full, frame)
        boxed_image_url = url_for('static', filename=boxed_image_path_relative)
        boxed_image_url = boxed_image_url.replace('\\', '/')
    except Exception as e:
        boxed_image_url = None
    percent_levels = [10, 20, 30, 40, 50, 70, 90, 100]
    percent_results = [int(100*count/lvl) if lvl > 0 else 0 for lvl in percent_levels]
    percent_results = [min(100, p) for p in percent_results]
    import hashlib
    file_hash = ''
    try:
        with open(image_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        pass
    result = {
        'filename': filename,
        'max_people': int(count),
        'avg_people': float(count),
        'frame_count': 1,
        'duration': 0,
        'percent_levels': percent_levels,
        'percent_results': percent_results,
        'people_counts': [count],
        'file_hash': file_hash,
        'boxed_image': boxed_image_url,
    }
    save_history({
        'filename': filename,
        'type': 'image',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'max_people': int(count),
        'avg_people': float(count),
        'link': url_for('analyze_image', filename=filename),
        'file_hash': file_hash,
        'boxed_image': boxed_image_url,
        'percent_levels': percent_levels,
        'percent_results': percent_results,
        'frame_count': 1,
        'duration': 0,
        'people_counts': [count],
    })
    return result

# Analyze image route
@app.route('/analyze_image/<filename>')
def analyze_image(filename):
    image_path = os.path.join(app.config['CAPTURE_FOLDER'], filename)
    # Kiểm tra file tồn tại trước khi đọc
    if not os.path.exists(image_path):
        return "Image file not found", 404

    model = YOLO('yolov8s.pt')
    class_list = []
    with open('coco.txt', 'r') as f:
        class_list = f.read().splitlines()

    frame = cv2.imread(image_path)
    if frame is None:
        return "Error reading image file", 500

    results = model.predict(frame, verbose=False)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")
    count = 0
    for index, row in px.iterrows():
        d = int(row[5])
        c = class_list[d]
        if 'person' in c:
            count += 1
            x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, str(c), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    boxed_image_path_relative = f'captures/{os.path.splitext(filename)[0]}_boxed.jpg'
    boxed_image_path_full = os.path.join(app.config['CAPTURE_FOLDER'], os.path.splitext(filename)[0] + '_boxed.jpg')
    boxed_image_url = None
    try:
        cv2.imwrite(boxed_image_path_full, frame)
        boxed_image_url = url_for('static', filename=boxed_image_path_relative)
        boxed_image_url = boxed_image_url.replace('\\', '/')
        print(f"Successfully saved boxed image for {filename} at {boxed_image_path_full}")
    except Exception as e:
        print(f"Error saving boxed image: {e}")
        boxed_image_url = None


    percent_levels = [10, 20, 30, 40, 50, 70, 90, 100]
    percent_results = [int(100*count/lvl) if lvl > 0 else 0 for lvl in percent_levels]
    percent_results = [min(100, p) for p in percent_results]
    import hashlib
    file_hash = ''
    try:
        with open(image_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"Error calculating file hash for {filename}: {e}")

    result = {
        'filename': filename,
        'max_people': int(count),
        'avg_people': float(count),
        'frame_count': 1,
        'duration': 0,
        'percent_levels': percent_levels,
        'percent_results': percent_results,
        'people_counts': [count], # Vẫn để list để reuse analyze.html
        'file_hash': file_hash,
        'boxed_image': boxed_image_url,
    }

    # Lưu kết quả vào history cho ảnh
    save_history({
        'filename': filename,
        'type': 'image',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'max_people': int(count),
        'avg_people': float(count),
        'link': url_for('analyze_image', filename=filename),
        'file_hash': file_hash,
        'boxed_image': boxed_image_url, # Lưu URL ảnh box vào history
        'percent_levels': percent_levels,
        'percent_results': percent_results,
         'frame_count': 1,
        'duration': 0,
        'people_counts': [count],
    })

    history_data = load_history()
    # Render analyze.html với kết quả và lịch sử
    return render_template('analyze.html', filename=filename, result=result, history=history_data)

@app.route('/history')
def api_history():
    data = load_history()
    return jsonify(data)

@app.route('/stats')
def api_stats():
    data = load_history()
    total = len(data)
    total_people = sum(entry.get('max_people', 0) for entry in data)
    by_type = {'image': 0, 'video': 0}
    for entry in data:
        t = entry.get('type', 'image')
        by_type[t] = by_type.get(t, 0) + 1
    return jsonify({
        'total': total,
        'total_people': total_people,
        'by_type': by_type,
        'history': data
    })

@app.route('/stats_page')
def stats_page():
    return render_template('stats.html')

@app.route('/livestream_iphone')
def livestream_iphone():
    return render_template('livestream_iphone.html')

@app.route('/iphone_feed')
def iphone_feed():
    rtmp_url = 'rtmp://localhost:1935/live/stream'
    def gen():
        cap = cv2.VideoCapture(rtmp_url)
        model = YOLO('yolov8s.pt')
        class_list = []
        with open('coco.txt', 'r') as f:
            class_list = f.read().splitlines()
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            results = model.predict(frame, verbose=False)
            a = results[0].boxes.data
            px = pd.DataFrame(a).astype("float")
            count = 0
            for index, row in px.iterrows():
                d = int(row[5])
                c = class_list[d]
                if 'person' in c:
                    count += 1
                    x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, str(c), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            cv2.putText(frame, f'People: {count}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        cap.release()
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_iphone_frame', methods=['POST'])
def capture_iphone_frame():
    rtmp_url = 'rtmp://localhost:1935/live/stream'
    cap = cv2.VideoCapture(rtmp_url)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return {'status': 'fail'}
    # Nhận diện người
    model = YOLO('yolov8s.pt')
    class_list = []
    with open('coco.txt', 'r') as f:
        class_list = f.read().splitlines()
    results = model.predict(frame, verbose=False)
    a = results[0].boxes.data
    px = pd.DataFrame(a).astype("float")
    count = 0
    for index, row in px.iterrows():
        d = int(row[5])
        c = class_list[d]
        if 'person' in c:
            count += 1
            x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(frame, str(c), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, f'People: {count}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)
    # Lưu ảnh
    filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '_iphone.jpg'
    filepath = os.path.join(app.config['CAPTURE_FOLDER'], filename)
    cv2.imwrite(filepath, frame)
    image_url = url_for('static', filename=f'captures/{filename}')
    return {'status': 'ok', 'image_url': image_url, 'people_count': count}

@app.route('/record_iphone_video', methods=['POST'])
def record_iphone_video():
    global recording, video_writer, recorded_frames
    data = request.get_json()
    action = data.get('action')
    rtmp_url = 'rtmp://localhost:1935/live/stream'
    if action == 'start':
        if not recording:
            recording = True
            recorded_frames = []
            def record():
                cap = cv2.VideoCapture(rtmp_url)
                while recording:
                    ret, frame = cap.read()
                    if not ret:
                        continue
                    recorded_frames.append(frame.copy())
                cap.release()
            threading.Thread(target=record, daemon=True).start()
        return {'status': 'ok'}
    elif action == 'stop':
        if recording:
            recording = False
            # Xử lý nhận diện video
            if not recorded_frames:
                return {'status': 'fail'}
            model = YOLO('yolov8s.pt')
            class_list = []
            with open('coco.txt', 'r') as f:
                class_list = f.read().splitlines()
            max_people = 0
            out_filename = datetime.now().strftime('%Y%m%d_%H%M%S') + '_iphone.mp4'
            out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_filename)
            h, w = recorded_frames[0].shape[:2]
            video_writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), 15, (w, h))
            for frame in recorded_frames:
                results = model.predict(frame, verbose=False)
                a = results[0].boxes.data
                px = pd.DataFrame(a).astype("float")
                count = 0
                for index, row in px.iterrows():
                    d = int(row[5])
                    c = class_list[d]
                    if 'person' in c:
                        count += 1
                        x1, y1, x2, y2 = int(row[0]), int(row[1]), int(row[2]), int(row[3])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.putText(frame, str(c), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                if count > max_people:
                    max_people = count
                cv2.putText(frame, f'People: {count}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0), 3)
                video_writer.write(frame)
            video_writer.release()
            video_url = url_for('static', filename=f'uploads/{out_filename}')
            return {'status': 'ok', 'video_url': video_url, 'max_people': max_people}
        else:
            return {'status': 'fail'}
    else:
        return {'status': 'fail'}

@app.route('/history_hash')
def history_hash():
    history_data = load_history()
    return render_template('history_hash.html', history=history_data)

@app.route('/full_history')
def full_history():
    history_data = load_history()
    return render_template('full_history.html', history=history_data)

@app.route('/detect')
def detect_page():
    return render_template('detect.html')

if __name__ == '__main__':
    # Tạo thư mục static/uploads và static/captures nếu chưa có
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CAPTURE_FOLDER'], exist_ok=True)
    # Tạo file history.json rỗng nếu chưa có
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump([], f)

    app.run(host='0.0.0.0', port=5000, debug=True) 