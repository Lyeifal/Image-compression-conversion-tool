import os
import sys
import shutil
from PIL import Image
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import logging
import traceback
from webp_init import AppConfig
import threading
import subprocess

# 全局变量，用于控制处理过程是否中止
abort_flag = False
# 假设 root 是 tkinter 主窗口对象，在 webp_ui.py 中传递进来
root = None

if getattr(sys, 'frozen', False):
    # 如果是打包后的可执行文件
    base_path = sys._MEIPASS
else:
    # 如果是开发环境下的脚本文件
    base_path = os.path.dirname(os.path.abspath(__file__))



ffmpeg_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'ffmpeg.exe')    
avfilter_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avfilter-10.dll')
avcodec_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avcodec-61.dll')
avdevice_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avdevice-61.dll')
avformat_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avformat-61.dll')

avutil_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'avutil-59.dll')
postproc_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'postproc-58.dll')
swresample_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'swresample-5.dll')
swscale_path = os.path.join(base_path, 'bin', 'ffmpeg', 'bin', 'swscale-8.dll')

# 设置 ffmpeg 可执行文件路径
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)


def set_root(main_root):
    global root
    root = main_root

def abort_processing():
    global abort_flag
    # 延迟 200 毫秒（0.2 秒）执行真正的中止操作
    root.after(1000, lambda: _real_abort_processing())

def _real_abort_processing():
    global abort_flag
    abort_flag = True

def save_config(app_config):
    """
    保存应用程序配置到文件中。

    :param app_config: 应用程序配置对象，包含配置文件路径和配置信息。
    """
    try:
        with open(app_config.config_file, 'w') as f:
            app_config.config.write(f)
    except Exception as e:
        logging.error(f"保存配置文件时出错: {e}")

def select_input_folder(root, input_label, app_config):
    """
    让用户选择输入文件夹，并更新配置和界面显示。

    :param root: 主窗口对象，用于显示文件选择对话框。
    :param input_label: 用于显示输入文件夹路径的标签对象。
    :param app_config: 应用程序配置对象，包含配置信息。
    """
    folder = filedialog.askdirectory(title="选择输入文件夹")
    if folder:
        app_config.input_folder = folder
        input_label.config(text=f"输入文件夹: {app_config.input_folder}")
        update_label_with_wrapping(root, input_label, input_label.cget("text"), "input_label", app_config)
        app_config.config.set('Paths', 'input_folder', app_config.input_folder)
        save_config(app_config)

def select_output_folder(root, output_label, app_config):
    """
    让用户选择输出文件夹，并更新配置和界面显示。

    :param root: 主窗口对象，用于显示文件选择对话框。
    :param output_label: 用于显示输出文件夹路径的标签对象。
    :param app_config: 应用程序配置对象，包含配置信息。
    """
    folder = filedialog.askdirectory(title="选择输出文件夹")
    if folder:
        app_config.output_folder = folder
        output_label.config(text=f"输出文件夹: {app_config.output_folder}")
        update_label_with_wrapping(root, output_label, output_label.cget("text"), "output_label", app_config)
        app_config.config.set('Paths', 'output_folder', app_config.output_folder)
        save_config(app_config)

def select_failed_output_folder(root, failed_output_label, app_config):
    """
    让用户选择转换失败图片的保存路径，并更新配置和界面显示。

    :param root: 主窗口对象，用于显示文件选择对话框。
    :param failed_output_label: 用于显示转换失败图片保存路径的标签对象。
    :param app_config: 应用程序配置对象，包含配置信息。
    """
    folder = filedialog.askdirectory(title="选择转换失败图片保存路径")
    if folder:
        app_config.failed_output_folder = folder
        failed_output_label.config(text=f"转换失败图片保存路径: {app_config.failed_output_folder}")
        update_label_with_wrapping(root, failed_output_label, failed_output_label.cget("text"), "failed_output_label", app_config)
        app_config.config.set('Paths', 'failed_output_folder', app_config.failed_output_folder)
        save_config(app_config)

def on_format_selected(event, format_combobox, app_config,encoder_combobox,encoder_label):

    app_config.output_format = format_combobox.get()
    app_config.config.set('Settings', 'output_format', app_config.output_format) 
    save_config(app_config) # 更新配置文件
    if app_config.output_format == "avif":
        app_config.supported_formats = ['avif']
        encoder_label.pack(side=tk.RIGHT, padx=5)
        encoder_combobox.pack(side=tk.RIGHT, padx=5)
    else:
        encoder_label.pack_forget()
        encoder_combobox.pack_forget()

