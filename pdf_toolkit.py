import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfReader, PdfWriter
import os

def merge_pdfs():
    files = filedialog.askopenfilenames(title="选择要合并的PDF文件（按顺序）", filetypes=[("PDF文件", "*.pdf")])
    if len(files) < 2:
        messagebox.showwarning("提示", "请至少选择2个PDF文件")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF文件", "*.pdf")])
    if not save_path:
        return
    
    writer = PdfWriter()
    for f in files:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)
    writer.write(save_path)
    writer.close()
    messagebox.showinfo("成功", f"合并完成！\n保存至: {save_path}")
    os.startfile(os.path.dirname(save_path))

def split_pdf():
    file = filedialog.askopenfilename(title="选择要拆分的PDF", filetypes=[("PDF文件", "*.pdf")])
    if not file:
        return
    try:
        pages_per = int(entry_pages.get())
        if pages_per <= 0:
            raise ValueError
    except:
        messagebox.showerror("错误", "请输入有效的页数（如 10）")
        return
    
    reader = PdfReader(file)
    total = len(reader.pages)
    base_name = os.path.splitext(os.path.basename(file))[0]
    save_dir = filedialog.askdirectory(title="选择拆分后保存的文件夹")
    if not save_dir:
        return

    for start in range(0, total, pages_per):
        writer = PdfWriter()
        end = min(start + pages_per, total)
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        out_file = os.path.join(save_dir, f"{base_name}_part{start//pages_per + 1}.pdf")
        writer.write(out_file)
        writer.close()
    messagebox.showinfo("完成", f"拆分完成！共生成 {(total-1)//pages_per + 1} 个文件")

# GUI 布局
root = tk.Tk()
root.title("📄 PDF万能工具箱")
root.geometry("400x250")

notebook = ttk.Notebook(root)
notebook.pack(pady=10, fill='both', expand=True)

# 合并标签
tab1 = tk.Frame(notebook)
notebook.add(tab1, text="合并PDF")
tk.Button(tab1, text="📑 选择多个PDF并合并", command=merge_pdfs, bg="#2196F3", fg="white", height=2, width=25).pack(pady=40)

# 拆分标签
tab2 = tk.Frame(notebook)
notebook.add(tab2, text="拆分PDF")
tk.Label(tab2, text="每多少页拆成一份:").pack(pady=10)
entry_pages = tk.Entry(tab2, width=10)
entry_pages.insert(0, "10")
entry_pages.pack()
tk.Button(tab2, text="✂️ 选择PDF并拆分", command=split_pdf, bg="#FF5722", fg="white", height=2, width=25).pack(pady=20)

root.mainloop()
