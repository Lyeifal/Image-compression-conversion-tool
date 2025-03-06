import tkinter as tk
from tkinter import ttk
from interaction import interaction  
from core import ImageConverter 
from init import app_config


# 创建主窗口
root = tk.Tk()
root.title(f"{app_config.title}")
IA = interaction(root)
IC = ImageConverter(root)
# -------------------------------------------------- 输入输出路径 -------------------------------------------------
# 创建输入文件夹选择按钮和标签
input_button = ttk.Button(root, text="选择输入文件夹", command=lambda: IA.select_input_folder(input_label))
input_button.pack(pady=5)
input_label = ttk.Label(root, text=f"输入文件夹: {app_config.input_folder if app_config.input_folder else '未选择'}", wraplength=app_config.wraplength)
input_label.pack()
# 初始化时检查输入标签文本是否需要换行
IA.update_label_with_wrapping(input_label,"input_label")

# 创建输出文件夹选择按钮和标签
output_button = ttk.Button(root, text="选择输出文件夹", command=lambda: IA.select_output_folder(output_label))
output_button.pack(pady=5)
output_label = ttk.Label(root, text=f"输出文件夹: {app_config.output_folder if app_config.output_folder else '未选择'}", wraplength=app_config.wraplength)
output_label.pack()
# 初始化时检查输出标签文本是否需要换行
IA.update_label_with_wrapping(output_label,"output_label")

# 创建失败图片保存路径选择按钮和标签
failed_output_button = ttk.Button(root, text="选择转换失败图片保存路径", command=lambda: IA.select_failed_output_folder(failed_output_label))
failed_output_button.pack(pady=5)
failed_output_label = ttk.Label(root, text=f"转换失败图片保存路径: {app_config.failed_output_folder if app_config.failed_output_folder else '未选择'}", wraplength=app_config.wraplength)
failed_output_label.pack()
# 初始化时检查失败输出标签文本是否需要换行
IA.update_label_with_wrapping(failed_output_label,"failed_output_label")

# --------------------------------------------------输出格式 -------------------------------------------------
frame1 = ttk.Frame(root)
frame1.pack(pady=(8,1))
format_frame = ttk.Frame(frame1)
format_frame.pack(pady=3)
# 选择输出格式的下拉框
format_label = ttk.Label(format_frame, text="选择输出格式:",width = app_config.label_width)
format_label.pack(side=tk.LEFT, padx=5)
format_combobox = ttk.Combobox(format_frame, values=app_config.supported_output_formats)
format_combobox.set(app_config.output_format)
format_combobox.bind("<<ComboboxSelected>>", lambda event: IA.on_format_selected(event, format_combobox,format_frame2))
format_combobox.pack(side=tk.RIGHT, padx=5)
# ------------------------------------------------------- 编码器 ------------------------------------------------
format_frame2 = ttk.Frame(frame1)
format_frame2.pack_forget()

three_frame1 = ttk.Frame(format_frame2)
three_frame1.pack(side=tk.TOP, padx=5)


# 编码器选择的下拉框
encoder_label = ttk.Label(three_frame1, text="选择编码器:",width = app_config.label_width)
encoder_combobox = ttk.Combobox(three_frame1, values=app_config.supported_encoder_formats)
encoder_combobox.set(app_config.encoder)
encoder_combobox.bind("<<ComboboxSelected>>", lambda event: IA.on_encoder_selected(event, encoder_combobox,three_frame2))
encoder_label.pack(side=tk.LEFT, padx=5)
encoder_combobox.pack(side=tk.RIGHT, padx=5) 
if app_config.output_format == "avif":
    format_frame2.pack(pady=5)
    IA.change_window_height("add",app_config.combobox_height)   
# CUDA GPU硬件加速
three_frame2 = ttk.Frame(format_frame2)
three_frame2.pack_forget()

cuda_var= tk.IntVar()
cuda_var.set(app_config.cuda)
cuda_checkbox = ttk.Checkbutton(three_frame2, text="cuda GPU硬件加速", variable=cuda_var,command=lambda:IA.on_cuda_checkbox_changed(cuda_var.get()))
cuda_checkbox.pack(pady=5)
if app_config.encoder == "libaom-av1":
    three_frame2.pack(side=tk.BOTTOM, padx=5)
    IA.change_window_height("add",app_config.checkbox_height)
# ------------------------------------------------------- 压缩方式 ------------------------------------------------  
frame2 = ttk.Frame(root) 
frame2.pack(pady=1) 
format_frame3 = ttk.Frame(frame2)
format_frame3.pack(pady=3)
# 选择压缩方式的下拉框
compression_label = ttk.Label(format_frame3, text="选择压缩方式:",width = app_config.label_width)
compression_label.pack(side=tk.LEFT, padx=5)
compression_combobox = ttk.Combobox(format_frame3, values=app_config.supported_compression_formats)
compression_combobox.set(app_config.compression_type)
compression_combobox.bind("<<ComboboxSelected>>", lambda event: IA.on_compression_selected(event, compression_combobox,format_frame4))
compression_combobox.pack(side=tk.RIGHT, padx=5)
# ------------------------------------------------------- 质量滑块 ------------------------------------------------
format_frame4 = ttk.Frame(frame2)
format_frame4.pack_forget()
quality_label = ttk.Label(format_frame4, text=f"有损压缩质量 (1-100):{str(app_config.quality)}")
quality_scale = ttk.Scale(format_frame4, from_=1, to=100, orient=tk.HORIZONTAL, command=lambda value: IA.on_quality_changed(value, quality_label))
quality_scale.set(app_config.quality)
quality_label.pack(pady=3)
quality_scale.pack(pady=3)
if app_config.compression_type == "有损":
    format_frame4.pack(pady=3)
    IA.change_window_height("add",app_config.scale_height) 
