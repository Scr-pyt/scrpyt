import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

def get_photo_date(filepath):
    """尝试读取EXIF拍摄日期，失败则返回文件修改时间"""
    try:
        img = Image.open(filepath)
        exif = img._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'DateTimeOriginal':
                    # EXIF格式: "2026:08:01 14:30:00"
                    return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    # 后备方案：文件修改时间
    timestamp = os.path.getmtime(filepath)
    return datetime.fromtimestamp(timestamp)

def organize_photos():
    src_dir = filedialog.askdirectory(title="选择照片所在文件夹（相机/手机导入目录）")
    if not src_dir:
        return
    dst_base = filedialog.askdirectory(title="选择目标根目录（照片将按日期存入）")
    if not dst_base:
        return

    # 支持的图片扩展名
    exts = ('.jpg', '.jpeg', '.png', '.heic', '.bmp', '.tiff', '.raw', '.arw')
    moved_count = 0
    error_count = 0

    # 禁用按钮
    btn_go.config(state=tk.DISABLED)
    status_var.set("正在扫描照片...")
    root.update()

    for root_dir, _, files in os.walk(src_dir):
        for f in files:
            if not f.lower().endswith(exts):
                continue
            full_path = os.path.join(root_dir, f)
            try:
                date_obj = get_photo_date(full_path)
                # 目标路径: /年/月/ 例如 2026/08/
                sub_path = os.path.join(str(date_obj.year), f"{date_obj.month:02d}")
                dst_dir = os.path.join(dst_base, sub_path)
                os.makedirs(dst_dir, exist_ok=True)
                
                dst_file = os.path.join(dst_dir, f)
                # 防止重名，加个时间戳后缀
                if os.path.exists(dst_file):
                    name, ext = os.path.splitext(f)
                    dst_file = os.path.join(dst_dir, f"{name}_{date_obj.strftime('%H%M%S')}{ext}")
                
                shutil.move(full_path, dst_file)
                moved_count += 1
                status_var.set(f"已整理: {f} -> {sub_path}")
                root.update()
            except Exception as e:
                error_count += 1
                print(f"处理 {f} 出错: {e}")

    status_var.set(f"✅ 完成！移动 {moved_count} 张照片，错误 {error_count} 个")
    messagebox.showinfo("整理完成", f"成功分类 {moved_count} 张照片！")
    btn_go.config(state=tk.NORMAL)

# GUI
root = tk.Tk()
root.title("📸 智能照片管家")
root.geometry("400x150")

tk.Label(root, text="把手机/相机照片一键按日期归档", font=("微软雅黑", 11)).pack(pady=15)
status_var = tk.StringVar()
status_var.set("选择源文件夹和目标文件夹")
tk.Label(root, textvariable=status_var, fg="blue").pack()

btn_go = tk.Button(root, text="🚀 开始整理照片", command=organize_photos, bg="#FF9800", fg="white", font=("微软雅黑", 10), width=20)
btn_go.pack(pady=15)

root.mainloop()
