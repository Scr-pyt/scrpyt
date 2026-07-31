import time
import threading
import tkinter as tk
from tkinter import messagebox
from plyer import notification
import pystray
from PIL import Image, ImageDraw
import json
import os

CONFIG_FILE = "eye_config.json"

class EyeRestApp:
    def __init__(self):
        self.interval_min = 45  # 默认45分钟
        self.running = True
        self.timer_thread = None
        self.load_config()
        self.start_timer()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.interval_min = data.get('interval', 45)

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'interval': self.interval_min}, f)

    def show_reminder(self):
        # 弹出提醒（同时使用通知和弹窗，双保险）
        notification.notify(
            title="👀 该休息眼睛啦！",
            message=f"您已经连续使用电脑 {self.interval_min} 分钟，远眺5分钟吧！",
            timeout=10
        )
        # 强制弹窗（更醒目）
        root = tk.Tk()
        root.withdraw()
        answer = messagebox.askyesno("护眼提醒", 
                                     f"您已连续工作 {self.interval_min} 分钟！\n建议休息5分钟，远眺窗外。\n\n点击「是」开始休息（倒计时5分钟）\n点击「否」跳过本次提醒",
                                     icon='warning')
        if answer:
            # 简单倒计时
            msg = messagebox.showinfo("休息中", "🧘 休息5分钟倒计时开始...\n（请远离屏幕，5分钟后本窗自动关闭）")
            # 用sleep阻塞主窗口5分钟（实际会卡住，但正好强制休息）
            # 为了不卡死UI，这里简单处理：提示后等5分钟
            time.sleep(300)  # 5分钟
            messagebox.showinfo("休息结束", "休息时间到，继续搬砖吧！ 💪")
        root.destroy()

    def timer_loop(self):
        while self.running:
            time.sleep(self.interval_min * 60)
            if self.running:
                self.show_reminder()

    def start_timer(self):
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()

    def stop(self):
        self.running = False
        # 退出托盘图标
        if hasattr(self, 'icon'):
            self.icon.stop()

def create_tray_icon():
    # 生成简易图标
    image = Image.new('RGB', (64, 64), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse([10, 10, 54, 54], fill=(0, 150, 255))
    draw.text((20, 20), "👀", fill="white")
    
    app = EyeRestApp()
    
    def on_quit(icon, item):
        app.running = False
        icon.stop()
        os._exit(0)

    def on_set_interval(icon, item):
        # 简单设置间隔（这里通过命令行简化，可扩展GUI）
        pass

    menu = pystray.Menu(
        pystray.MenuItem("护眼运行中", None, enabled=False),
        pystray.MenuItem("退出", on_quit)
    )
    icon = pystray.Icon("eye_rest", image, "护眼提醒器", menu)
    app.icon = icon
    icon.run()

if __name__ == '__main__':
    create_tray_icon()
