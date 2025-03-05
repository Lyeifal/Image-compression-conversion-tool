import tkinter as tk
from tkinter import  ttk
import webp_init
import webp_core

# 创建主窗口
root = tk.Tk()
root.title("图片转换Webp工具")
# 将主窗口对象传递给 webp_core 模块
webp_core.set_root(root)

# 创建输入文件夹选择按钮和标签
input_button = tk.Button(root, text="选择输入文件夹", command=lambda: webp_core.select_input_folder(root, input_label, webp_init.app_config))
input_button.pack(pady=5)
input_label = tk.Label(root, text=f"输入文件夹: {webp_init.app_config.input_folder if webp_init.app_config.input_folder else '未选择'}", wraplength=webp_init.app_config.window_width - 20)
input_label.pack()
# 初始化时检查输入标签文本是否需要换行
webp_core.update_label_with_wrapping(root, input_label, input_label.cget("text"), "input_label", webp_init.app_config)

# 创建输出文件夹选择按钮和标签
output_button = tk.Button(root, text="选择输出文件夹", command=lambda: webp_core.select_output_folder(root, output_label, webp_init.app_config))
output_button.pack(pady=5)
output_label = tk.Label(root, text=f"输出文件夹: {webp_init.app_config.output_folder if webp_init.app_config.output_folder else '未选择'}", wraplength=webp_init.app_config.window_width - 20)
output_label.pack()
# 初始化时检查输出标签文本是否需要换行
webp_core.update_label_with_wrapping(root, output_label, output_label.cget("text"), "output_label", webp_init.app_config)

# 创建失败图片保存路径选择按钮和标签
failed_output_button = tk.Button(root, text="选择转换失败图片保存路径", command=lambda: webp_core.select_failed_output_folder(root, failed_output_label, webp_init.app_config))
failed_output_button.pack(pady=5)
failed_output_label = tk.Label(root, text=f"转换失败图片保存路径: {webp_init.app_config.failed_output_folder if webp_init.app_config.failed_output_folder else '未选择'}", wraplength=webp_init.app_config.window_width - 20)
failed_output_label.pack()
# 初始化时检查失败输出标签文本是否需要换行
webp_core.update_label_with_wrapping(root, failed_output_label, failed_output_label.cget("text"), "failed_output_label", webp_init.app_config)

# 创建一个框架来容纳输出格式和编码器的标签与下拉框
format_frame = tk.Frame(root)
format_frame2 = tk.Frame(root)
format_frame.pack(pady=5)
format_frame2.pack(pady=5)

# 选择输出格式的下拉框
format_label = tk.Label(format_frame, text="选择输出格式:")
format_label.pack(side=tk.LEFT, padx=5)
format_combobox = ttk.Combobox(format_frame2, values=["webp", "png", "jpeg", "jpeg2000",'avif'])
format_combobox.set(webp_init.app_config.output_format)
format_combobox.bind("<<ComboboxSelected>>", lambda event: webp_core.on_format_selected(event, format_combobox, webp_init.app_config,encoder_combobox,encoder_label))
format_combobox.pack(side=tk.LEFT, padx=5)

# 编码器选择的下拉框
encoder_label = tk.Label(format_frame, text="选择编码器:")
encoder_combobox = ttk.Combobox(format_frame2, values=["libsvtav1", "libaom-av1"])
encoder_combobox.set(webp_init.app_config.encoder)
encoder_combobox.bind("<<ComboboxSelected>>", lambda event: webp_core.on_encoder_selected(event, encoder_combobox, webp_init.app_config))
# 初始时隐藏software
encoder_label.pack_forget()  
encoder_combobox.pack_forget()  
if webp_init.app_config.output_format == "avif":
    encoder_label.pack(side=tk.RIGHT, padx=5)
    encoder_combobox.pack(side=tk.RIGHT, padx=5)

# 选择压缩方式的下拉框
compression_label = tk.Label(root, text="选择压缩方式:")
compression_label.pack(pady=5)
compression_combobox = ttk.Combobox(root, values=["无损", "有损"])
compression_combobox.set(webp_init.app_config.compression_type)
# 绑定事件时传递 quality_scale 参数
compression_combobox.bind("<<ComboboxSelected>>", lambda event: webp_core.on_compression_selected(event, compression_combobox, quality_scale, webp_init.app_config))
compression_combobox.pack(pady=5)

# 质量滑块
quality_label = tk.Label(root, text="有损压缩质量 (1-100):")
quality_label.pack(pady=1)
# 使用 ttk.Scale 组件
style = ttk.Style()
style.theme_use('default')
# 配置可用状态的样式
style.configure('TScale', background="lightgray", troughcolor="lightblue", sliderrelief="raised")
# 配置禁用状态的样式
style.map('TScale',
          background=[('disabled', 'gray')],
          troughcolor=[('disabled', 'darkgray')],
          sliderrelief=[('disabled', 'flat')])
# 新增：用于显示滑块值的标签
quality_value_label = tk.Label(root, text=str(webp_init.app_config.quality))
quality_value_label.pack(pady=1)

quality_scale = ttk.Scale(root, from_=1, to=100, orient=tk.HORIZONTAL, command=lambda value: webp_core.on_quality_changed(value, quality_value_label, webp_init.app_config))
quality_scale.set(webp_init.app_config.quality)
quality_scale.config(state=tk.DISABLED)
quality_scale.pack(pady=1)
if webp_init.app_config.compression_type == "有损":
    quality_scale.config(state=tk.NORMAL)

# 添加是否重命名文件的勾选框
rename_var = tk.IntVar()
rename_checkbox = tk.Checkbutton(root, text="重命名输出文件", variable=rename_var)
rename_checkbox.pack(pady=5)

format_frame3 = tk.Frame(root)
format_frame3.pack(pady=5)
# 创建显示支持格式的按钮
show_formats_button = tk.Button(format_frame3, text="支持格式", command=lambda: webp_core.show_supported_formats(webp_init.app_config))
show_formats_button.pack(side=tk.LEFT, padx=5)

# 创建处理图片的按钮
# 修改：将 quality_scale 替换为 progress_bar
process_button = tk.Button(format_frame3, text="开始处理图片", command=lambda: webp_core.process_images(root, progress_bar, abort_button ,webp_init.app_config, rename_var.get(),encoder_combobox.get()))
process_button.pack(side=tk.RIGHT, padx=5)

# 创建进度条
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')

# 创建中止按钮，初始状态为隐藏
abort_button = tk.Button(root, text="中止处理", command=lambda: root.after(200,webp_core.abort_processing))
abort_button.pack_forget()
# 添加作者、邮箱和打包日期信息
author_info = f"qoph.fun,AKXL718@163.com,2025-03-05"
author_label = tk.Label(root, text=author_info)
author_label.pack(side=tk.BOTTOM, pady=10)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - webp_init.app_config.window_width) // 2
y = (screen_height - webp_init.app_config.window_height) // 2
root.geometry(f"{webp_init.app_config.window_width}x{webp_init.app_config.window_height}+{x}+{y}")

# 运行主循环
root.mainloop()

# 在程序结束时保存配置文件
webp_init.app_config.save_config()
