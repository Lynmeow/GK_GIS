import requests
import os

DISTRICTS = [
    {"name": "Quận 1",     "lat": 10.7769, "lng": 106.7009, "ndvi": 0.18, "lst": 38.5},
    {"name": "Quận 3",     "lat": 10.7797, "lng": 106.6855, "ndvi": 0.20, "lst": 37.9},
    {"name": "Quận 4",     "lat": 10.7583, "lng": 106.7020, "ndvi": 0.19, "lst": 38.2},
    {"name": "Quận 5",     "lat": 10.7553, "lng": 106.6625, "ndvi": 0.17, "lst": 38.8},
    {"name": "Quận 6",     "lat": 10.7464, "lng": 106.6346, "ndvi": 0.21, "lst": 37.6},
    {"name": "Quận 7",     "lat": 10.7323, "lng": 106.7218, "ndvi": 0.35, "lst": 36.2},
    {"name": "Quận 8",     "lat": 10.7231, "lng": 106.6285, "ndvi": 0.22, "lst": 37.4},
    {"name": "Quận 10",    "lat": 10.7740, "lng": 106.6680, "ndvi": 0.16, "lst": 39.1},
    {"name": "Quận 11",    "lat": 10.7626, "lng": 106.6488, "ndvi": 0.17, "lst": 38.7},
    {"name": "Quận 12",    "lat": 10.8679, "lng": 106.6567, "ndvi": 0.28, "lst": 40.1},
    {"name": "Bình Thạnh", "lat": 10.8123, "lng": 106.7141, "ndvi": 0.25, "lst": 37.5},
    {"name": "Gò Vấp",     "lat": 10.8384, "lng": 106.6652, "ndvi": 0.24, "lst": 39.0},
    {"name": "Phú Nhuận",  "lat": 10.7993, "lng": 106.6800, "ndvi": 0.20, "lst": 38.3},
    {"name": "Tân Bình",   "lat": 10.8015, "lng": 106.6519, "ndvi": 0.22, "lst": 38.6},
    {"name": "Tân Phú",    "lat": 10.7906, "lng": 106.6283, "ndvi": 0.23, "lst": 38.1},
    {"name": "Bình Tân",   "lat": 10.7637, "lng": 106.6019, "ndvi": 0.26, "lst": 38.0},
    {"name": "Thủ Đức",    "lat": 10.8701, "lng": 106.7539, "ndvi": 0.42, "lst": 35.8},
    {"name": "Bình Chánh", "lat": 10.6838, "lng": 106.5686, "ndvi": 0.31, "lst": 39.8},
    {"name": "Hóc Môn",    "lat": 10.8914, "lng": 106.5950, "ndvi": 0.38, "lst": 38.9},
    {"name": "Củ Chi",     "lat": 11.0046, "lng": 106.4894, "ndvi": 0.58, "lst": 33.8},
    {"name": "Nhà Bè",     "lat": 10.6978, "lng": 106.7421, "ndvi": 0.52, "lst": 34.5},
    {"name": "Cần Giờ",    "lat": 10.4113, "lng": 106.9523, "ndvi": 0.71, "lst": 32.1},
]

# Màu riêng cho từng quận
DISTRICT_COLORS = [
    '#EF233C','#FF6B6B','#FF9A3C','#FFD60A','#06D6A0','#00B4D8',
    '#0077B6','#7B2FBE','#F72585','#4CC9F0','#4361EE','#3A0CA3',
    '#7209B7','#560BAD','#480CA8','#3F37C9','#4895EF','#4CC9F0',
    '#06D6A0','#80B918','#AACC00','#BFD200',
]

