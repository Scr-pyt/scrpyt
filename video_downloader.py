import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import yt_dlp
import os

def download_video():
    url = entry_url.get().strip()
    if not url:
        messagebox.showwarning("提示", "请先粘贴视频链接")
        return
    save_path = filedialog.askdirectory(title="选择保存位置")
    if not save_path:
        return

    # 禁用按钮，防止重复点击
    btn_download.config(state=tk.DISABLED)
    status_var.set("正在获取视频信息...")
    progress_bar['value'] = 0

    def download_thread():
        try:
            # 根据勾选选择格式
            if var_audio.get() == 1:
                format_code = 'bestaudio/best'
                ext = 'mp3'
            else:
                format_code = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                ext = 'mp4'
            
            ydl_opts = {
                'format': format_code,
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            root.after(0, lambda: status_var.set("✅ 下载完成！"))
            root.after(0, lambda: messagebox.showinfo("成功", "视频已下载到所选文件夹"))
            root.after(0, lambda: os.startfile(save_path))  # 打开文件夹
        except Exception as e:
            root.after(0, lambda: status_var.set(f"❌ 错误: {str(e)[:50]}"))
            root.after(0, lambda: messagebox.showerror("下载失败", str(e)))
        finally:
            root.after(0, lambda: btn_download.config(state=tk.NORMAL))
            root.after(0, lambda: progress_bar['value'](0))

    def progress_hook(d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                root.after(0, lambda p=percent: progress_bar.config(value=p))
                root.after(0, lambda p=percent: status_var.set(f"下载中... {p:.1f}%"))
        elif d['status'] == 'finished':
            root.after(0, lambda: status_var.set("正在处理/合并文件..."))

    threading.Thread(target=download_thread, daemon=True).start()

# UI 界面
root = tk.Tk()
root.title("大众视频下载器 v1.0")
root.geometry("500x220")
root.resizable(False, False)

tk.Label(root, text="📎 粘贴视频链接（B站/抖音/YouTube等）", font=("微软雅黑", 10)).pack(pady=10)
entry_url = tk.Entry(root, width=60, font=("微软雅黑", 10))
entry_url.pack(pady=5)
entry_url.insert(0, "https://www.bilibili.com/video/BV1xx...")

# 选项框
frame_opts = tk.Frame(root)
frame_opts.pack(pady=8)
var_audio = tk.IntVar()
tk.Checkbutton(frame_opts, text="仅下载音频 (MP3)", variable=var_audio).pack(side=tk.LEFT, padx=10)

# 进度条
progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.pack(pady=5)

# 状态与按钮
status_var = tk.StringVar()
status_var.set("就绪，粘贴链接即可")
tk.Label(root, textvariable=status_var, fg="gray", font=("微软雅黑", 9)).pack()

btn_download = tk.Button(root, text="⬇️ 下载到本地", command=download_video, bg="#4CAF50", fg="white", font=("微软雅黑", 10), width=20)
btn_download.pack(pady=10)

root.mainloop()