def on_compression_selected(event, compression_combobox, quality_scale, app_config):
    """
    处理压缩方式选择事件，根据选择的压缩方式启用或禁用质量滑块。

    :param event: 事件对象，通常由下拉框选择事件触发。
    :param compression_combobox: 用于选择压缩方式的下拉框对象。
    :param quality_scale: 用于设置有损压缩质量的滑块对象。
    :param app_config: 应用程序配置对象，包含配置信息。
    """
    app_config.compression_type = compression_combobox.get()
    app_config.config.set('Settings', 'compression_type', app_config.compression_type)  # 更新配置
    save_config(app_config)
    if app_config.compression_type == "有损":
        quality_scale.config(state=tk.NORMAL)
    else:
        quality_scale.config(state=tk.DISABLED)

def on_encoder_selected(event, encoder_combobox, app_config):
    app_config.encoder = encoder_combobox.get()
    app_config.config.set('Settings', 'encoder', app_config.encoder)  # 更新配置
    save_config(app_config)

def on_quality_changed(value, quality_value_label, app_config):
    """
    处理质量滑块值变化事件，更新配置和界面显示。

    :param value: 滑块当前的值。
    :param quality_value_label: 用于显示质量值的标签对象。
    :param app_config: 应用程序配置对象，包含配置信息。
    """
    app_config.quality = int(float(value))
    quality_value_label.config(text=str(app_config.quality))
    app_config.config.set('Settings', 'quality', str(app_config.quality))
    save_config(app_config)

def show_supported_formats(app_config):
    """
    显示支持的图片格式。

    :param app_config: 应用程序配置对象，包含支持的格式信息。
    """
    messagebox.showinfo("支持格式", ", ".join(app_config.supported_formats))

def run_ffmpeg(input_path, output_path, encoder, lossless = -1 , quality = -1):
    
    command = ['ffmpeg', '-i', input_path, '-c:v', encoder, output_path]
    # print('----------------------')
    if lossless == 1:
        # print('无损图片')
        if encoder == 'libaom-av1':
            command = [
                'ffmpeg',
                '-hwaccel' ,'cuda',
                '-i', input_path,
                '-c:v', 'libaom-av1',
                '-lossless', '1',
                '-cpu-used', '0',
                '-row-mt', '1',
                '-pix_fmt', 'yuv420p',
                '-tiles', '2x2',    
                output_path
            ]
        else:
            command = ['ffmpeg', '-i', input_path, '-vcodec', encoder, '-lossless', '1', output_path]
    elif quality != -1:
        # print('有损图片')
        command = ['ffmpeg', '-i', input_path, '-vcodec', encoder, '-q:v', str(quality), output_path]

    # 启动子进程并隐藏控制台窗口 , creationflags=subprocess.CREATE_NO_WINDOW
    result = subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW , capture_output=True, text=True, encoding='utf-8')

    # 打印错误信息
    if result.returncode != 0:
        logging.error(f"Error occurred while processing: {input_path}")
        logging.error(f"stderr: {result.stderr}")
        logging.error(f"stdout: {result.stdout}")
    else:
        logging.info(f"Successfully processed: {input_path}")
        logging.info(f"stdout: {result.stdout}")

def run_ffmpeg_video(input_path, output_path, encoder, lossless = -1 , quality = -1):
    
    # 有损
    # print('有损视频')
    command = [
            'ffmpeg',
            '-i', input_path,  # 输入文件
            '-c:v', 'libaom-av1',  # 使用 libaom-av1 编码器
            '-crf', '20',  # 启用有损压缩
            '-cpu-used', "0",  # 压缩效率
            '-row-mt', '1',  # 启用行级多线程
            '-tiles', "2x2",  # 瓦片分割
            '-pix_fmt', 'yuv420p',  # 使用 yuv420p 像素格式
            '-loop', '0',  # 设置无限循环
            '-vsync', 'vfr',  # 保持原始帧率
            '-an',  # 移除音频
            output_path  # 输出文件
        ]
    
    if lossless == 1:
        # 无损
        # print('无损视频')
        command = [
            'ffmpeg',
            '-i', input_path,  # 输入文件
            '-c:v', 'libaom-av1',  # 使用 libaom-av1 编码器
            '-lossless', '1',  # 启用无损压缩
            '-cpu-used', "0",  # 压缩效率
            '-row-mt', '1',  # 启用行级多线程
            '-tiles', "2x2",  # 瓦片分割
            '-pix_fmt', 'yuv420p',  # 使用 yuv420p 像素格式
            '-loop', '0',  # 设置无限循环
            '-vsync', 'vfr',  # 保持原始帧率
            '-an',  # 移除音频
            output_path  # 输出文件
        ]

    # 启动子进程并隐藏控制台窗口 , creationflags=subprocess.CREATE_NO_WINDOW
    result = subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW , capture_output=True, text=True, encoding='utf-8')

    # 打印错误信息
    if result.returncode != 0:
        logging.error(f"Error occurred while processing: {input_path}")
        logging.error(f"stderr: {result.stderr}")
        logging.error(f"stdout: {result.stdout}")