def get_districts_air_quality():
    """Lấy AQI thật cho từng quận từ OpenWeather"""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    results = []

    for i, d in enumerate(DISTRICTS):
        try:
            url = (
                f"http://api.openweathermap.org/data/2.5/air_pollution"
                f"?lat={d['lat']}&lon={d['lng']}&appid={api_key}"
            )
            res  = requests.get(url, timeout=5)
            data = res.json()

            aqi_raw = data['list'][0]['main']['aqi']
            pm25    = data['list'][0]['components']['pm2_5']
            no2     = data['list'][0]['components']['no2']

            aqi_map = {1: 25, 2: 75, 3: 125, 4: 175, 5: 300}
            aqi     = aqi_map.get(aqi_raw, 50)

            results.append({
                'name':  d['name'],
                'lat':   d['lat'],
                'lng':   d['lng'],
                'aqi':   aqi,
                'pm25':  round(pm25, 1),
                'no2':   round(no2, 1),
                'level': aqi_raw,
                'ndvi':  d.get('ndvi', 0.3),
                'lst':   d.get('lst', 36.0),
                'color': DISTRICT_COLORS[i % len(DISTRICT_COLORS)],
            })
        except Exception:
            results.append({
                'name':  d['name'],
                'lat':   d['lat'],
                'lng':   d['lng'],
                'aqi':   50,
                'pm25':  0,
                'no2':   0,
                'level': 1,
                'ndvi':  d.get('ndvi', 0.3),
                'lst':   d.get('lst', 36.0),
                'color': DISTRICT_COLORS[i % len(DISTRICT_COLORS)],
            })

    return results


def get_risk_classification():
    """
    Tính điểm rủi ro tổng hợp cho từng quận từ AQI + LST + NDVI.

    Công thức điểm rủi ro (0-100):
      - AQI score  (40%): AQI/300 * 40
      - LST score  (35%): (LST-28)/17 * 35
      - NDVI score (25%): (1-NDVI) * 25

    Phân loại:
      - 0-35  : Thấp
      - 36-60 : Trung bình
      - 61-80 : Cao
      - 81-100: Nguy hiểm
    """
    districts_data = get_districts_air_quality()
    results = []

    for d in districts_data:
        aqi  = d['aqi']
        lst  = d['lst']
        ndvi = d['ndvi']

        # Tính điểm từng yếu tố
        aqi_score  = min(40, (aqi / 300) * 40)
        lst_score  = min(35, max(0, (lst - 28) / 17 * 35))
        ndvi_score = min(25, (1 - ndvi) * 25)
        total_score = round(aqi_score + lst_score + ndvi_score, 1)

        # Phân loại
        if total_score >= 81:
            risk_level, risk_label, risk_color = 'critical', 'Nguy hiểm', '#EF233C'
        elif total_score >= 61:
            risk_level, risk_label, risk_color = 'high', 'Cao', '#FF9A3C'
        elif total_score >= 36:
            risk_level, risk_label, risk_color = 'medium', 'Trung bình', '#FFD60A'
        else:
            risk_level, risk_label, risk_color = 'low', 'Thấp', '#06D6A0'

        # Nguyên nhân chính
        causes = []
        if aqi > 100:
            causes.append({'factor': 'AQI', 'msg': f'AQI {aqi} — ô nhiễm không khí cao'})
        if lst > 38:
            causes.append({'factor': 'LST', 'msg': f'LST {lst}°C — đảo nhiệt đô thị'})
        if ndvi < 0.2:
            causes.append({'factor': 'NDVI', 'msg': f'NDVI {ndvi} — thiếu cây xanh'})
        if not causes:
            causes.append({'factor': 'OK', 'msg': 'Môi trường trong ngưỡng an toàn'})

        # Đề xuất hành động
        recommendations = []
        if ndvi < 0.2:
            recommendations.append('🌳 Tăng diện tích cây xanh, công viên đô thị')
        if ndvi < 0.25:
            recommendations.append('🌿 Trồng cây vỉa hè, mái nhà xanh')
        if lst > 38:
            recommendations.append('💧 Tăng mặt nước, hồ điều tiết nhiệt')
        if lst > 40:
            recommendations.append('🏗 Hạn chế bê tông hóa, dùng vật liệu phản nhiệt')
        if aqi > 100:
            recommendations.append('🚗 Hạn chế phương tiện cá nhân giờ cao điểm')
        if aqi > 150:
            recommendations.append('🏭 Kiểm soát khí thải công nghiệp')
        if not recommendations:
            recommendations.append('✅ Duy trì hiện trạng, tiếp tục giám sát')

        results.append({
            **d,
            'risk_score':  total_score,
            'risk_level':  risk_level,
            'risk_label':  risk_label,
            'risk_color':  risk_color,
            'score_detail': {
                'aqi_score':  round(aqi_score, 1),
                'lst_score':  round(lst_score, 1),
                'ndvi_score': round(ndvi_score, 1),
            },
            'causes':          causes,
            'recommendations': recommendations,
        })

    results.sort(key=lambda x: x['risk_score'], reverse=True)
    return results