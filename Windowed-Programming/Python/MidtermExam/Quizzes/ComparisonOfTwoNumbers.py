import tkinter as tk

root = tk.Tk()
root.title("兩整數最大值")
root.geometry("300x200")

tk.Label(root, text="整數 A:").pack()
a_entry = tk.Entry(root)
a_entry.pack()

tk.Label(root, text="整數 B:").pack()
b_entry = tk.Entry(root)
b_entry.pack()

result_label = tk.Label(root, text="")
result_label.pack()

def compare():
    try:
        a = int(a_entry.get())
        b = int(b_entry.get())
        result_label.config(text=f"最大值：{max(a, b)}")
    except:
        tk.showerror("錯誤", "請輸入正確的整數")

tk.Button(root, text="比較", command=compare).pack()

root.mainloop()