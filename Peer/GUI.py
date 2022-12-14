# sample code
import socket
from socket import *
import pickle
import time
from threading import Thread
import random
import os
from os import listdir
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from server_process import ServerProc
from client_process import ClientProc
from Deserializer import ReqTag, RepTag


class GUI:
    def __init__(self, master):
        self.root = master  # init GUI tree
        self.chat_transcript_area = None
        self.enter_text_widget = None
        self.friend_area = None
        self.frframe = None
        self.chatframe = None
        self.entryframe = None
        self.logout_but = None

        self.username = None
        self.password = None
        self.nickname = None
        self.currChatFriend = None

        self.init_frame()
        self.init_gui()
        # init server and client processes
        self.HOST = gethostbyname(gethostname())  # server proc host
        self.PORT = random.randint(1024, 49151)  # server proc port
        # take a client socket to connect to server proc, and recv msg + file
        self.client = ClientProc(self.HOST, self.PORT, self)
        # run server proc
        self.server = ServerProc(self.HOST, self.PORT, self.client, self)

    def init_frame(self):
        # init or reset login/signup frame
        self.userframe = Frame()
        self.passframe = Frame()
        self.nickframe = Frame()
        self.login_but = Frame()
        self.signup_but = Frame()

    def init_gui(self):  # GUI initializer
        self.root.title("Chat App")
        self.root.resizable(0, 0)
        self.login_ui()
    # def createSocket(self):
    #     try:
    #         so = socket(AF_INET, SOCK_STREAM)
    #         ip = '127.0.0.1'
    #         port = random.randint(10000, 49151)
    #         so.bind((ip,port))
    #         return so, (ip, port)
    #     except:
    #         return self.createSocket()

    # def sendMessage(self, conn, msg):
    #     conn.sendall(pickle.dumps(msg))
    def hide_frame(self):
        self.userframe.pack_forget()
        self.passframe.pack_forget()
        self.nickframe.pack_forget()
        self.login_but.pack_forget()
        self.signup_but.pack_forget()
        if self.logout_but:
            self.logout_but.pack_forget()
        if self.frframe:
            self.frframe.pack_forget()
        if self.chatframe:
            self.chatframe.pack_forget()
        if self.entryframe:
            self.entryframe.pack_forget()

    # ------------------------- LOGIN GUI -------------------------------
    #####################################################################

    def login_ui(self):
        self.hide_frame()
        self.init_frame()

        Label(self.userframe, text='Username:', font=(
            "Helvetica", 13)).pack(side='left', padx=10)
        self.username = Entry(self.userframe, width=40, borderwidth=2)
        self.username.pack(side='left', anchor='e')
        Label(self.passframe, text='Password:', font=(
            "Helvetica", 13)).pack(side='left', padx=10)
        self.password = Entry(self.passframe, show='*',
                              width=40, borderwidth=2)
        self.password.pack(side='left', anchor='e')
        Button(self.login_but, text="Log in", width=10,
               command=self.login).pack(side='bottom')
        Label(self.signup_but, text='If you don\'t have an account,',
              font=("Helvetica", 10)).pack(side='left', padx=10)
        Button(self.signup_but, text='Sign up', bd=0, fg='blue',
               command=self.signup_ui).pack(side='left')

        self.userframe.pack(anchor='nw')
        self.passframe.pack(anchor='nw')
        self.login_but.pack(anchor='center')
        self.signup_but.pack(anchor='nw')

    def login(self):
        username = self.username.get()
        password = self.password.get()
        if len(username) == 0:
            messagebox.showerror('Message', "Please enter username")
            return
        if len(password) == 0:
            messagebox.showerror('Message', "Please enter password")
            return
        # success
        self.username.config(state='disabled')
        self.password.config(state='disabled')
        # time.sleep(0.1)
        flag = []
        t = Thread(target=ClientProc.loginThread, args=(
            self.client, username, password, flag))
        t.start()
        t.join()
        if not flag:  # flag not changed -> server not responding/ error/ wrong login info
            messagebox.showinfo('Message', 'Username or password is invalid')
            self.username.config(state='normal')
            self.password.config(state='normal')
            return
        messagebox.showinfo('Message', 'Log in successfully!')
        self.hide_frame()
        self.display_logout_but()
        self.display_chat_entry_box()
        self.display_friend_box()
        self.display_chat_box()

    # ------------------------- SIGNUP GUI ------------------------------
    #####################################################################
    def signup_ui(self):
        self.hide_frame()
        self.init_frame()

        Label(self.userframe, text='Username:', font=("Helvetica", 13)).pack(side='left', padx=10)
        self.username = Entry(self.userframe, width=40, borderwidth=2)
        self.username.pack(side='left', anchor='e')
        Label(self.passframe, text='Password:', font=("Helvetica", 13)).pack(side='left', padx=10)
        self.password = Entry(self.passframe, show='*', width=40, borderwidth=2)
        self.password.pack(side='left', anchor='e')
        Label(self.nickframe, text='Nickname:', font=("Helvetica", 13)).pack(side='left', padx=10)
        self.nickname = Entry(self.nickframe, width=40, borderwidth=2)
        self.nickname.pack(side='left', anchor='e')
        Button(self.signup_but, text="Sign up", width=10, command=self.sign_up).pack(side='bottom')
        Label(self.login_but, text='If you already have an account,', font=("Helvetica", 10)).pack(side='left', padx=10)
        Button(self.login_but, text='Log in', bd=0, fg='blue', command=self.login_ui).pack(side='left')

        self.userframe.pack(anchor='nw')
        self.passframe.pack(anchor='nw')
        self.nickframe.pack(anchor='nw')
        self.signup_but.pack(anchor='center')
        self.login_but.pack(anchor='nw')

    def sign_up(self):
        username = self.username.get()
        password = self.password.get()
        nickname = self.nickname.get()
        if len(username) == 0:
            messagebox.showerror('Message', "Please enter username")
            return
        if len(password) == 0:
            messagebox.showerror('Message', "Please enter password")
            return
        if len(nickname) == 0:
            messagebox.showerror('Message', "Please enter nickname")
            return
        self.username.config(state='disabled')
        self.password.config(state='disabled')
        self.nickname.config(state='disabled')
        # time.sleep(0.1)
        flag = []
        t = Thread(target=ClientProc.signupThread, args=(
            self.client, username, password, nickname, flag))
        t.start()
        t.join()

        if not flag:  # flag not changed -> server not responding/ error/ wrong signup info
            messagebox.showinfo('Message', 'Username is currently in use')
            self.username.config(state='normal')
            self.password.config(state='normal')
            self.nickname.config(state='normal')
            return
        messagebox.showinfo('Message', 'Sign up successfully!')
        self.hide_frame()
        self.display_logout_but()
        self.display_chat_entry_box()
        self.display_friend_box()
        self.display_chat_box()

    # ------------------------- LOGOUT UI -------------------------------
    #####################################################################
    def display_logout_but(self):
        self.logout_but = Frame()
        Label(self.logout_but, text=self.client.nickname).pack(
            side='left', padx=10)
        Button(self.logout_but, text="Log out", width=10,
               command=self.log_out).pack(side='left')
        self.logout_but.pack(anchor='nw')

    def log_out(self):
        thread = Thread(target=ClientProc.logoutThread, args=(self.client,), daemon=True)
        thread.start()
        self.login_ui()

    # ------------------------- friend box UI ---------------------------
    #####################################################################
    def display_friend_box(self, peerID=-1):
        self.frframe = Frame()
        self.frframe.pack(side='left')
        # self.friendBox = Frame(self.frframe)

        Label(self.frframe, text='Friend List:', font=("Serif", 12)).pack(side='top', anchor='w')

        self.friend_area = Frame(self.frframe, width=30, height=15)
        self.friend_area.pack(side='left', padx=10)

        scrollbar = Scrollbar(self.frframe, orient=VERTICAL)
        scrollbar.pack(side='right', fill='y')

        # self.friendBox.pack(side='top', anchor='s')

        self.currChatFriend = IntVar(self.friend_area, peerID)
        for friend in self.client.friends:
            Radiobutton(self.friend_area, text=str((friend['nickname'], friend['status'])),
                        variable=self.currChatFriend, value=friend['id'], width=30,
                        state=DISABLED if friend['status'] == 'OFFLINE' else NORMAL,
                        background="light blue", command=self.request_session).pack(side='top', fill=X, ipady=5)

    def update_friend_box(self):
        self.friend_area.pack_forget()
        self.friend_area = Frame(self.frframe, width=30, height=15)
        self.friend_area.pack(side='left', padx=10)
        for friend in self.client.friends:
            Radiobutton(self.friend_area, text=str((friend['nickname'], friend['status'])),
                        variable=self.currChatFriend, value=friend['id'], width=30,
                        state=DISABLED if friend['status'] == 'OFFLINE' else NORMAL,
                        background="light blue", command=self.request_session).pack(side='top', fill=X, ipady=5)

    def request_session(self):
        peerID = self.currChatFriend.get()  # current chat friend id
        if peerID not in self.client.chatSessions:
            # request connection to peer
            thread = Thread(target=ClientProc.openSessionThread,
                            args=(self.client, peerID), daemon=True)
            thread.start()
        self.reset_chatbox(peerID)

    # ------------------------- ENTRY CHAT UI ---------------------------
    #####################################################################
    def display_chat_entry_box(self, peerID=-1):
        self.entryframe = Frame()
        self.entryframe.pack(side='bottom')
        Label(self.entryframe, text='Enter message:', font=("Serif", 12))\
            .pack(side='top', anchor='w',padx=(251,10),pady=(10,1))

        self.fileButton = Button(self.entryframe, text='Browse', width=10, background='#8d99ae',
                                 font=('Serif', 12), fg='white', cursor='hand2', state=DISABLED,
                                 command=lambda: self.send_file(peerID))
        self.fileButton.pack(side='left',anchor='e',padx=(145,10))

        self.enter_text_widget = Text(self.entryframe, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='right',anchor='e', pady=(1,15))

        if peerID != -1:
            self.enter_text_widget.bind('<Return>', lambda e, peerID=peerID: self.on_enter_key_pressed(peerID))
            self.fileButton.config(state=ACTIVE)


    def on_enter_key_pressed(self, peerID):
        self.send_chat(peerID)
        # clear text
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self, peerID):
        # add message to self chatbox
        senders_name = self.client.nickname.strip() + ":\n"
        data = self.enter_text_widget.get(1.0, 'end').strip()
        msg = (senders_name + data)
        self.insertchatbox(msg)
        if peerID not in self.client.chatSessions:
            self.client.chatSessions[peerID] = [msg]
        else:
            self.client.chatSessions[peerID] += [msg]
        # new thread to send message
        thread = Thread(target=ClientProc.sendChatThread, args=(self.client, msg, peerID), daemon=True)
        thread.start()
        self.enter_text_widget.delete(1.0, 'end')
    def send_file(self, peerID):
        file_path = filedialog.askopenfilename(initialdir=os.path.sep, title='Choose file')
        filename = file_path.split('/').pop()
        # add message to self chatbox
        senders_name = self.client.nickname.strip() + ": "
        data = 'SEND ' + filename
        msg = (senders_name + data)
        self.insertchatbox(msg)
        if peerID not in self.client.chatSessions:
            self.client.chatSessions[peerID] = [msg]
        else:
            self.client.chatSessions[peerID] += [msg]
        # new thread to send the file
        thread = Thread(target=ClientProc.sendFileThread, args=(self.client, peerID, file_path), daemon=True)
        thread.start()


    # ------------------------- CHAT BOX UI -----------------------------
    #####################################################################
    def display_chat_box(self, sessionID=-1):
        self.chatframe = Frame()
        self.chatframe.pack(side='top', anchor='e')

        Label(self.chatframe, text='Chat Box:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(self.chatframe, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(self.chatframe, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')


        if sessionID != -1 and sessionID in self.client.chatSessions:
            self.chat_transcript_area.tag_configure('center', justify='center')
            self.chat_transcript_area.tag_configure('left', justify='left')
            self.chat_transcript_area.tag_configure('right', justify='right')
            for msg in self.client.chatSessions[sessionID]:
                self.insertchatbox(msg)

    def insertchatbox(self, msg):
        # centered SESSION_INIT
        if int(self.chat_transcript_area.index('end-1c').split('.')[0]) == 1:
            tag = 'center'
        # if the message belongs to self -> right, else left
        elif msg.split(':')[0] == self.client.nickname:
            tag = 'right'
        else:
            tag = 'left'
        self.chat_transcript_area.insert(END, msg + '\n', tag)
        self.chat_transcript_area.yview(END)

    def reset_chatbox(self, sessionID=-1):
        if self.frframe:
            self.frframe.pack_forget()
        if self.entryframe:
            self.entryframe.pack_forget()
        if self.chatframe:
            self.chatframe.pack_forget()
        self.display_chat_entry_box(sessionID)
        self.display_friend_box(sessionID)
        self.display_chat_box(sessionID)

    # ------------------------- CLOSE WINDOW UI -------------------------
    #####################################################################
    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            exit(0)

    # ------------------------- UTILS -----------------------------------
    #####################################################################
