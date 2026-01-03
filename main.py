# main.py
import tkinter as tk
from gui.main_window import SupermercadoApp

def main():
    root = tk.Tk()
    app = SupermercadoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()