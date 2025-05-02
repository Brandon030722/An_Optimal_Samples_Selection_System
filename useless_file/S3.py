import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
from algorithm_ import generate_SA
import sys
import ast


class Third(tk.Toplevel):
    def __init__(self, master, selected_filename):
        super().__init__(master)
        self.filename = selected_filename  # 保存文件名为实例变量
        self.title("Advanced Filter Operations")
        self.geometry("800x600")
        self.selected_option = tk.StringVar(value="none")  # 默认没有选项被选中
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="An Optimal Samples Selection System").pack(pady=20)
        ttk.Label(self, text="Please select the filter methods").pack()

        # 单选按钮设置
        ttk.Radiobutton(self, text="Define positions and numbers",
                        value="S4", variable=self.selected_option).pack()
        ttk.Radiobutton(self, text="Define positions and range of numbers",
                        value="S5", variable=self.selected_option).pack()
        ttk.Radiobutton(self, text="Select positions to fixed numbers",
                        value="S6", variable=self.selected_option).pack()

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # 下一页按钮
        ttk.Button(self, text="Next", command=self.open_next_window).pack(pady=10)
        ttk.Button(bottom_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text="Exit", command=self.close_window).pack(side=tk.LEFT, padx=10)

    def open_next_window(self):
        if self.selected_option.get() in ["S4", "S5", "S6"]:
            window_class = globals().get(self.selected_option.get())
            if window_class:
                new_window = window_class(self, self.filename)  # 使用self.filename传递
                new_window.grab_set()  # Makes the new window modal
            else:
                messagebox.showerror("Error", "The selected operation is not implemented yet.")
        else:
            messagebox.showerror("Error", "Please select an option before proceeding.")

    def go_back(self):
        self.destroy()
        self.master.deiconify()

    def close_window(self):
        self.destroy()
        sys.exit()

# Stub classes for S4, S5, S6 to demonstrate switching
class S4(tk.Toplevel):
    def __init__(self, master, filename):
        super().__init__(master)
        self.filename = filename
        self.title("Define positions and numbers")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Define positions and numbers, please input 3 positions").pack(pady=10)

        position_frame = ttk.Frame(self)
        position_frame.pack(pady=5)
        self.position_entries = []
        for i in range(3):
            entry = ttk.Entry(position_frame, width=10)
            entry.pack(side=tk.LEFT, padx=5, pady=5)
            self.position_entries.append(entry)

        ttk.Label(self, text="Input numbers for the positions").pack(pady=10)
        number_frame = ttk.Frame(self)
        number_frame.pack(pady=5)
        self.number_entries = []
        for i in range(3):
            entry = ttk.Entry(number_frame, width=10)
            entry.pack(side=tk.LEFT, padx=5, pady=5)
            self.number_entries.append(entry)

        self.reverse_filter = tk.BooleanVar()
        ttk.Checkbutton(self, text="Enable reverse filtering", variable=self.reverse_filter).pack(pady=10)

        ttk.Button(self, text="Filter", command=self.filter_data).pack(pady=5)

        ttk.Label(self, text="Enter filename to save as:").pack()
        self.filename_entry = ttk.Entry(self)
        self.filename_entry.pack(pady=5)

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        ttk.Button(self, text="Save Filtered Data", command=self.save_data).pack(pady=5)
        ttk.Button(bottom_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text="Exit", command=self.close_window).pack(side=tk.LEFT, padx=10)
        

        self.result_text = scrolledtext.ScrolledText(self, height=10, width=50)
        self.result_text.pack(pady=10)

    def filter_data(self):
        try:
            positions = [int(entry.get()) - 1 for entry in self.position_entries]
            numbers = [int(entry.get()) for entry in self.number_entries]
            filtered_data = []

            with open(self.filename, 'r', encoding='utf-8') as file:
                for line in file:
                    data = ast.literal_eval(line.strip())
                    if self.reverse_filter.get():
                        if all(data[pos] != num for pos, num in zip(positions, numbers)):
                            filtered_data.append(data)
                    else:
                        if all(data[pos] == num for pos, num in zip(positions, numbers)):
                            filtered_data.append(data)

            self.result_text.delete('1.0', tk.END)
            result = "\n".join(map(str, filtered_data))
            self.result_text.insert(tk.END, result)
            self.filtered_data = filtered_data
        except Exception as e:
            print("Error:", e)


    def save_data(self):
        file_name = self.filename_entry.get().strip()
        if file_name:
            if hasattr(self, 'filtered_data'):
                complete_path = os.path.join("./", file_name + ".txt")
                with open(complete_path, 'w') as file:
                    for data in self.filtered_data:
                        file.write(f"{data}\n")
                messagebox.showinfo("Success", "Data saved successfully.")
            else:
                messagebox.showwarning("Warning", "No data to save. Please filter first.")
        else:
            messagebox.showwarning("Warning", "Please enter a valid filename.")

    def close_window(self):
        self.destroy()
        sys.exit()

    def go_back(self):
        self.destroy()
        self.master.deiconify()

