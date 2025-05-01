import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_TOKEN = '4a6864292edd6b25a0f78029418dbd464298547d'

def get_air_quality_data(lat=None, lon=None, city="Yogyakarta"):
    if lat and lon:
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={API_TOKEN}"
    else:
        url = f"https://api.waqi.info/feed/{city}/?token={API_TOKEN}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "ok":
            aqi = data["data"]["aqi"]
            # Tentukan warna dan saran kesehatan berdasarkan nilai AQI
            if aqi <= 50:
                class_color = "green"
                health_advice = "Baik - Aman untuk beraktivitas di luar ruangan."
                category = "Baik"
            elif aqi <= 100:
                class_color = "yellow"
                health_advice = "Sedang - Kurangi aktivitas luar ruangan jika Anda sensitif terhadap polusi udara."
                category = "Sedang"
            elif aqi <= 150:
                class_color = "orange"
                health_advice = "Tidak sehat bagi kelompok sensitif. Anak-anak, lansia, dan penderita penyakit pernapasan harus membatasi aktivitas luar ruangan."
                category = "Tidak Sehat bagi Kelompok Sensitif"
            elif aqi <= 200:
                class_color = "red"
                health_advice = "Tidak sehat - Batasi aktivitas luar ruangan."
                category = "Tidak Sehat"
            elif aqi <= 300:
                class_color = "purple"
                health_advice = "Sangat tidak sehat - Kurangi aktivitas di luar ruangan sebanyak mungkin."
                category = "Sangat Tidak Sehat"
            else:
                class_color = "darkred"
                health_advice = "Berbahaya - Hindari aktivitas di luar ruangan."
                category = "Berbahaya"
            
            # Tambahkan data polutan dan cuaca tambahan
            pm25 = data["data"]["iaqi"].get("pm25", {}).get("v", "N/A")
            pm10 = data["data"]["iaqi"].get("pm10", {}).get("v", "N/A")
            temp = data["data"]["iaqi"].get("t", {}).get("v", "N/A")
            pressure = data["data"]["iaqi"].get("p", {}).get("v", "N/A")
            humidity = data["data"]["iaqi"].get("h", {}).get("v", "N/A")
            wind = data["data"]["iaqi"].get("w", {}).get("v", "N/A")

            return {
                "aqi": aqi,
                "class_color": class_color,
                "category": category,
                "health_advice": health_advice,
                "pm25": pm25,
                "pm10": pm10,
                "temp": temp,
                "pressure": pressure,
                "humidity": humidity,
                "wind": wind
            }
        else:
            return None
    else:
        return None

# Halaman Utama dengan Pilihan Input
@app.route('/')
def home():
    return render_template('home.html')

# Halaman untuk Input Koordinat
@app.route('/input_coordinates', methods=['GET', 'POST'])
def input_coordinates():
    data = None
    if request.method == 'POST':
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        data = get_air_quality_data(lat=lat, lon=lon)
    return render_template('input_coordinates.html', data=data)

# Halaman untuk Memilih Lokasi di Peta
@app.route('/input_map')
def input_map():
    return render_template('input_map.html')

# Route untuk Memperbarui Data Berdasarkan Klik di Peta
@app.route('/air_quality_by_coords')
def air_quality_by_coords():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    data = get_air_quality_data(lat=lat, lon=lon)
    if data:
        return jsonify(data)
    return jsonify({"error": "Data tidak tersedia"}), 404

if __name__ == '__main__':
    app.run(debug=True)
