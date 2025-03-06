这是一个图片转换工具，使用python pillow + ffmpeg开发

支持将多种格式图片以`webp`或`avif`格式输出

### 如何开始？

安装pillow库
```bash
pip install pillow
```

在`webp_core.py`或 `init.py `文件中配置 `ffmpeg.exe`的路径

```python
 if getattr(sys, 'frozen', False):
            # 如果是打包后的可执行文件
            base_path = sys._MEIPASS
            ffmpeg_path = os.path.join(base_path,'..','bin', 'ffmpeg', 'bin', 'ffmpeg.exe')    
        else:
            # 如果是开发环境下的脚本文件
            base_path = os.path.dirname(os.path.abspath(__file__))
            ffmpeg_path = os.path.join(base_path,'..','bin', 'ffmpeg', 'bin', 'ffmpeg.exe')    

```
通过`webp_ui.py`开始

```bash
python webp_ui.py
```
也可以通过 `ui.py` 从开发版本开始

```bash
python ./dev/ui.py
```
