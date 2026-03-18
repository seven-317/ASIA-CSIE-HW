import tkinter as tk
from tkinter import messagebox

def get_text() -> str:
    return text.get("1.0", "end-1c")

def keyword_count():
    article = get_text()
    kw = kw_var.get().strip()
    if not kw:
        messagebox.showwarning("錯誤", "請輸入關鍵字")
        return
    cnt = article.count(kw)
    messagebox.showinfo("統計結果", f"關鍵字「{kw}」出現次數：{cnt}")

def replace_keyword():
    article = get_text()
    src = src_var.get().strip()
    dst = dst_var.get().strip()

    if not src:
        messagebox.showwarning("錯誤", "請輸入要被取代的文字")
        return

    new_article = article.replace(src, dst)
    text.delete("1.0", "end")
    text.insert("1.0", new_article)

    messagebox.showinfo("完成", f"已將「{src}」取代為「{dst}」")

def clear_text():
    text.delete("1.0", "end")
    messagebox.showinfo("完成", "已清空內容")

root = tk.Tk()
root.title("期末Q4 文章關鍵字工具")
root.geometry("900x560")

top = tk.Frame(root)
top.pack(fill="x", padx=10, pady=10)

kw_var = tk.StringVar()
src_var = tk.StringVar()
dst_var = tk.StringVar()

tk.Label(top, text="關鍵字：").grid(row=0, column=0, sticky="e")
tk.Entry(top, textvariable=kw_var, width=20).grid(row=0, column=1, padx=6)
tk.Button(top, text="統計", width=10, command=keyword_count).grid(row=0, column=2, padx=6)

tk.Label(top, text="取代：").grid(row=0, column=3, sticky="e")
tk.Entry(top, textvariable=src_var, width=18).grid(row=0, column=4, padx=6)

tk.Label(top, text="成：").grid(row=0, column=5, sticky="e")
tk.Entry(top, textvariable=dst_var, width=18).grid(row=0, column=6, padx=6)

tk.Button(top, text="執行取代", width=12, command=replace_keyword).grid(row=0, column=7, padx=6)
tk.Button(top, text="清空", width=10, command=clear_text).grid(row=0, column=8, padx=6)

text = tk.Text(root, wrap="word")
text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# 預填示意
text.insert("1.0", "請在這裡貼上文章內容。\n你可以輸入關鍵字統計、或做文字取代。")

root.mainloop()
