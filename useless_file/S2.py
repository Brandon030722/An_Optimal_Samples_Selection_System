import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
import subprocess
import sys, os
# from S3 import Third


class Second(tk.Toplevel):
    def __init__(self, master, directory):
        super().__init__(master)
        self.directory = directory  # 特定的文件夹路径
        self.title("Document Preview System")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # 文件列表标签
        label = ttk.Label(self, text="List of Text Files")
        label.pack(pady=10)

        # 文件下拉列表
        self.file_list = ttk.Combobox(self, state="readonly")
        self.file_list.pack(pady=5)

        # 显示文件内容的文本框
        self.content_text = scrolledtext.ScrolledText(self, height=15, width=80)
        self.content_text.pack(pady=10)

        # 文件操作按钮
        ttk.Button(self, text="Show File", command=self.show_selected_file).pack(pady=5)
        ttk.Button(self, text="Delete Selected File", command=self.confirm_delete).pack(pady=5)
        ttk.Button(self, text="Print File", command=self.print_file).pack(pady=5)

        # 底部按钮
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # ttk.Button(bottom_frame, text="Access to filtering operations", command=self.open_Third_page).pack(side=tk.RIGHT, padx=10)
        ttk.Button(bottom_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text="Exit", command=self.close_window).pack(side=tk.LEFT, padx=10)

        self.read_files()

    def read_files(self):
        files = [f for f in os.listdir(self.directory) if f.endswith('.db')]
        self.file_list['values'] = files
        if files:
            self.file_list.current(0)

    def show_selected_file(self):
        filepath = os.path.join(self.directory, self.file_list.get())
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, content)

    def confirm_delete(self):
        filepath = os.path.join(self.directory, self.file_list.get())
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {self.file_list.get()}?"):
            os.remove(filepath)
            messagebox.showinfo("Deletion Successful", "The file has been deleted.")
            self.read_files()

    def print_file(self):
        filepath = os.path.join(self.directory, self.file_list.get())
        try:
            # /p 参数 = 打印；/pt 更通用，可指定打印机
            subprocess.run(['notepad.exe', '/p', filepath], check=True)
        except Exception as e:
            messagebox.showerror("Print Error",
                                 f"Unable to print file.\n{e}")

    # def open_Third_page(self):
    #     self.withdraw()
    #     # Create and show the third window as a modal dialog
    #     selected_filename = os.path.join(self.directory, self.file_list.get())
    #     # 创建并显示第三个窗口，将选中的文件名作为参数传递
    #     third_window = Third(self, selected_filename)
    #     third_window.mainloop()  # Makes the window modal for the application


    def go_back(self):
        self.destroy()
        self.master.deiconify()

    def close_window(self):
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    print(os.path.join("./data", "1.txt"))
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    app = Second(root, directory="./data")  # 修改为你的文件夹路径
    app.mainloop()