def process_images(root, progress_bar, abort_button, app_config, rename_file,encoder):
    """
    处理图片转换和压缩任务。

    :param root: 主窗口对象，用于更新界面和显示消息框。
    :param progress_bar: 进度条对象，用于显示处理进度。
    :param abort_button: 中止按钮对象，用于中止处理过程。
    :param app_config: 应用程序配置对象，包含输入输出路径、压缩方式等配置信息。
    :param rename_file: 是否重命名输出文件的标志，1 表示重命名，0 表示覆盖。
    """
    if app_config.output_format == "avif":
        app_config.supported_formats.extend(app_config.supported_formats_vidoe)
                  
    def process_images_thread():
        global abort_flag
        abort_flag = False
        if not app_config.input_folder or not app_config.output_folder:
            messagebox.showerror("错误", "请选择输入和输出文件夹")
            return
        if not os.path.exists(app_config.output_folder):
            os.makedirs(app_config.output_folder)
        if app_config.failed_output_folder and not os.path.exists(app_config.failed_output_folder):
            os.makedirs(app_config.failed_output_folder)

        image_files = []
        for root_dir, _, files in os.walk(app_config.input_folder):
            for file in files:
                
                if any(file.lower().endswith(fmt) for fmt in app_config.supported_formats):
                    image_files.append(os.path.join(root_dir, file))

        total_images = len(image_files)
        if total_images == 0:
            messagebox.showinfo("提示", "未找到支持的图片文件")
            return

        # 显示进度条并增加窗口高度
        abort_button.pack(pady=10)
        progress_bar.pack(pady=10)
        progress_bar['maximum'] = total_images
        app_config.window_height += 80  # 假设进度条使窗口高度增加 30 像素

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - app_config.window_width) // 2
        y = (screen_height - app_config.window_height) // 2
        root.geometry(f"{app_config.window_width}x{app_config.window_height}+{x}+{y}")

        root.update()

        success_count = 0
        failed_count = 0  # 新增：记录失败图片的数量

        temp_image_folder = os.path.join(app_config.config_folder, "temp_image")
        if not os.path.exists(temp_image_folder):
            os.makedirs(temp_image_folder)
        # print(f"image_files:{image_files}")
        for index, image_path in enumerate(image_files):
            if abort_flag:
                break
            try:
                # 处理文件输出路径
                relative_path = os.path.relpath(image_path, app_config.input_folder)
                output_subfolder = os.path.join(app_config.output_folder, os.path.dirname(relative_path))
                try:
                    if not os.path.exists(output_subfolder):
                        os.makedirs(output_subfolder)
                except PermissionError:
                    logging.error(f"没有权限创建文件夹 {output_subfolder}，跳过处理")
                    failed_count += 1
                    continue
                
                # 转换 avif start       
                if app_config.output_format == "avif":
                   
                    output_path = os.path.splitext(os.path.join(output_subfolder, os.path.basename(image_path)))[0] + ".avif"

                    output_path = rename_files(rename_file,output_path)

                    # print(f"output_path:{output_path}")
                    # 处理视频文件
                    base_name, ext  = os.path.splitext(image_path)
                    # print(f"ext:{ext}")
                    # 视频压缩转换逻辑   
                    if ext in app_config.supported_formats_vidoe :
                        # print("视频逻辑")
                        # 处理视频文件
                        if app_config.compression_type == "无损":

                            run_ffmpeg_video(image_path, output_path, encoder, lossless=1)
                        else:
                            # 有损压缩使用 -q 选项控制质量
                            run_ffmpeg_video(image_path, output_path, encoder)
                     
                    else:
                    # 图片压缩转换逻辑    
                        # 打开图像并确保高度为偶数
                        temp_image_path = evenSize(image_path,temp_image_folder,ext)
                  
                        if app_config.compression_type == "无损":
                            # 无损压缩使用 -lossless 选项
                   
                            run_ffmpeg(temp_image_path, output_path, encoder, lossless=1)
                        
                        elif app_config.compression_type == "有损":
                            # 有损压缩使用 -q 选项控制质量
                            run_ffmpeg(temp_image_path, output_path, encoder, quality=app_config.quality)
                         
                        elif app_config.compression_type == "自动":
                            # 自动模式 使用编码器默认参数  以废弃 感觉没人会用这个
                            run_ffmpeg(temp_image_path, output_path, encoder)
                # 转换 avif end
                else:
                # 转换 other start 
                    output_path = os.path.splitext(os.path.join(output_subfolder, os.path.basename(image_path)))[0] + f".{app_config.output_format}"

                    output_path = rename_files(rename_file,output_path)

                    # 打开图片并进行转换
                    img = Image.open(image_path)
                    if app_config.compression_type == "无损":
                        img.save(output_path, format=app_config.output_format, lossless=True)
                    elif app_config.compression_type == "有损":
                        img.save(output_path, format=app_config.output_format, quality=app_config.quality)
                    elif app_config.compression_type == "自动":
                        # 自动判断是否需要无损压缩
                        img.save(output_path, format=app_config.output_format)

                success_count += 1

                # 转换 other end
            except Exception as e:
                failed_count += 1  # 新增：失败图片数量加 1
                tb_info = traceback.format_exc()
                logging.error(f"处理图片 {image_path} 时出错: {e}\n详细堆栈信息:\n{tb_info}")
                if app_config.failed_output_folder:
                    shutil.copy(image_path, os.path.join(app_config.failed_output_folder, os.path.basename(image_path)))
            # 更新进度条
            progress_bar['value'] = index + 1
            root.update()

        # 隐藏进度条并减少窗口高度
        progress_bar.pack_forget()
        abort_button.pack_forget()

        app_config.window_height -= 80  # 恢复窗口高度
        app_config.window_height = max(app_config.window_height, app_config.min_window_height)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - app_config.window_width) // 2
        y = (screen_height - app_config.window_height) // 2
        root.geometry(f"{app_config.window_width}x{app_config.window_height}+{x}+{y}")

        #os.remove(temp_image_folder)
        if abort_flag:
            if failed_count > 0:
                messagebox.showwarning("中止", f"{success_count}张图片处理完成，处理过程已中止，有 {failed_count} 张图片处理失败，失败的图片已保存到 {app_config.failed_output_folder}")
            else:
                messagebox.showwarning("中止", f"{success_count}张图片处理完成，处理过程已中止")
        elif failed_count > 0:
            messagebox.showwarning("完成", f"{success_count}张图片处理完成，但有 {failed_count} 张图片处理失败，失败的图片已保存到 {app_config.failed_output_folder}")
        else:
            messagebox.showinfo("完成", f"{success_count}张图片处理完成")
    # 启动一个新的线程来执行处理任务
    thread = threading.Thread(target=process_images_thread)
    thread.start()

