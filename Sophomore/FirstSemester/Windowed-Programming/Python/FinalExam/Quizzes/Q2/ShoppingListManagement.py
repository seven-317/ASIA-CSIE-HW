import tkinter as tk
from tkinter import messagebox

def update_stats():
    count = listbox.size()
    stats_var.set(f"總項目數：{count}")

def add_item():
    item = entry_var.get().strip()
    if not item:
        messagebox.showwarning("錯誤", "商品名稱不可空白")
        return
    listbox.insert(tk.END, item)
    entry_var.set("")
    update_stats()

def delete_selected():
    sel = listbox.curselection()  # tuple of indices
    if not sel:
        messagebox.showwarning("錯誤", "請先選取要刪除的項目（可多選）")
        return
    # 反向刪除避免 index 位移
    for idx in reversed(sel):
        listbox.delete(idx)
    update_stats()

def sort_items():
    items = list(listbox.get(0, tk.END))
    items_sorted = sorted(items)  # Python 預設排序（Unicode 順序）
    listbox.delete(0, tk.END)
    for it in items_sorted:
        listbox.insert(tk.END, it)
    update_stats()

root = tk.Tk()
root.title("期末Q2 購物清單管理")
root.geometry("520x360")
root.resizable(False, False)

entry_var = tk.StringVar()
stats_var = tk.StringVar(value="總項目數：0")

tk.Label(root, text="商品名稱：").place(x=25, y=20)
tk.Entry(root, textvariable=entry_var, width=28).place(x=95, y=20)

tk.Button(root, text="新增", width=12, command=add_item).place(x=360, y=16)
tk.Button(root, text="刪除選取", width=12, command=delete_selected).place(x=360, y=56)
tk.Button(root, text="排序", width=12, command=sort_items).place(x=360, y=96)

tk.Label(root, text="清單（可多選）：").place(x=25, y=60)

listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=40, height=14)
listbox.place(x=25, y=85)

tk.Label(root, textvariable=stats_var).place(x=25, y=320)

update_stats()
root.mainloop()
