from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Thông tin API gốc
BASE_TARGET_URL = "http://dungkon.lol/images"

# Thay vì 1 key, chúng ta đưa tất cả vào 1 list
API_KEYS = [
    "dungkon_nhh59", 
    "dungkon_ltjqia", 
    "dungkon_6xbidn", 
    "dungkon_bd9r4d",
    "dungkon_spsal5", 
    "dungkon_d1jebi", 
    "dungkon_2kd0op", 
    "dungkon_wizjy",
    "dungkon_j5ysp", 
    "dungkon_skvhi3", 
    "dungkon_f3ii8e", 
    "dungkon_4z4rj", 
    "dungkon_ugz56", 
    "dungkon_u2z1lm", 
    "dungkon_j5rtj8"
]

# Biến toàn cục để theo dõi xem đang dùng key ở vị trí nào (bắt đầu từ 0)
current_key_index = 0

@app.route('/')
def index():
    host = request.host_url 
    
    api_list = [
        {"path": "/api/images/du", "desc": "ảnh vú", "url": f"{host}api/images/du"},
        {"path": "/api/images/bopvu", "desc": "bóp vú", "url": f"{host}api/images/bopvu"},
        {"path": "/api/images/dit", "desc": "ảnh địt", "url": f"{host}api/images/dit"},
        {"path": "/api/images/bucu", "desc": "bú cu", "url": f"{host}api/images/bucu"},
        {"path": "/api/images/bopmong", "desc": "bóp mông", "url": f"{host}api/images/bopmong"},
        {"path": "/api/images/lon", "desc": "ảnh lồn", "url": f"{host}api/images/lon"},
        {"path": "/api/images/lon", "desc": "ảnh lồn", "url": f"{host}api/images/lon"}
    ]
    return render_template('index.html', apis=api_list)

@app.route('/api/images/<endpoint>', methods=['GET'])
def proxy_image(endpoint):
    global current_key_index
    
    # Vòng lặp này sẽ thử tối đa bằng số lượng key đang có (5 lần)
    # Tránh việc lặp vô hạn nếu tất cả các key đều đã hết lượt
    for _ in range(len(API_KEYS)):
        current_key = API_KEYS[current_key_index]
        target_url = f"{BASE_TARGET_URL}/{endpoint}?apikey={current_key}"
        
        try:
            response = requests.get(target_url, timeout=10)
            
            # TRƯỜNG HỢP 1: API gốc chặn luôn bằng mã lỗi HTTP (VD: 429 Too Many Requests, 403)
            if response.status_code != 200:
                print(f"Key {current_key} bị lỗi HTTP {response.status_code}. Chuyển key...")
                # Tăng index lên 1, nếu vượt quá số lượng key thì quay về 0
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                continue # Bỏ qua vòng lặp này, quay lại vòng lặp mới với key mới
                
            data = response.json()
            
            # TRƯỜNG HỢP 2: API gốc vẫn trả về mã 200 nhưng nội dung JSON báo lỗi hết lượt
            # (Bạn cần điều chỉnh chữ "error" hoặc "limit" tùy theo cách API dungkon báo lỗi)
            if data.get("error") == "Đã vượt quá giới hạn sử dụng API Key.":
                print(f"Key {current_key} đã hết hạn mức. Chuyển key...")
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                continue

            # Nếu chạy đến đây tức là lấy ảnh thành công, trả về cho người dùng luôn
            return jsonify(data), 200
            
        except requests.exceptions.RequestException as e:
            # Lỗi mạng hoặc API gốc sập, cũng thử đổi key
            print(f"Lỗi kết nối với key {current_key}: {e}")
            current_key_index = (current_key_index + 1) % len(API_KEYS)
            continue
            
    # Nếu chạy hết vòng lặp (đã thử hết toàn bộ 5 key) mà vẫn không return được data
    return jsonify({
        "status": "error", 
        "message": "Toàn bộ API Key đều đã cạn lượt hôm nay hoặc máy chủ gốc đang bảo trì."
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