class S5(tk.Toplevel):
    def __init__(self, master, filename):
        super().__init__(master)
        self.filename = filename
        self.title("Define positions and range of numbers")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Define positions and range of numbers, please input 3 ranges").pack(pady=10)

        position_frame = ttk.Frame(self)
        position_frame.pack(pady=5)
        self.position_entries = []
        for i in range(3):
            entry = ttk.Entry(position_frame, width=10)
            entry.pack(side=tk.LEFT, padx=5, pady=5)
            self.position_entries.append(entry)

        ttk.Label(self, text="Input ranges for the positions").pack(pady=10)
        range_frame = ttk.Frame(self)
        range_frame.pack(pady=5)
        self.range_entries = []
        for i in range(3):
            range_entry_frame = ttk.Frame(range_frame)
            range_entry_frame.pack(pady=2)
            lower_entry = ttk.Entry(range_entry_frame, width=5)
            lower_entry.pack(side=tk.LEFT, padx=2)
            ttk.Label(range_entry_frame, text="to").pack(side=tk.LEFT, padx=2)
            upper_entry = ttk.Entry(range_entry_frame, width=5)
            upper_entry.pack(side=tk.LEFT, padx=2)
            self.range_entries.append((lower_entry, upper_entry))

        self.reverse_filter = tk.BooleanVar()
        ttk.Checkbutton(self, text="Enable reverse filtering", variable=self.reverse_filter).pack(pady=10)

        ttk.Button(self, text="Filter", command=self.filter_data).pack(pady=5)

        ttk.Label(self, text="Enter filename to save as:").pack()
        self.filename_entry = ttk.Entry(self)
        self.filename_entry.pack(pady=5)

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        ttk.Button(self, text="Save Filtered Data", command=self.save_data).pack(pady=5)
        ttk.Button(bottom_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text="Exit", command=self.close_window).pack(side=tk.LEFT, padx=10)
        

        self.result_text = scrolledtext.ScrolledText(self, height=10, width=50)
        self.result_text.pack(pady=10)

    def filter_data(self):
        try:
            positions = [int(entry.get()) - 1 for entry in self.position_entries]
            ranges = [(int(entry[0].get()), int(entry[1].get())) for entry in self.range_entries]
            filtered_data = []

            with open(self.filename, 'r', encoding='utf-8') as file:
                for line in file:
                    data = ast.literal_eval(line.strip())
                    if self.reverse_filter.get():
                        if all(not (ranges[i][0] <= data[pos] <= ranges[i][1]) for i, pos in enumerate(positions)):
                            filtered_data.append(data)
                    else:
                        if all(ranges[i][0] <= data[pos] <= ranges[i][1] for i, pos in enumerate(positions)):
                            filtered_data.append(data)

            self.result_text.delete('1.0', tk.END)
            result = "\n".join(map(str, filtered_data))
            self.result_text.insert(tk.END, result)
            self.filtered_data = filtered_data

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def save_data(self):
        file_name = self.filename_entry.get().strip()
        if file_name:
            if hasattr(self, 'filtered_data'):
                complete_path = os.path.join("./", file_name + ".txt")
                with open(complete_path, 'w') as file:
                    for data in self.filtered_data:
                        file.write(f"{data}\n")
                messagebox.showinfo("Success", "Data saved successfully.")
            else:
                messagebox.showwarning("Warning", "No data to save. Please filter first.")
        else:
            messagebox.showwarning("Warning", "Please enter a valid filename.")

    def close_window(self):
        self.destroy()
        sys.exit()

    def go_back(self):
        self.destroy()
        self.master.deiconify()

class S6(tk.Toplevel):
    def __init__(self, master, filename):
        super().__init__(master)
        self.filename = filename
        self.title("Select positions to fixed numbers")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Define positions, please input 3 positions and enter their sum").pack(pady=10)

        # 设置位置输入框
        position_frame = ttk.Frame(self)
        position_frame.pack(pady=5)
        self.position_entries = []
        for i in range(3):
            entry = ttk.Entry(position_frame, width=10)
            entry.pack(side=tk.LEFT, padx=5, pady=5)
            self.position_entries.append(entry)

        # 设置和数输入框
        ttk.Label(self, text="Input the sum for the positions").pack(pady=10)
        self.sum_entry = ttk.Entry(self, width=15)
        self.sum_entry.pack(pady=5)

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # 设置反筛选复选框
        self.reverse_filter = tk.BooleanVar()
        ttk.Checkbutton(self, text="Enable reverse filtering", variable=self.reverse_filter).pack(pady=10)

        ttk.Button(self, text="Filter", command=self.filter_data).pack(pady=5)
        ttk.Button(self, text="Save Filtered Data", command=self.save_data).pack(pady=5)
        ttk.Button(bottom_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=10)
        ttk.Button(bottom_frame, text="Exit", command=self.close_window).pack(side=tk.LEFT, padx=10)
        
        

        # 结果显示文本框
        self.result_text = scrolledtext.ScrolledText(self, height=10, width=50)
        self.result_text.pack(pady=10)

    def filter_data(self):
        try:
            positions = [int(entry.get()) - 1 for entry in self.position_entries]
            target_sum = int(self.sum_entry.get())
            filtered_data = []

            with open(self.filename, 'r', encoding='utf-8') as file:
                for line in file:
                    data = ast.literal_eval(line.strip())
                    actual_sum = sum(data[pos] for pos in positions)
                    if self.reverse_filter.get():
                        if actual_sum != target_sum:
                            filtered_data.append(data)
                    else:
                        if actual_sum == target_sum:
                            filtered_data.append(data)

            self.result_text.delete('1.0', tk.END)
            result = "\n".join(map(str, filtered_data))
            self.result_text.insert(tk.END, result)
            self.filtered_data = filtered_data

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def save_data(self):
        file_name = self.filename_entry.get().strip()
        if file_name:
            if hasattr(self, 'filtered_data'):
                complete_path = os.path.join("./", file_name + ".txt")
                with open(complete_path, 'w') as file:
                    for data in self.filtered_data:
                        file.write(f"{data}\n")
                messagebox.showinfo("Success", "Data saved successfully.")
            else:
                messagebox.showwarning("Warning", "No data to save. Please filter first.")
        else:
            messagebox.showwarning("Warning", "Please enter a valid filename.")

    def close_window(self):
        self.destroy()
        sys.exit()

    def go_back(self):
        self.destroy()
        self.master.deiconify()
