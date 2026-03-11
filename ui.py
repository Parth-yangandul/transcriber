import tkinter as tk
from tkinter import scrolledtext
from trans import transcriber

def run_transcriber():
    output_box.delete(1.0, tk.END)
    try:
        result = transcriber()
        output_box.insert(tk.END, str(result))
    except Exception as e:
        output_box.insert(tk.END, f"Error: {str(e)}")

# Create main window
root = tk.Tk()
root.title("Transcriber UI")
root.geometry("500x400")

# Create button
run_button = tk.Button(root, text="Run Transcriber", command=run_transcriber, height=2, width=20)
run_button.pack(pady=20)

# Create output box
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15)
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()