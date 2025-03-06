
import subprocess
import os
base_path = os.path.dirname(os.path.abspath(__file__))
ffmpeg_path = os.path.join(base_path,'..','bin', 'ffmpeg', 'bin', 'ffmpeg.exe')    
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

input_path = r'D:\BaiduNetdiskDownload\wait play\BK\待压缩的girl\2\service sex anal fondle (00000).webm'
output_path = r'D:\BaiduNetdiskDownload\wait play\BK\待压缩的girl\4\service sex anal fondle (00000).avif'
command1 = [
                'ffmpeg',
                '-i', input_path,  # 输入文件
                '-c:v', 'libaom-av1',  # 使用 libaom-av1 编码器
             
                '-cpu-used', "5",  # 压缩效率
                '-row-mt', '1',  # 启用行级多线程
                '-tiles', "4x4",  # 瓦片分割
                '-pix_fmt', 'yuv420p',  # 使用 yuv420p 像素格式
                '-loop', '0',  # 设置无限循环
                '-crf', '32',  # 设置压缩质量
                '-fps_mode', 'vfr',  # 保持原始帧率
                '-an',  # 移除音频

                output_path  # 输出文件
            ]
command = [
            'ffprobe'    ,
            output_path
            ]
   #'-lossless', '1',  # 启用无损压缩
command2 = [
            'ffplay',
            output_path
            ]
process = subprocess.run(command2)