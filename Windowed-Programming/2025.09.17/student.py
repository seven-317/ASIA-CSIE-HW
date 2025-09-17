from tkinter import *

root = Tk()
root.title("114021177 湯和錡")
root.geometry("300x200")

lable_name = Label(root, text="姓名: 湯和錡", font=("Arial", 12, "bold"))
lable_name.pack(pady=10)

lable_id = Label(root, text="學號: 114021177", fg="blue")
lable_id.pack(pady=10)

lable_dept = Label(root, text="科系: 資工2B", anchor=CENTER)
lable_dept.pack(fill="x", pady=10)


root.mainloop()