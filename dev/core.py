import os
import shutil
import traceback
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image
from init import app_config,info_logger,error_logger


class ImageConverter:
    def __init__(self,root):
        self.root = root
        self.abort_flag = False
        self._success_count = 0
        self._failed_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.processes = []
        self.end_flag = True # 允许自动弹出结束
        
    def run_ffmpeg(self,input_path, output_path, lossless = -1):
        encoder = app_config.encoder
        quality = app_config.quality
        # 默认
        command = ['ffmpeg', '-i', input_path, '-c:v', encoder, output_path]
        if lossless == 1:
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
            command = ['ffmpeg', '-i', input_path, '-vcodec', encoder, '-q:v', str(quality), output_path]

        # 启动子进程并隐藏控制台窗口 , creationflags=subprocess.CREATE_NO_WINDOW
        process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW , 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    encoding='utf-8')

        return process

    def run_ffmpeg_video(self,input_path, output_path, lossless = -1):
        print("开始处理视频")
        # 有损
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
            command = [
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
            command1 = [
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
        # result = subprocess.run(command, creationflags=subprocess.CREATE_NO_WINDOW , capture_output=True, text=True, encoding='utf-8')
        process = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW , 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    encoding='utf-8')
        return process


    def process_single_image(self, image_path,x):
        """
        处理单个图片文件的转换和压缩任务。

        :param image_path: 要处理的图片文件路径。
        :x: 线程标记
        """
        try:
            # 处理文件输出路径
            relative_path = os.path.relpath(image_path, app_config.input_folder)
            output_subfolder = os.path.join(app_config.output_folder, os.path.dirname(relative_path))
            try:
                if not os.path.exists(output_subfolder):
                    os.makedirs(output_subfolder)
            except PermissionError:
                error_logger.error(f"没有权限创建子文件夹 {output_subfolder}，跳过处理")
                return False
                
            
            # 转换 avif start ===========================================================================      
            if app_config.output_format == "avif":
            
                output_path = os.path.splitext(os.path.join(output_subfolder, os.path.basename(image_path)))[0] + ".avif"

                output_path = self.rename_files(output_path)

                # 判断源文件是图片还是视频
                base_name, ext  = os.path.splitext(image_path)
  
                if ext in app_config.supported_read_formats_vidoe :
                
                    # 处理视频文件
                    if app_config.compression_type == "无损":

                        process  = self.run_ffmpeg_video(image_path, output_path, lossless=1)
                  
                
                else:
                    
                    # 打开图像并确保高度为偶数
                    temp_image_path = self.evenSize(image_path,ext,x)
                    # 处理图片文件
                    if app_config.compression_type == "无损":
                        # 无损压缩使用 -lossless 选项
            
                        process = self.run_ffmpeg(temp_image_path, output_path, lossless=1)
                    
                    elif app_config.compression_type == "有损":
                        # 有损压缩使用 -q 选项控制质量
                        process = self.run_ffmpeg(temp_image_path, output_path)
                    
                    elif app_config.compression_type == "自动":
                        # 自动模式 使用编码器默认参数  以废弃 感觉没人会用这个
                        process = self.run_ffmpeg(temp_image_path, output_path)
                if len(self.processes) < app_config.max_ffmpeg_processes:
                    self.processes.append(process)
              
                    def handle_process_output(process, image_path,output_path):
                        stdout, stderr = process.communicate()
                        self.ffmpeg_result(process, image_path,stdout,stderr,output_path)
                        self.processes.remove(process)
                        
                    thread = threading.Thread(target=handle_process_output, args=(process, image_path,output_path))
                    thread.start()
                else:  
                    stdout, stderr = process.communicate()
                    self.ffmpeg_result(process, image_path,stdout,stderr,output_path)
               
    
            # 转换 avif end ===========================================================================
            else:
            # 转换 other start 
                output_path = os.path.splitext(os.path.join(output_subfolder, os.path.basename(image_path)))[0] + f".{app_config.output_format}"

                output_path = self.rename_files(output_path)

                # 打开图片并进行转换
                img = Image.open(image_path)
                if app_config.compression_type == "无损":
                    img.save(output_path, format=app_config.output_format, lossless=True)
                elif app_config.compression_type == "有损":
                    img.save(output_path, format=app_config.output_format, quality=app_config.quality)
                elif app_config.compression_type == "自动":
                    # 自动判断是否需要无损压缩
                    img.save(output_path, format=app_config.output_format)

                self.success_count += 1

            # 转换 other end
        except Exception as e:
            tb_info = traceback.format_exc()
            error_logger.error(f"处理图片 {image_path} 时出错: {e}\n详细堆栈信息:\n{tb_info}")
            if app_config.failed_output_folder and app_config.failed_output_folder != app_config.input_folder:
              
                shutil.copy(image_path, os.path.join(app_config.failed_output_folder, os.path.basename(image_path)))
            self.failed_count += 1
           
    def process_images(self,frame3,progress_bar,IA):
        """
        处理图片转换和压缩任务。

        """
        self.end_flag = True # 允许自动弹出结束
        self._success_count = 0
        self._failed_count = 0
        self.success_count = 0
        self.failed_count = 0

        # 启动一个新的线程来执行处理任务
        def process_images_thread():
            # 若输出格式为avif 读取添加视频格式
            supported_formats = app_config.supported_read_formats_image
            if app_config.output_format == "avif":
                supported_formats.extend(app_config.supported_read_formats_vidoe)
            # -------------- 三个目录 ------------------
            if not app_config.input_folder or not app_config.output_folder:
                messagebox.showerror("错误", "请选择输入和输出文件夹")
                return
            if not os.path.exists(app_config.output_folder):
                os.makedirs(app_config.output_folder)
            if app_config.failed_output_folder and not os.path.exists(app_config.failed_output_folder):
                os.makedirs(app_config.failed_output_folder)  

            # -------------- 读取需要压制的图片 ----------------------
            image_files = []
            for root_dir, _, files in os.walk(app_config.input_folder):
                for file in files:
                    if any(file.lower().endswith(fmt) for fmt in supported_formats):
                        image_files.append(os.path.join(root_dir, file))

            total_images = len(image_files)
            if total_images == 0:
                messagebox.showinfo("提示", "未找到支持的图片文件")
                return
            
            # 显示进度条并增加窗口高度
            frame3.pack(pady=5)
            IA.change_window_height("add",app_config.progress_bar_height)
            progress_bar['maximum'] = total_images
            progress_bar['value'] = 0
            self.root.update()
            self.IA = IA
            self.progress_bar = progress_bar
            self.frame3 = frame3
            # -------------- 处理图片 ----------------------
            for image_path in image_files:
                if self.abort_flag:
                    break
                self.process_single_image(image_path,1)  
      
       
        thread = threading.Thread(target=process_images_thread)
        thread.start()

    def rename_files(self, output_path):
        # 处理重命名逻辑
        if app_config.rename:
            counter = 1
            base_name, ext = os.path.splitext(output_path)
            while os.path.exists(output_path):
                output_path = f"{base_name} - 副本{counter}{ext}"
                counter += 1
        else:
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except PermissionError as e:
                raise PermissionError(f"没有权限删除文件 {output_path}，跳过处理") from e
        return output_path        

    def abort_processing(self):
        self.end_flag = False
        self.frame3.pack_forget()
        self.IA.change_window_height("sub",app_config.progress_bar_height)
        self.abort_flag = True
        for process in self.processes:
            process.terminate()     
        self.remove_temp_files()
        # 更强的强制中止子进程
        # process.kill()
        if self.failed_count > 0 :
            messagebox.showwarning("中止", f"{self.success_count}张图片处理完成，但有 {self.failed_count} 张图片处理失败，失败的图片已保存到 {app_config.failed_output_folder}")
        else:
            messagebox.showinfo("中止", f"{self.success_count}张图片处理完成")

    def evenSize(self,image_path,ext,x):
        img = Image.open(image_path)
        width, height = img.size
        if width % 2 != 0:
            width = width - 1
        if height % 2 != 0:
            height = height - 1
        img = img.resize((width, height))
        # 保存临时图像
        temp_image_path = os.path.join(app_config.temp_image_folder, f"temp_image{ext}")
        temp_image_path = self.rename_temp_files(temp_image_path,x)
        if ext.lower() == '.jpg':
            ext = 'JPEG'
        else:
            ext = ext[1:]
        if ext.upper() == 'JPEG':  
            if img.mode == "RGBA":
                img = img.convert("RGB")      
        img.save(temp_image_path, format=f"{ext}".upper())

        return temp_image_path  

    def rename_temp_files(self, output_path,x):
        # 处理重命名逻辑
        
        counter = 1
        base_name, ext = os.path.splitext(output_path)
        while os.path.exists(output_path):
            output_path = f"{base_name} - {x} - {counter}{ext}"
            counter += 1
       
        return output_path        
 
    def remove_temp_files(self):
        # 删除临时文件
        if os.path.exists(app_config.temp_image_folder):
            for filename in os.listdir(app_config.temp_image_folder):
                file_path = os.path.join(app_config.temp_image_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    error_logger.error(f"Failed to delete {file_path}. Reason: {e}")
    
    def ffmpeg_result(self,process, image_path,stdout,stderr,output_path):

        if process.returncode != 0:
            # 检查输出文件是否存在且非空
            output_file_exists = os.path.exists(output_path) and os.path.getsize(output_path) > 0

            if output_file_exists:
                # 非零返回值，但输出文件存在且非空，认为成功

                info_logger.info(f"Warning: Non-zero return code1111 ({process.returncode}), but output file exists: {image_path}")
                info_logger.info(f"stdout: {stdout}")
                info_logger.info(f"stderr: {stderr}")
                self.success_count += 1
            else:
                # 非零返回值且输出文件不存在，认为失败
                error_logger.error(f"errorcode : {process.returncode}, ------Error occurred while processing: {image_path}")
                error_logger.error(f"stderr: {stderr}")
                error_logger.error(f"stdout: {stdout}")

                self.failed_count += 1
                if app_config.failed_output_folder and app_config.failed_output_folder != app_config.input_folder:
                    shutil.copy(image_path, os.path.join(app_config.failed_output_folder, os.path.basename(image_path)))
        else:
            info_logger.info(f"Successfully processed: {image_path}")
            info_logger.info(f"stdout: {stdout}")
            self.success_count += 1

    @property
    def success_count(self):
        return self._success_count

    @success_count.setter
    def success_count(self, value):
        old_value = self._success_count
        self._success_count = value
        if value > old_value:
            self._update_progress_bar()
        
    @property
    def failed_count(self):
        return self._failed_count

    @failed_count.setter
    def failed_count(self, value):
        old_value = self._failed_count
        self._failed_count = value
        if value > old_value:
            self._update_progress_bar()

    def _update_progress_bar(self):
        if self.progress_bar:
            total = self._success_count + self._failed_count
            self.progress_bar['value'] = total
            self.root.update()
            #self.root.update_idletasks()  # 刷新界面
            print(total)
            if total == self.progress_bar['maximum'] and self.end_flag:
                print('处理完成')
                app_config.input_button_item.config(state=tk.NORMAL)
                app_config.output_button_item.config(state=tk.NORMAL)
                app_config.failed_output_button_item.config(state=tk.NORMAL)
                app_config.format_combobox_item.config(state=tk.NORMAL)
                app_config.encoder_combobox_item.config(state=tk.NORMAL)
                app_config.compression_combobox_item.config(state=tk.NORMAL)
                app_config.quality_scale_item.config(state=tk.NORMAL)
                app_config.rename_checkbox_item.config(state=tk.NORMAL)
                app_config.process_button_item.config(state=tk.NORMAL)
                self.end_process()

    def end_process(self):
        self.frame3.pack_forget()
        self.IA.change_window_height("sub",app_config.progress_bar_height)
        if self.failed_count > 0:
            messagebox.showwarning("完成", f"{self.success_count}张图片处理完成，但有 {self.failed_count} 张图片处理失败，失败的图片已保存到 {app_config.failed_output_folder}")
        else:
            messagebox.showinfo("完成", f"{self.success_count}张图片处理完成")
        # self.IA.change_window_height("sub",app_config.progress_bar_height)
        self.remove_temp_files()     