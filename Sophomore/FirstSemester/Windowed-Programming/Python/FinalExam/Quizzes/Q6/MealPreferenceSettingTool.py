import tkinter as tk

def set_all():
    val = all_var.get()
    for v in item_vars.values():
        v.set(val)
    update_result()

def update_all_checkbox():
    # 如果全部勾選 -> 全選勾；否則全選不勾
    all_checked = all(v.get() for v in item_vars.values())
    all_var.set(all_checked)

def update_result():
    selected = [name for name, v in item_vars.items() if v.get()]
    result_var.set(f"已選 {len(selected)} 項：" + ("、".join(selected) if selected else "（無）"))

def on_item_toggle():
    update_all_checkbox()
    update_result()

root = tk.Tk()
root.title("期末Q6 餐點偏好設定")
root.geometry("420x340")
root.resizable(False, False)

all_var = tk.BooleanVar(value=False)
result_var = tk.StringVar(value="已選 0 項：（無）")

items = ["雞肉", "牛肉", "素食", "不吃牛", "不吃辣", "不吃葱"]
item_vars = {name: tk.BooleanVar(value=False) for name in items}

tk.Checkbutton(root, text="全部選擇", variable=all_var, command=set_all).pack(anchor="w", padx=20, pady=(15, 8))

for name in items:
    tk.Checkbutton(root, text=name, variable=item_vars[name], command=on_item_toggle).pack(anchor="w", padx=40)

tk.Label(root, textvariable=result_var).pack(anchor="w", padx=20, pady=18)

# 初始顯示
update_result()

root.mainloop()
