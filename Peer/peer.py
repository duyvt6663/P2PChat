# sample code
from socket import *
import pickle
import time
from threading import Thread
import random
from tkinter import *
from os import listdir
from GUI import GUI
from server_process import ServerProcess

if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()