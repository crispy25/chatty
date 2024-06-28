from typing import Any, Tuple
import customtkinter as ctk
import threading
import socket

DEFAULT_PORT = 9999
MSG_SIZE = 1024

class LoginUI(ctk.CTkFrame):
    clicks = 0
    user_nickname = ''

    def __click__(self):
        LoginUI.clicks += 1
        if LoginUI.clicks == 1:
            LoginUI.user_nickname = self.entry.get()
            self.name_input.delete(0, 'end')
            self.hint_label.destroy()
            self.hint_label = ctk.CTkLabel(master=self, text='Enter server IP', font=('Kozuka Mincho Pro R', 20))
            self.hint_label.place(relx=0.3, rely=0.42)
        else:
            LoginUI.server_ip = self.entry.get()
            if LoginUI.user_nickname == '':
                LoginUI.user_nickname = 'anonymus-bob'
            if LoginUI.server_ip == '':
                LoginUI.server_ip = '127.0.0.1'
            
            try:
                self.master.connect(LoginUI.server_ip)
                self.destroy()
            except Exception as e:
                self.name_input.delete(0, 'end')
                print(f'Can\'t connect to the server: {e}')

    def __init__(self, master: Any, width: int = 200, height: int = 200, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str, str] = "transparent", fg_color: str | Tuple[str, str] | None = None, border_color: str | Tuple[str, str] | None = None, background_corner_colors: Tuple[str | Tuple[str, str]] | None = None, overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.entry = ctk.StringVar(self)

        self.name_label = ctk.CTkLabel(master=self, text='Chatty', font=('Kozuka Mincho Pro R', 44, 'bold'))
        self.name_label.place(relx=0.44, rely=0.2)
        
        self.hint_label = ctk.CTkLabel(master=self, text='Enter nickname', font=('Kozuka Mincho Pro R', 20))
        self.hint_label.place(relx=0.3, rely=0.42)

        self.name_input = ctk.CTkEntry(master=self, fg_color='black', placeholder_text='Nickname', textvariable=self.entry)
        self.name_input.place(relx=0.3, rely=0.5, relwidth=0.4)

        self.button = ctk.CTkButton(master=self, text='GO', command=self.__click__)
        self.button.place(relx=0.7, rely=0.5, relwidth=0.07)


class TextFrame(ctk.CTkScrollableFrame):
    def __init__(self, master: Any, width: int = 200, height: int = 200, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str] = "transparent", fg_color: str | Tuple[str] | None = None, border_color: str | Tuple[str] | None = None, scrollbar_fg_color: str | Tuple[str] | None = None, scrollbar_button_color: str | Tuple[str] | None = None, scrollbar_button_hover_color: str | Tuple[str] | None = None, label_fg_color: str | Tuple[str] | None = None, label_text_color: str | Tuple[str] | None = None, label_text: str = "", label_font: Tuple | ctk.CTkFont | None = None, label_anchor: str = "center"):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, scrollbar_fg_color, scrollbar_button_color, scrollbar_button_hover_color, label_fg_color, label_text_color, label_text, label_font, label_anchor)


class MainUI(ctk.CTkFrame):
    def __init__(self, master: Any, width: int = 200, height: int = 200, corner_radius: int | str | None = None, border_width: int | str | None = None, bg_color: str | Tuple[str] = "transparent", fg_color: str | Tuple[str] | None = None, border_color: str | Tuple[str] | None = None, background_corner_colors: Tuple[str | Tuple[str]] | None = None, overwrite_preferred_drawing_method: str | None = None, **kwargs):
        super().__init__(master, width, height, corner_radius, border_width, bg_color, fg_color, border_color, background_corner_colors, overwrite_preferred_drawing_method, **kwargs)
        self.entry = ctk.StringVar()

        self.login_ui = LoginUI(master=self)
        self.login_ui.pack(expand=True, fill='both')

        self.text_frame = TextFrame(master=self)

        self.input = ctk.CTkEntry(master=self, fg_color='gray', textvariable=self.entry)
        self.input.focus_set()
        self.input.bind('<Return>', self.send_message)

        self.sck = None

    def send_message(self, event):
        line = self.input.get()
        self.input.delete(0, 'end')

        if line == '':
            return

        if line == 'exit':
            line = f'{LoginUI.user_nickname} left!'
            self.sck.sendall(line.encode())
            self.sck.close()
            exit(0)

        line = f'{LoginUI.user_nickname}: {line}'
        self.sck.sendall(line.encode())

    def recv_from_server(self, sck):
        while True:
            try:
                line = sck.recv(MSG_SIZE)

                new_label = ctk.CTkLabel(self.text_frame, text=line, font=('Kozuka Mincho Pro R', 20))
                new_label.pack(padx=20, anchor=ctk.W)
            except Exception as e:
                print('Disconnected')
                break

    def connect(self, host):
        self.sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sck.connect((get_host_ip(host), get_port(host)))

        recv_thread = threading.Thread(target=self.recv_from_server, args=(self.sck,), daemon=True)
        recv_thread.start()

        line = f'{LoginUI.user_nickname} joined!'
        self.sck.sendall(line.encode())

        self.text_frame.pack(expand=True, fill='both')
        self.input.pack(fill='x')


def get_host_ip(host_address: str):
    if ':' not in host_address:
        return host_address
    else:
        return host_address.partition(':')[0]


def get_port(host_address: str):
    if ':' not in host_address:
        return DEFAULT_PORT
    else:
        return int(host_address.partition(':')[2])


def run_client():
    app = ctk.CTk()
    app.title('Chatty')
    app.geometry('1000x800')

    main_ui = MainUI(app)
    main_ui.pack(expand=True, fill='both')

    app.mainloop()


if __name__ == '__main__':
    run_client()
