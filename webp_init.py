import os
import configparser
import platform
from datetime import datetime
import logging

class AppConfig:
    # 类的定义保持不变
    def __init__(self):
 
        # 获取 AppData 目录
        if platform.system() == "Windows":
            appdata_dir = os.getenv('APPDATA')
        elif platform.system() == "Darwin":  # macOS
            appdata_dir = os.path.expanduser('~/Library/Application Support')
        elif platform.system() == "Linux":
            appdata_dir = os.path.expanduser('~/.config')
        else:
            appdata_dir = os.getcwd()

        # 配置文件路径
        self.config_folder = os.path.join(appdata_dir, "ToWebp")
        self.config_file = os.path.join(self.config_folder, 'config.ini')

        # 确保配置文件夹存在
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

        # 日志文件路径，以日期命名
        self.log_file = os.path.join(self.config_folder, f"{datetime.now().strftime('%Y-%m-%d')}.log")

        # 初始化日志记录器
        logging.basicConfig(filename=self.log_file, level=logging.ERROR,
                            format='%(asctime)s - %(levelname)s - %(message)s',encoding='utf-8')
        # 初始化配置
        self.config = configparser.ConfigParser()
        # 检查配置文件是否存在，不存在则创建并写入默认配置
        if not os.path.exists(self.config_file):
            self.config.add_section('Paths')
            self.config.set('Paths', 'input_folder', '')
            self.config.set('Paths', 'output_folder', '')
            self.config.set('Paths', 'failed_output_folder', '')
            self.config.add_section('Settings')
            self.config.set('Settings', 'output_format', 'webp')
            self.config.set('Settings', 'compression_type', '无损')
            self.config.set('Settings', 'quality', '80')
            self.config.set('Settings', 'encoder', 'libsvtav1')  # 保存编码器配置
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        else:
            self.config.read(self.config_file)
            # 确保 'Paths' 和 'Settings' 部分存在
            if not self.config.has_section('Paths'):
                self.config.add_section('Paths')
            if not self.config.has_section('Settings'):
                self.config.add_section('Settings')

        # 读取配置
        self.input_folder = self.config.get('Paths', 'input_folder', fallback='')
        self.output_folder = self.config.get('Paths', 'output_folder', fallback='')
        self.failed_output_folder = self.config.get('Paths', 'failed_output_folder', fallback='')
        self.quality = int(self.config.get('Settings', 'quality', fallback=''))
        self.output_format = self.config.get('Settings', 'output_format', fallback='')
        self.compression_type = self.config.get('Settings', 'compression_type', fallback='')
        self.encoder = self.config.get('Settings', 'encoder', fallback='')  # 读取编码器配置
        # 完全支持的格式
        # BLP BMP DDS DIB EPS GIF ICNS ICO IM JPEG JPEG2000 
        # MPO MSP PCX PFM PNG PPM SGI SPIDER TGA TIFF
        # WEBP XBM
        # 只支持读的格式
        # CUR DCX FITS FLI,FLC FPX FTEX GBR GD IMT IPTC/NAA
        # MCIDAS MIC PCD PIXAR PSD QOI SUN WAL WMF,EMF XPM
        # 只支持写的格式
        # PALM PDF XV Thumbnails
        # 常用格式
        # WEBP  JPEG2000  JPEG  PNG  GIF  BMP  ICO  JPG
        # self.output_format = "WEBP"
        # self.compression_type = "无损"
        # [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".ico",
        #                           ".jfif", ".jpe", ".tif", ".apng", ".tiff", ".dib", ".jxl",
        #                           ".jp2", ".j2k", ".jpc", ".jpf", ".jpx", ".j2c"]
        self.supported_formats = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".ico",
                                  ".jfif", ".jpe", ".tif", ".tiff", ".dib", ".jp2", ".j2k", ]
        
        self.supported_formats_vidoe = [".mp4",".avi",".mkv",".webm"]

        # 设置窗口的大小和位置
        self.window_width = 400
        self.window_height = 510
        # 新增：设置最小窗口高度
        self.min_window_height = 510
        # 记录每个标签因换行增加的高度
        self.height_increases = {
            "input_label": 23,
            "output_label": 23,
            "failed_output_label": 23
        }

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
        except Exception as e:
            logging.error(f"保存配置文件时出错: {e}")

# 创建 AppConfig 类的实例
app_config = AppConfig()
