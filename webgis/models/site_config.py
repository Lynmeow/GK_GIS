from django.db import models


class SiteConfig(models.Model):
    # Hero
    hero_subtitle = models.TextField(blank=True, default='Nền tảng WebGIS tích hợp ảnh vệ tinh Sentinel-2, Landsat 8 và dữ liệu khí tượng thực tế để theo dõi, phân tích và cảnh báo các chỉ số môi trường đô thị TP.HCM theo thời gian thực.')

    # Mục tiêu
    about_desc = models.TextField(blank=True, default='TP.HCM đang đối mặt với nhiều thách thức môi trường nghiêm trọng như ô nhiễm không khí, đảo nhiệt đô thị và suy giảm mảng xanh. HHL WebGIS cung cấp công cụ giám sát môi trường toàn diện, trực quan và dễ tiếp cận cho các nhà nghiên cứu và cơ quan quản lý đô thị.')

    # Mission cards
    mission1_title = models.CharField(max_length=200, blank=True, default='Dữ liệu vệ tinh độ phân giải cao')
    mission1_desc  = models.TextField(blank=True, default='Tích hợp ảnh Sentinel-2 (10m) và Landsat 8 (30m) qua Google Earth Engine, cung cấp dữ liệu không gian liên tục và cập nhật định kỳ.')
    mission2_title = models.CharField(max_length=200, blank=True, default='Phân tích đa chỉ số tích hợp')
    mission2_desc  = models.TextField(blank=True, default='Tổng hợp đồng thời nhiều chỉ số môi trường trong một nền tảng duy nhất, hỗ trợ phân tích xu hướng theo không gian và thời gian.')
    mission3_title = models.CharField(max_length=200, blank=True, default='Ứng dụng Machine Learning')
    mission3_desc  = models.TextField(blank=True, default='Mô hình Random Forest dự đoán nhiệt độ bề mặt đất (LST), phân tích và cảnh báo sớm hiện tượng đảo nhiệt đô thị (UHI) tại TP.HCM.')
    mission4_title = models.CharField(max_length=200, blank=True, default='Hệ thống cảnh báo chủ động')
    mission4_desc  = models.TextField(blank=True, default='Tự động phát cảnh báo khi AQI, PM2.5 hay LST vượt ngưỡng an toàn, phân loại theo mức độ và khu vực để hỗ trợ ra quyết định kịp thời.')

    # Module cards
    module1_title = models.CharField(max_length=200, blank=True, default='Bản Đồ')
    module1_desc  = models.TextField(blank=True, default='Hiển thị ảnh vệ tinh và lớp chỉ số môi trường tương tác trên Leaflet.js. Xem chi tiết theo từng quận/huyện.')
    module2_title = models.CharField(max_length=200, blank=True, default='Phân Tích')
    module2_desc  = models.TextField(blank=True, default='Phân tích xu hướng NDVI, LST, AQI, PM2.5 theo không gian và thời gian. Biểu đồ Chart.js trực quan.')
    module3_title = models.CharField(max_length=200, blank=True, default='Cảnh Báo')
    module3_desc  = models.TextField(blank=True, default='Tự động phát cảnh báo khi chỉ số vượt ngưỡng. Phân loại mức độ xanh, vàng, đỏ.')
    module4_title = models.CharField(max_length=200, blank=True, default='Báo Cáo')
    module4_desc  = models.TextField(blank=True, default='Tổng hợp và xuất báo cáo định kỳ theo ngày, tuần, tháng. Lưu trữ lịch sử báo cáo.')
    module5_title = models.CharField(max_length=200, blank=True, default='Dự Báo Thời Tiết')
    module5_desc  = models.TextField(blank=True, default='Dự báo 7 ngày tích hợp OpenWeatherMap API. Hiển thị nhiệt độ, độ ẩm, gió, lượng mưa.')
    module6_title = models.CharField(max_length=200, blank=True, default='Dự Báo ML')
    module6_desc  = models.TextField(blank=True, default='Dự đoán nhiệt độ bề mặt đất bằng Random Forest. Phân tích đảo nhiệt đô thị theo quận.')
    module7_title = models.CharField(max_length=200, blank=True, default='Đề Xuất')
    module7_desc  = models.TextField(blank=True, default='Kênh tiếp nhận đề xuất từ Nhà nghiên cứu với hệ thống xét duyệt và audit log đầy đủ.')

    # Index cards
    index1_name = models.CharField(max_length=50, blank=True, default='NDVI')
    index1_desc = models.CharField(max_length=200, blank=True, default='Chỉ số thực vật, độ phủ xanh đô thị')
    index2_name = models.CharField(max_length=50, blank=True, default='LST')
    index2_desc = models.CharField(max_length=200, blank=True, default='Nhiệt độ bề mặt đất, đảo nhiệt UHI')
    index3_name = models.CharField(max_length=50, blank=True, default='NDWI')
    index3_desc = models.CharField(max_length=200, blank=True, default='Chỉ số mặt nước, sông kênh đô thị')
    index4_name = models.CharField(max_length=50, blank=True, default='NDBI')
    index4_desc = models.CharField(max_length=200, blank=True, default='Mật độ xây dựng, bê tông hóa đô thị')
    index5_name = models.CharField(max_length=50, blank=True, default='AQI')
    index5_desc = models.CharField(max_length=200, blank=True, default='Chỉ số chất lượng không khí tổng hợp')
    index6_name = models.CharField(max_length=50, blank=True, default='PM2.5')
    index6_desc = models.CharField(max_length=200, blank=True, default='Bụi mịn siêu nhỏ, tác nhân ô nhiễm chính')

    # Contact
    contact_desc = models.TextField(blank=True, default='Mọi thắc mắc hoặc góp ý về hệ thống, vui lòng liên hệ nhóm phát triển HHL.')

    class Meta:
        verbose_name = 'Cấu hình trang giới thiệu'

    def __str__(self):
        return 'Site Config'

    @classmethod
    def get_config(cls):
        config, _ = cls.objects.get_or_create(id=1)
        return config