def rename_files(rename_file, output_path):
    # 处理重命名逻辑
    if rename_file:
        counter = 1
        base_name, ext = os.path.splitext(output_path)
        while os.path.exists(output_path):
            output_path = f"{base_name} - 副本{counter}{ext}"
            counter += 1
    else:
        if os.path.exists(output_path):
            os.remove(output_path)
    return output_path        

def evenSize(image_path,temp_image_folder,ext):
    img = Image.open(image_path)
    width, height = img.size
    if width % 2 != 0:
        width = width - 1
    if height % 2 != 0:
        height = height - 1
    img = img.resize((width, height))
    # 保存临时图像
    temp_image_path = os.path.join(temp_image_folder, f"temp_image{ext}")
    if ext.lower() == '.jpg':
        ext = 'JPEG'
    else:
        ext = ext[1:]
    img.save(temp_image_path, format=f"{ext}")

    return temp_image_path   
     
def update_label_with_wrapping(root, label, text, label_key, app_config):
    """
    更新标签文本，并根据文本换行情况调整窗口高度
    :param root: 主窗口对象
    :param label: 要更新的标签对象
    :param text: 要设置到标签上的文本
    :param label_key: 标签的唯一标识，用于记录该标签的高度变化
    :param app_config: 应用程序的配置对象，包含窗口大小、标签高度变化等信息
    """
    label.config(wraplength=app_config.window_width - 20)

    original_height = app_config.height_increases[label_key]

    label.config(text=text)
    label.update_idletasks()
    new_height = label.winfo_reqheight()
    height_difference = new_height - original_height
    if height_difference != 0:
        app_config.height_increases[label_key] = new_height
        app_config.window_height += height_difference 

    app_config.window_height = max(app_config.window_height, app_config.min_window_height)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - app_config.window_width) // 2
    y = (screen_height - app_config.window_height) // 2
    root.geometry(f"{app_config.window_width}x{app_config.window_height}+{x}+{y}")

