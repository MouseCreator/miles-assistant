
import tkinter as tk
from tkinter import ttk
from tkinter import Menu


class VisualMessage(tk.Label):
    def __init__(self, frame: tk.Frame, message, anchor, bg):
        super().__init__(frame, text=message, anchor=anchor, bg=bg, padx=5, pady=5)
        self.message = message
        self.anchor = anchor
    def m_pack(self):
        self.pack(anchor=self.anchor, pady=2, padx=5)

class TheirMessage(VisualMessage):
    def __init__(self, frame: tk.Frame, message):
        super().__init__(frame, message, "w", "lightgray")

class OurMessage(VisualMessage):
    def __init__(self, frame: tk.Frame, message):
        super().__init__(frame, message, "e", "lightblue")



class AssistantApp():
    def __init__(self):
        self.root = tk.Tk()

        self.root.title("Miles assistant")
        self.root.geometry("500x500")
        self.root.minsize(400, 400)

        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menu_bar = Menu(self.root)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Close", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        options_menu = Menu(menu_bar, tearoff=0)
        options_menu.add_command(label="General...")
        options_menu.add_command(label="Hot keys...")
        menu_bar.add_cascade(label="Options", menu=options_menu)

        self.root.config(menu=menu_bar)

    def create_widgets(self):
        self.chat_frame = tk.Frame(self.root, bg="white")
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        their_msg = TheirMessage(self.chat_frame, "Hello from them!")
        their_msg.m_pack()
        our_msg = OurMessage(self.chat_frame, "Hello from me!")
        our_msg.m_pack()

        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.option_var = tk.StringVar(value="--")
        self.dropdown = ttk.Combobox(input_frame, textvariable=self.option_var, values=["--", "1", "2"], width=5)
        self.dropdown.grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.text_field = tk.Text(input_frame, height=3, width=40)
        self.text_field.grid(row=0, column=1, padx=(0, 5), sticky="we")

        self.send_button = ttk.Button(input_frame, text="Send")
        self.send_button.grid(row=0, column=2, padx=(0, 5))

        self.mic_button = ttk.Button(input_frame, text="Record")
        self.mic_button.grid(row=0, column=3)

        input_frame.columnconfigure(1, weight=1)

if __name__ == "__main__":
    app = AssistantApp()
    app.root.mainloop()