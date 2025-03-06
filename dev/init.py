import os
import sys
import configparser
import platform
from datetime import datetime
import logging

class AppConfig:
    # 类的定义保持不变
    def __init__(self):      
        # 初始化配置文件
        self.init_config()
        # 初始化日志记录器
        self.init_logging()
        # 初始化窗口参数
        self.init_window()
        # 支持格式
        self.init_supported_formats()
        # 初始化bin路径
        self.init_bin()
        self.max_ffmpeg_processes = 10
        self.author_info = f"qoph.fun,AKXL718@163.com,2025-03-06"
        self.title = "图片转换工具1.0005"
        self.input_button_item = ''
        self.output_button_item = ''
        self.failed_output_button_item = ''
        self.format_combobox_item = ''
        self.encoder_combobox_item = ''
        self.compression_combobox_item = ''
        self.quality_scale_item = ''
        self.rename_checkbox_item = ''
        self.process_button_item = ''
    # ---------------------------__init__ end----------------------------   
    # 初始化支持读取的格式
    def init_supported_formats(self):
        #------------------Pillow库支持的格式------------------
        # ------完全支持的格式                                        
        # BLP BMP DDS DIB EPS GIF ICNS ICO IM JPEG JPEG2000 
        # MPO MSP PCX PFM PNG PPM SGI SPIDER TGA TIFF
        # WEBP XBM
        # ------只支持读的格式
        # CUR DCX FITS FLI,FLC FPX FTEX GBR GD IMT IPTC/NAA
        # MCIDAS MIC PCD PIXAR PSD QOI SUN WAL WMF,EMF XPM
        # ------只支持写的格式
        # PALM PDF XV Thumbnails
        # ------常用格式
        # WEBP  JPEG2000  JPEG  PNG  GIF  BMP  ICO  JPG
        #----------------------------end---------------------
        self.supported_read_formats_image = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".ico",
                                            ".jfif", ".jpe", ".tif", ".tiff", ".dib", ".jp2", ".j2k", ]
        
        self.supported_read_formats_vidoe = [".mp4",".avi",".mkv",".webm"]

        self.supported_read_formats_audio = [".mp3",".wav",".flac",".aac",".ogg"]

        self.supported_output_formats = ["webp", "png", "jpeg", "jpeg2000","avif"]

        self.supported_encoder_formats = ["libsvtav1", "libaom-av1"]

        self.supported_compression_formats = ["无损", "有损"]
    # ---------------------------init_supported_formats end----------------------------   
    # 初始化配置文件
    def init_config(self):
        appdata_dir = self.getAppData()   
        # 配置文件目录
        self.config_folder = os.path.join(appdata_dir, "ToAvif")
        # 配置文件路径
        self.config_file = os.path.join(self.config_folder, 'config.ini')
       
        # 确保配置文件夹
        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

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
            self.config.set('Settings', 'rename', '0')  
            self.config.set('Settings', 'cuda', '0')  
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
        self.input_folder = self.config.get('Paths', 'input_folder', fallback='') # 读取输入文件夹配置
        self.output_folder = self.config.get('Paths', 'output_folder', fallback='') # 读取输出文件夹配置
        self.failed_output_folder = self.config.get('Paths', 'failed_output_folder', fallback='') # 读取失败图片保存路径配置
        self.quality = int(self.config.get('Settings', 'quality', fallback='80')) # 读取有损压缩质量配置
        self.output_format = self.config.get('Settings', 'output_format', fallback='avif') # 读取输出格式配置
        self.compression_type = self.config.get('Settings', 'compression_type', fallback='无损')  # 读取压缩方式配置
        self.encoder = self.config.get('Settings', 'encoder', fallback='libaom-av1')  # 读取编码器配置
        self.rename = int(self.config.get('Settings', 'rename', fallback='0'))  # 读取是否重命名配置
        self.cuda = int(self.config.get('Settings', 'cuda', fallback='0'))  # 读取是否使用CUDA配置
    # ---------------------------init_config end----------------------------  
    # 初始化日志记录器
    def init_logging(self):
        # 临时图片文件夹
        self.temp_image_folder = os.path.join(self.config_folder, "temp_image")
        if not os.path.exists(self.temp_image_folder):
            os.makedirs(self.temp_image_folder)
        # 日志文件目录
        self.config_folder_log = os.path.join(self.config_folder, "log")
        # 日志文件路径
        error_log_file = os.path.join(self.config_folder_log, f"error_{datetime.now().strftime('%Y-%m-%d')}.log")
        info_log_file = os.path.join(self.config_folder_log, f"info_{datetime.now().strftime('%Y-%m-%d')}.log")
        # 确保日志文件夹存在
        if not os.path.exists(self.config_folder_log):
            os.makedirs(self.config_folder_log)
        # 初始化错误日志记录器
        self.error_logger = logging.getLogger('error_logger')
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s -----------------')
        error_handler.setFormatter(error_formatter)
        self.error_logger.addHandler(error_handler)

        # 初始化信息日志记录器
        self.info_logger = logging.getLogger('info_logger')
        self.info_logger.setLevel(logging.INFO)
        info_handler = logging.FileHandler(info_log_file, encoding='utf-8')
        info_handler.setFormatter(error_formatter)
        self.info_logger.addHandler(info_handler)
    # ---------------------------init_logging end----------------------------  
    # 初始化窗口
    def init_window(self): 
        # 设置窗口的大小和位置
        self.window_width = 400
        self.window_height = 400
        # 路径文本最大宽度
        self.wraplength = self.window_width - 20
        self.label_width = 13
        # 最小窗口高度
        self.min_window_height = 400
        # 记录每个标签因换行增加的高度
        self.height_increases = {
            "input_label": 23,
            "output_label": 23,
            "failed_output_label": 23
        }
        # 记录每个标签的高度
        self.checkbox_height = 30
        self.combobox_height = 40
        self.scale_height = 75
        self.progress_bar_height = 50
        self.last_output_format = self.output_format
        self.last_compression = self.compression_type
    # ---------------------------init_window end----------------------------   
    def init_bin(self):
        ffmpeg_path = ''
        if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            base_path = sys._MEIPASS
            ffmpeg_path = os.path.join(base_path,'bin', 'ffmpeg', 'bin', 'ffmpeg.exe')    
        else:
            # 如果是开发环境下的脚本文件
            base_path = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = os.path.join(base_path,'..','bin', 'ffmpeg', 'bin', 'ffmpeg.exe')    

       
        # avfilter_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avfilter-10.dll')
        # avcodec_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avcodec-61.dll')
        # avdevice_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avdevice-61.dll')
        # avformat_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avformat-61.dll')

        # avutil_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avutil-59.dll')
        # postproc_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'postproc-58.dll')
        # swresample_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'swresample-5.dll')
        # swscale_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'swscale-8.dll')

        # 设置 ffmpeg 可执行文件路径
        os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)
    # ---------------------------init_bin end----------------------------   
    # 获取 AppData 目录
    def getAppData(self):
        if platform.system() == "Windows":
            appdata_dir = os.getenv('APPDATA')
        elif platform.system() == "Darwin":  # macOS
            appdata_dir = os.path.expanduser('~/Library/Application Support')
        elif platform.system() == "Linux":
            appdata_dir = os.path.expanduser('~/.config')
        else:
            appdata_dir = os.getcwd()

        return appdata_dir  
    # ---------------------------getAppData end----------------------------   
# 创建 AppConfig 类的实例
app_config = AppConfig()
error_logger = app_config.error_logger
info_logger = app_config.info_logger
