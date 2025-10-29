import tkinter as tk

root = tk.Tk()
root.title("偶數或奇數判斷")
root.geometry("300x200")

tk.Label(root, text="請輸入整數：").pack()
entry = tk.Entry(root)
entry.pack()
result_label = tk.Label(root, text="")
result_label.pack()

def check():
    try:
        n = int(entry.get())
        if n % 2 == 0:
            result_label.config(text="偶數")
        else:
            result_label.config(text="奇數")
    except:
        tk.showerror("錯誤", "請輸入正確的整數")

tk.Button(root, text="判斷", command=check).pack()

root.mainloop()