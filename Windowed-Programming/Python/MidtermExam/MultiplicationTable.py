import tkinter as tk

root = tk.Tk()
root.title("乘法表產生器")
root.geometry("300x250")

tk.Label(root, text="輸入整數 N 生成 N 的 1~9 乘法表：").pack()
entry = tk.Entry(root)
entry.pack()

result_label = tk.Label(root, text="", justify="left")
result_label.pack()

def generate():
    try:
        n = int(entry.get())
        output = ""
        for i in range(1, 10):
            output += f"{n} x {i} = {n*i}\n"
        result_label.config(text=output)
    except:
        tk.showerror("錯誤", "請輸入正確的整數")

tk.Button(root, text="生成", command=generate).pack()

root.mainloop()