# ------------------------------------------------------- 重命名 ------------------------------------------------
# 添加是否文件的勾选框
rename_var = tk.IntVar()
rename_var.set(app_config.rename)
rename_checkbox = ttk.Checkbutton(root, text="重命名输出文件", variable=rename_var,command=lambda:IA.on_rename_checkbox_changed(rename_var.get()))
rename_checkbox.pack(pady=5)
# -------------------------------------------------------支持格式 与 开始------------------------------------------------
format_frame3 = ttk.Frame(root)
format_frame3.pack(pady=5)
# 创建显示支持格式的按钮
show_formats_button = ttk.Button(format_frame3, text="支持格式", command=lambda: IA.show_supported_formats())
show_formats_button.pack(side=tk.LEFT, padx=5)

# 创建处理图片的按钮
# 修改：将 quality_scale 替换为 progress_bar
process_button = ttk.Button(format_frame3, text="开始处理图片", command=lambda: start_processing())

app_config.input_button_item = input_button
app_config.output_button_item = output_button
app_config.failed_output_button_item = failed_output_button
app_config.format_combobox_item = format_combobox
app_config.encoder_combobox_item = encoder_combobox
app_config.compression_combobox_item = compression_combobox
app_config.quality_scale_item = quality_scale
app_config.rename_checkbox_item = rename_checkbox
app_config.process_button_item = process_button
def start_processing():
    # 调用 IC.process_images 方法
    IC.process_images(frame3, progress_bar, IA)
    # 禁用输入文件夹选择按钮
    input_button.config(state=tk.DISABLED)
    # 禁用输出文件夹选择按钮
    output_button.config(state=tk.DISABLED)
    # 禁用转换失败图片保存路径选择按钮
    failed_output_button.config(state=tk.DISABLED)
    # 禁用输出格式下拉框
    format_combobox.config(state=tk.DISABLED)
    # 禁用编码器选择下拉框
    encoder_combobox.config(state=tk.DISABLED)
    # 禁用压缩方式下拉框
    compression_combobox.config(state=tk.DISABLED)
    # 禁用质量滑块
    quality_scale.config(state=tk.DISABLED)
    # 禁用重命名勾选框
    rename_checkbox.config(state=tk.DISABLED)
    # 禁用开始处理图片按钮
    process_button.config(state=tk.DISABLED)
    
process_button.pack(side=tk.RIGHT, padx=5)
# ------------------------------------------------------- 进度条 ------------------------------------------------
frame3 = ttk.Frame(root)
frame3.pack_forget()
# 创建进度条
progress_bar = ttk.Progressbar(frame3, orient=tk.HORIZONTAL, length=300, mode='determinate')

progress_bar.pack(pady=3)
# ------------------------------------------------------- 中止按钮 ------------------------------------------------
# 创建中止按钮，初始状态为隐藏
abort_button = ttk.Button(frame3, text="中止处理", command=lambda: abort_processing())
abort_button.pack(pady=3)
def abort_processing():
    IC.abort_processing()
    # 禁用输入文件夹选择按钮
    input_button.config(state=tk.NORMAL)
    # 禁用输出文件夹选择按钮
    output_button.config(state=tk.NORMAL)
    # 禁用转换失败图片保存路径选择按钮
    failed_output_button.config(state=tk.NORMAL)
    # 禁用输出格式下拉框
    format_combobox.config(state=tk.NORMAL)
    # 禁用编码器选择下拉框
    encoder_combobox.config(state=tk.NORMAL)
    # 禁用压缩方式下拉框
    compression_combobox.config(state=tk.NORMAL)
    # 禁用质量滑块
    quality_scale.config(state=tk.NORMAL)
    # 禁用重命名勾选框
    rename_checkbox.config(state=tk.NORMAL)
    # 禁用开始处理图片按钮
    process_button.config(state=tk.NORMAL)

# ------------------------------------------------------- 作者 ------------------------------------------------
# 添加作者、邮箱和打包日期信息
author_info = f"{app_config.author_info}"
author_label = ttk.Label(root, text=author_info)
author_label.pack(side=tk.BOTTOM, pady=3)
# ------------------------------------------------------- 窗口居中 ------------------------------------------------
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - app_config.window_width) // 2
y = (screen_height - app_config.window_height) // 2
root.geometry(f"{app_config.window_width}x{app_config.window_height}+{x}+{y}")
# ------------------------------------------------------- 运行 ------------------------------------------------
# 运行主循环
root.mainloop()

# 在程序结束时保存配置文件
IA.save_config(app_config)
