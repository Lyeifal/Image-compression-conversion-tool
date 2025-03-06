from tkinter import filedialog, messagebox
from init import error_logger,app_config

class interaction:

    def __init__(self, root):
        self.root = root
    def save_config(self,app_config):
        """
        保存应用程序配置到文件中。

        :param app_config: 应用程序配置对象，包含配置文件路径和配置信息。
        """
        try:
            with open(app_config.config_file, 'w') as f:
                app_config.config.write(f)
        except Exception as e:
            error_logger.error(f"保存配置文件时出错: {e}")

    def select_input_folder(self,input_label):
        """
        让用户选择输入文件夹，并更新配置和界面显示。

        :param root: 主窗口对象，用于显示文件选择对话框。
        :param input_label: 用于显示输入文件夹路径的标签对象。
        """
        folder = filedialog.askdirectory()
        if folder:
            app_config.input_folder = folder
            input_label.config(text=f"输入文件夹: {app_config.input_folder}")
            app_config.config.set('Paths', 'input_folder', folder)
            self.update_label_with_wrapping(input_label, "input_label")
            self.save_config(app_config)

    def select_output_folder(self,output_label):
        """
        让用户选择输出文件夹，并更新配置和界面显示。

        :param root: 主窗口对象，用于显示文件选择对话框。
        :param output_label: 用于显示输出文件夹路径的标签对象。
        """
        folder = filedialog.askdirectory()
        if folder:
            app_config.output_folder = folder
            output_label.config(text=f"输出文件夹: {app_config.output_folder}")
            app_config.config.set('Paths', 'output_folder', folder)
            self.update_label_with_wrapping(output_label, "output_label")
            self.save_config(app_config)

    def select_failed_output_folder(self,failed_output_label):
        """
        让用户选择转换失败图片的保存路径，并更新配置和界面显示。

        :param root: 主窗口对象，用于显示文件选择对话框。
        :param failed_output_label: 用于显示转换失败图片保存路径的标签对象。
        """
        folder = filedialog.askdirectory()
        if folder:
            app_config.failed_output_folder = folder
            failed_output_label.config(text=f"转换失败图片保存路径: {app_config.failed_output_folder}")
            app_config.config.set('Paths', 'failed_output_folder', folder)
            self.update_label_with_wrapping(failed_output_label, "failed_output_label")
            self.save_config(app_config)

    def on_format_selected(self, event, format_combobox,format_frame):
        """
        处理输出格式选择事件，根据选择的输出格式显示或隐藏编码器选择组件。

        :param event: 事件对象，通常由下拉框选择事件触发。
        :param format_combobox: 用于选择输出格式的下拉框对象。
        :param encoder_combobox: 用于选择编码器的下拉框对象。
        :param encoder_label: 用于显示编码器选择提示的标签对象。
        """
        selected_format = format_combobox.get()
        
        if selected_format == "avif" and app_config.output_format != "avif":
            format_frame.pack(pady=3)
            self.change_window_height("add",app_config.combobox_height)
        elif selected_format != "avif" and app_config.output_format == "avif":
            format_frame.pack_forget()
            self.change_window_height("sub",app_config.combobox_height)

        app_config.output_format = selected_format
        app_config.config.set('Settings', 'output_format', selected_format)
        self.save_config(app_config)

    def on_compression_selected(self, event, compression_combobox,format_frame4):
        """
        处理压缩方式选择事件，根据选择的压缩方式启用或禁用质量滑块。

        :param event: 事件对象，通常由下拉框选择事件触发。
        :param compression_combobox: 用于选择压缩方式的下拉框对象。
        :param quality_scale: 用于设置有损压缩质量的滑块对象。
        """
        selected_compression = compression_combobox.get()
       
        if selected_compression == "有损" and app_config.compression_type!= "有损":
            format_frame4.pack(pady=3)
            self.change_window_height("add",app_config.scale_height)
        elif selected_compression!= "有损" and app_config.compression_type == "有损":
            format_frame4.pack_forget()
            self.change_window_height("sub",app_config.scale_height)
        app_config.compression_type = selected_compression
        app_config.config.set('Settings', 'compression_type', selected_compression)
        self.save_config(app_config)

    def on_encoder_selected(self, event, encoder_combobox,three_frame):
        selected_encoder = encoder_combobox.get()
        if selected_encoder == "libaom-av1" and app_config.encoder != "libaom-av1":
            three_frame.pack(pady=3)
            self.change_window_height("add",app_config.checkbox_height)
        elif selected_encoder!= "libaom-av1" and app_config.encoder == "libaom-av1":
            three_frame.pack_forget()
            self.change_window_height("sub",app_config.checkbox_height)
        app_config.encoder = selected_encoder
        app_config.config.set('Settings', 'encoder', selected_encoder)
        self.save_config(app_config)

    def on_quality_changed(self, value, quality_label):
        """
        处理质量滑块值变化事件，更新配置和界面显示。

        :param value: 滑块当前的值。
        :param quality_label: 用于显示质量值的标签对象。
        """
        quality = int(float(value))
        app_config.quality = quality
        app_config.config.set('Settings', 'quality', str(quality))
        self.save_config(app_config)
        quality_label.config(text=f"有损压缩质量 (1-100):{str(quality)}")

    def on_cuda_checkbox_changed(self,var):
        """
        处理 CUDA 复选框状态变化事件，根据复选框状态启用或禁用编码器选择组件。

        :param var: 复选框的状态变量。
        """
        app_config.cuda = var
        app_config.config.set('Settings', 'cuda', str(var))
        self.save_config(app_config)
      
    def on_rename_checkbox_changed(self,var):
        """
        处理是否重命名文件复选框状态变化事件，根据复选框状态启用或禁用编码器选择组件。

        :param var: 复选框的状态变量。
        """
        app_config.rename = var
        app_config.config.set('Settings', 'rename', str(var))
        self.save_config(app_config)

    def show_supported_formats(self):
        """
        显示支持的图片格式。

        :param app_config: 应用程序配置对象，包含支持的格式信息。
        """
        messagebox.showinfo("支持格式", "支持的图片格式:".join(app_config.supported_read_formats_image)+
                            "\n 支持的视频格式(仅支持avif输出):".join(app_config.supported_read_formats_vidoe))
                            
    def update_label_with_wrapping(self, label, label_key):
        """
        更新标签文本，并根据文本换行情况调整窗口高度
        :param root: 主窗口对象
        :param label: 要更新的标签对象
        :param label_key: 标签的唯一标识，用于记录该标签的高度变化
        """
        label.config(wraplength=app_config.wraplength)

        original_height = app_config.height_increases[label_key]

        label.config(text= label.cget("text"))
        label.update_idletasks()
        new_height = label.winfo_reqheight()
        height_difference = new_height - original_height
        if height_difference != 0:
            app_config.height_increases[label_key] = new_height
            app_config.window_height += height_difference 

        app_config.window_height = max(app_config.window_height, app_config.min_window_height)

        self.reset_window_position()

    def change_window_height(self,type,value):
        """
        调整窗口高度
        :param type: 调整类型，"add" 表示增加高度，"sub" 表示减少高度
        :param value: 调整的高度值
        """
        if type == "add":
            app_config.window_height += value
        elif type == "sub":
            app_config.window_height = max(app_config.window_height - value, app_config.min_window_height)
        else:
            error_logger.error(f"不支持的调整类型: {type}")
            return
        self.reset_window_position()
        self.save_config(app_config)

    def reset_window_position(self):
        """
        重置窗口位置
        :param root: 主窗口对象
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()   
        x = (screen_width - app_config.window_width) // 2
        y = (screen_height - app_config.window_height) // 2
        self.root.geometry(f"{app_config.window_width}x{app_config.window_height}+{x}+{y}")

        
