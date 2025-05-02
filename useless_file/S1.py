import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import os
from algorithm_ import generate_SA    # ← 新行
from S2 import Second
import sys
import time
import multiprocessing


class S1(tk.Tk):  
    def __init__(self):
        super().__init__()
        self.title("An Optimal Samples Selection System")
        self.geometry("1000x400")
        self.save_count = 0  # Initialize the save counter
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(sticky=(tk.E + tk.W + tk.N + tk.S))

        params_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
        params_frame.grid(row=0, column=0, sticky=(tk.E + tk.W + tk.N + tk.S), padx=5, pady=5)

        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=0, column=1, sticky=(tk.E + tk.W + tk.N + tk.S), padx=5, pady=5)

        save_history_frame = ttk.LabelFrame(main_frame, text="Save History", padding="10")
        save_history_frame.grid(row=0, column=2, sticky=(tk.E + tk.W + tk.N + tk.S), padx=5, pady=5)

        self.var_method = tk.StringVar(value="manual")
        ttk.Radiobutton(params_frame, text="Input n", variable=self.var_method, value="manual").grid(row=2, column=0)
        ttk.Radiobutton(params_frame, text="Random n", variable=self.var_method, value="random").grid(row=2, column=1)

        ttk.Label(params_frame, text="m (45≤m≤54):").grid(row=0, column=0)
        self.entry_m = ttk.Entry(params_frame)
        self.entry_m.grid(row=0, column=1)

        ttk.Label(params_frame, text="n count (if random):").grid(row=1, column=0)
        self.entry_nIN = ttk.Entry(params_frame)
        self.entry_nIN.grid(row=1, column=1)

        self.entry_n = ttk.Entry(params_frame)
        self.entry_n.grid(row=3, column=0, columnspan=2, sticky=(tk.E + tk.W))
##########
        ttk.Label(params_frame, text="The number of S at least").grid(row=4, column=0)
        self.entry_least_s = ttk.Entry(params_frame)
        self.entry_least_s.grid(row=4, column=1)
###########
        ttk.Label(params_frame, text="k (4≤k≤7):").grid(row=5, column=0)
        self.entry_k = ttk.Entry(params_frame)
        self.entry_k.grid(row=5, column=1)

        ttk.Label(params_frame, text="j (5≤j≤6):").grid(row=6, column=0)
        self.entry_j = ttk.Entry(params_frame)
        self.entry_j.grid(row=6, column=1)

        ttk.Label(params_frame, text="s (3≤s≤7):").grid(row=7, column=0)
        self.entry_s = ttk.Entry(params_frame)
        self.entry_s.grid(row=7, column=1)

        s1_label = ttk.Label(results_frame, text="Value input")
        s1_label.grid(row=0, column=0, pady=(0, 5))
        self.text_n = scrolledtext.ScrolledText(results_frame, width=30, height=10)
        self.text_n.grid(row=1, column=0)

        s2_label = ttk.Label(results_frame, text="Results")
        s2_label.grid(row=2, column=0, pady=(10, 5))
        self.text_output = scrolledtext.ScrolledText(results_frame, width=30, height=10)
        self.text_output.grid(row=3, column=0)

        self.execution_time_label = ttk.Label(results_frame, text="Execution Time: ")
        self.execution_time_label.grid(row=4, column=0, pady=(10, 5))

        ttk.Button(params_frame, text="Save Results", command=self.save_results).grid(row=9, column=0, columnspan=2)
        ttk.Button(params_frame, text="Execute", command=self.generate_SA_application).grid(row=10, column=0,
                                                                                            columnspan=2)
        ttk.Button(params_frame, text="Delete All", command=self.delete_all).grid(row=11, column=0, columnspan=2)
        ttk.Button(params_frame, text="Next", command=self.open_next_window).grid(row=12, column=0, columnspan=2)
        ttk.Button(params_frame, text="Exit", command=self.close_window).grid(row=13, column=2, columnspan=2)

        self.text_save_history = scrolledtext.ScrolledText(save_history_frame, width=40, height=20)
        self.text_save_history.grid(row=0, column=0)

    def generate_n(self):
        global n_length
        if self.var_method.get() == 'manual':
            n = [int(x) for x in self.entry_n.get().split(',')]
            n_length = len(n)
        elif self.var_method.get() == 'random':
            m = int(self.entry_m.get())
            nIN = int(self.entry_nIN.get())
            n = random.sample(range(1, m + 1), nIN)
            n_length = nIN
        self.text_n.delete(1.0, tk.END)
        for item in n:
            self.text_n.insert(tk.END, f"{item}\n")
        return n

    def save_results(self):
        output_text = self.text_output.get("1.0", tk.END).strip()
        if output_text:
            m = self.entry_m.get()
            k = self.entry_k.get()
            j = self.entry_j.get()
            s = self.entry_s.get()
            self.save_count += 1  # Increment save count
            data_rows = len(resultSA)

            data_folder = os.path.join(os.getcwd(), "data")
            os.makedirs(data_folder, exist_ok=True)

            filename = f"{m}-{n_length}-{k}-{j}-{s}-{self.save_count}-{data_rows}.db"
            filepath = os.path.join(data_folder, filename)
            with open(filepath, 'w') as file:
                file.write(output_text)
            self.text_save_history.insert(tk.END, f"Saved: {filename}\n")
            messagebox.showinfo("Save Successful", f"Results saved in {filename}")
        else:
            messagebox.showwarning("Save Failed", "There is no output to save.")

    def generate_SA_application(self):
        self.text_output.delete(1.0, tk.END)
        n = self.generate_n()
        k = int(self.entry_k.get())
        j = int(self.entry_j.get())
        s = int(self.entry_s.get())
        s_least = int(self.entry_least_s.get())
        start_time = time.time()  # 记录开始时间
        global resultSA
        resultSA = generate_SA(n, k, j, s, s_least)  # Assuming generate_SA is defined and works correctly
        end_time = time.time()  # 记录结束时间
        print(f"Total solutions: {len(resultSA)}")
        execution_time = end_time - start_time  # 计算执行时间
        for result in resultSA:
            self.text_output.insert(tk.END, f"{result}\n")
        self.execution_time_label.config(text=f"Execution Time: {execution_time} seconds")  # 更新执行时间标签文本
        print(f"Execution time: {execution_time} seconds")  # 打印执行时间到终端

    def delete_all(self):
        self.text_save_history.delete(1.0, tk.END)
        # 清除所有输入框中的内容
        self.entry_m.delete(0, tk.END)
        self.entry_nIN.delete(0, tk.END)
        self.entry_n.delete(0, tk.END)
        self.entry_k.delete(0, tk.END)
        self.entry_j.delete(0, tk.END)
        self.entry_s.delete(0, tk.END)
        # 清除结果文本框中的内容
        self.text_output.delete(1.0, tk.END)
        self.text_n.delete(1.0, tk.END)

    def open_next_window(self):
        self.withdraw()
        current_directory = os.path.dirname(__file__)
        data_folder_path = os.path.join(current_directory, "data")
        second_window = Second(self, directory="./data")
        second_window.mainloop()

    def close_window(self):
        self.destroy()
        sys.exit()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = S1()
    app.mainloop()