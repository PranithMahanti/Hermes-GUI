import socket
import threading

import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

class GUIClient:
    def __init__(self):
        msg = tkinter.Tk()
        msg.withdraw()

        self.host= simpledialog.askstring("Server", "Enter the host adddress: ", parent=msg)
        self.port = 47777

        self.nick = simpledialog.askstring("Nickname: ", "Enter your nickname: ", parent=msg)
        print(f"{self.host}:{self.port} with {self.nick}")

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client = client
            self.client.connect((self.host, self.port))
        except ConnectionRefusedError:
            print(f"The server {self.host} is currently down and not taking any connections.")

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        rec_thread = threading.Thread(target=self.recieve)

        gui_thread.start()
        rec_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(background="lightblue")

        self.chat_label = tkinter.Label(self.win, text="Chat: ", bg="lightblue")
        self.chat_label.config(font=("Arial", 15))
        self.chat_label.pack(padx=12, pady=9)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=12, pady=9)
        self.text_area.config(state="disabled")

        self.msg_label = tkinter.Label(self.win, text="Message: ", bg="lightblue")
        self.msg_label.config(font=("Roboto", 15))
        self.msg_label.pack(padx=12, pady=9)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=12, pady=9)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write)
        self.win.bind("<Return>", self.write)
        self.send_button.config(font=("Arial", 15))
        self.send_button.pack(padx=12, pady=9)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self, event=None):
        message = f"{self.nick}: {self.input_area.get('1.0', 'end').strip()}\n"
        self.client.send(message.encode('utf-8'))

        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.client.close()
        exit(0)

    def recieve(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == "REQ_NICK":
                    self.client.send(self.nick.encode('ascii'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message)
                        self.text_area.yview('end')

                        self.text_area.config(state="disabled")

            except ConnectionAbortedError:
                break

            except:
                print("Error occurred")
                self.client.close()
                break


if __name__=="__main__":
    client = GUIClient()
