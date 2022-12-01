# sample code
from socket import *
import pickle
import time
import threading
import random
from os import listdir
from tkinter import *
from tkinter import messagebox
from GUI import GUI

from GUI import *


if __name__ == '__main__':
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(0.1)
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()