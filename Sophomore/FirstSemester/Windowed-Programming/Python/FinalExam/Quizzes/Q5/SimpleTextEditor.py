import tkinter as tk
from tkinter import messagebox

def calc_lines():
    # end-1c 是最後一個字元（避免 end 多一行）
    line_str = text.index("end-1c").split(".")[0]
    try:
        lines = int(line_str)
    except ValueError:
        lines = 0
    messagebox.showinfo("行數", f"目前行數：{lines}")

root = tk.Tk()
root.title("期末Q5 簡易文字編輯器")
root.geometry("760x520")

top = tk.Frame(root)
top.pack(fill="x", padx=10, pady=10)

tk.Button(top, text="重新計算行數", command=calc_lines).pack(side="left")

frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side="right", fill="y")

text = tk.Text(frame, yscrollcommand=scrollbar.set, wrap="none")
text.pack(side="left", fill="both", expand=True)

scrollbar.config(command=text.yview)

text.insert("1.0", "這是一個簡易文字編輯器。\nText 搭配 Scrollbar。\n可重新計算目前行數。")

root.mainloop()
