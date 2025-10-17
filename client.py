import time
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import xmlrpc.client
import threading

class ChatClientGUI:
    def __init__(self, master, binder_url):
        self.master = master
        self.master.title("Chat Distribuído")
        self.binder = xmlrpc.client.ServerProxy(binder_url)  # Conexão com o binder para buscar o servidor de chat
        self.chat_server = None  # Inicializa a variável do servidor de chat como None
        self.username = None  # Inicializa o nome de usuário como None
        self.current_room = None  # Inicializa a sala atual como None
        self.json_file = "user_data.json"  # Arquivo para armazenar dados do usuário
        self.keep_updating = False  # Flag para controle de atualização contínua de mensagens

        self.master.geometry("500x300")  # Define o tamanho inicial da janela (300x300 pixels)

        
        # Lock para garantir que apenas uma requisição seja feita por vez
        self.lock = threading.Lock()
        self.server_lock = threading.Lock()

        # Criação da tela de login
        self.create_login_screen()

    def connect_to_server(self):
        #Conecta ao servidor de chat usando o binder para encontrar o endereço.
        try:
            server_address, server_port = self.binder.lookup_procedure('chat_server')
            server_url = f'http://{server_address}:{server_port}'
            self.chat_server = xmlrpc.client.ServerProxy(server_url)  # Conecta ao servidor de chat
        except xmlrpc.client.Fault as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor: {e}")

    def save_user_data(self):
        #Salva os dados do usuário em um arquivo JSON.
        with open(self.json_file, "w") as f:
            json.dump({"username": self.username}, f)

    def load_user_data(self):
        #Carrega os dados do usuário de um arquivo JSON, se existir.
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
                self.username = data["username"]
                return True  # Retorna True se os dados foram carregados com sucesso
        except FileNotFoundError:
            return False  # Retorna False se o arquivo não for encontrado

    def create_login_screen(self):
        #Cria a tela de login para o usuário se registrar ou fazer login.
        self.clear_screen()  # Limpa a tela antes de criar o conteúdo da tela de login
        self.master.config(bg="#2c3e50") # Define cor do background da tela

        # Nome de usuário
        tk.Label(self.master, text="Usuário:", font=("Helvetica", 12), bg="#2c3e50", fg="#ecf0f1").pack(pady=5)
        username_entry = tk.Entry(self.master, font=("Helvetica", 12), bd=2, relief="solid", fg="#000000", bg="#FAFAFA", justify="center")
        username_entry.pack(pady=10, ipady=5, ipadx=10)

         # Senha
        tk.Label(self.master, text="Senha:", font=("Helvetica", 12), bg="#2c3e50", fg="#ecf0f1").pack(pady=5)
        password_entry = tk.Entry(self.master, font=("Helvetica", 12), bd=2, relief="solid", fg="#000000", bg="#FAFAFA", show="*", justify="center")
        password_entry.pack(pady=10, ipady=5, ipadx=10)

        def login_or_register():
            #Função para logar ou registrar o usuário.
            username = username_entry.get().strip()  # Obtém o nome de usuário
            password = password_entry.get().strip()  # Obtém a senha
            if not username:
                messagebox.showerror("Erro", "Usuário não pode estar vazio.")  # Verifica se o nome de usuário é vazio
                return

            try:
                self.connect_to_server()  # Conectar ao servidor de chat

                # Tenta fazer login ou registrar o usuário
                if self.chat_server.login_user(username, password):  
                    self.username = username
                    self.save_user_data()  # Salva os dados do usuário
                    self.create_room_screen()  # Cria a tela de seleção de sala
                else:
                    messagebox.showerror("Erro", "Usuário já registrado.")
            except xmlrpc.client.Fault as e:
                messagebox.showerror("Erro", f"Erro ao registrar: {e}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro desconhecido: {e}")
        
        # Botão de Login / Registro
        login_button = tk.Button(self.master, text="Login / Registrar", font=("Helvetica", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", command=login_or_register, activebackground="#2980b9")
        login_button.pack(pady=15, ipadx=20, ipady=10)

        # Efeito de hover no botão (Função extra para melhorar a interação)
        self.add_hover_effect(login_button)

    def create_room_screen(self):
        #Cria a tela de criação de sala e navegação entre salas.
        self.clear_screen()  # Limpa a tela antes de criar a nova tela
        self.master.geometry("500x450")  # Define o tamanho da tela
        self.master.config(bg="#2c3e50") # Define cor do background da tela
        # Estilo para o título
        welcome_label = tk.Label(self.master, text=f"Bem-vindo, {self.username}", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="#ecf0f1")
        welcome_label.pack(pady=20)

        def create_room():
            #Função para criar uma nova sala.
            room_name = self.ask_room_name()  # Solicita o nome da nova sala
            if room_name:
                try:
                    if self.chat_server.create_room(room_name):  # Tenta criar a sala
                        self.show_custom_message("Sucesso", f"Sala '{room_name}' criada.")
                except xmlrpc.client.Fault as e:
                    self.show_custom_message("Erro", f"Erro ao criar sala: {e}")

        def list_rooms():
            #Função para listar as salas disponíveis.
            try:
                rooms = self.chat_server.list_rooms()  # Obtém a lista de salas
                self.show_custom_message("Salas Disponíveis", "\n".join(rooms))  # Exibe as salas em uma janela personalizada
            except xmlrpc.client.Fault as e:
                self.show_custom_message("Erro", f"Erro ao listar salas: {e}")

        # Botões para criação, listagem e entrada nas salas
        button_frame = tk.Frame(self.master, bg="#2c3e50")
        button_frame.pack(pady=20)

        create_room_button = tk.Button(button_frame, text="Criar Sala", font=("Helvetica", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", command=create_room, activebackground="#2980b9")
        create_room_button.grid(row=0, column=0, padx=20, pady=10, ipadx=15, ipady=10)

        list_rooms_button = tk.Button(button_frame, text="Listar Salas", font=("Helvetica", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", command=list_rooms, activebackground="#2980b9")
        list_rooms_button.grid(row=1, column=0, padx=20, pady=10, ipadx=15, ipady=10)

        join_room_button = tk.Button(button_frame, text="Entrar em Sala", font=("Helvetica", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", command=self.join_room, activebackground="#2980b9")
        join_room_button.grid(row=2, column=0, padx=20, pady=10, ipadx=15, ipady=10)

        exit_button = tk.Button(button_frame, text="Sair", font=("Helvetica", 12, "bold"), fg="#fff", bg="#e74c3c", relief="flat", command=self.master.quit, activebackground="#c0392b")
        exit_button.grid(row=3, column=0, padx=20, pady=10, ipadx=15, ipady=10)

        # Efeitos de hover nos botões (Funções para interação visual)
        self.add_hover_effect(create_room_button)
        self.add_hover_effect(list_rooms_button)
        self.add_hover_effect(join_room_button)
        self.add_hover_effect(exit_button)
    
    def create_chat_screen(self):
        #Cria a tela principal de chat onde as mensagens são enviadas e recebidas.
        self.master.geometry("600x650")  # Define o tamanho da tela de chat
        self.master.config(bg="#2c3e50")

        for widget in self.master.winfo_children():
            widget.destroy()  # Limpa a tela antes de criar a nova tela de chat

        # Exibe a sala atual
        tk.Label(self.master, text=f"Sala atual: {self.current_room}", font=("Arial", 16, "bold"), fg="#ecf0f1", bg="#2c3e50").pack(pady=20)

        # Frame para a área de mensagens
        messages_frame = tk.Frame(self.master, bg="#FAFAFA")
        messages_frame.pack(pady=10)

        # Listbox onde as mensagens serão exibidas
        self.message_list = tk.Listbox(messages_frame, width=50, height=20, font=("Arial", 12), bg="#2a3947", fg="#fafafa", bd=0, highlightthickness=0)
        self.message_list.pack(side=tk.LEFT, fill=tk.BOTH)

        # Barra de rolagem para as mensagens
        scrollbar = tk.Scrollbar(messages_frame, bg="#34495e")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.message_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.message_list.yview)

        # Frame para o campo de entrada de mensagens e destinatário
        input_frame = tk.Frame(self.master, bg="#2c3e50")
        input_frame.pack(pady=10)

        # Campo de entrada de mensagem
        message_entry = tk.Entry(input_frame, width=40, font=("Arial", 12), bg="#FAFAFA", fg="#000000", relief="flat", bd=2)
        message_entry.pack(side=tk.LEFT, padx=5)

        # Campo de entrada do destinatário
        recipient_entry = tk.Entry(input_frame, width=20, font=("Arial", 12), bg="#FAFAFA", fg="#000000", relief="flat", bd=2)
        recipient_entry.insert(0, "Para (opcional)")  # Placeholder para o destinatário
        recipient_entry.pack(side=tk.LEFT, padx=5)

        # Inicia a atualização automática do chat
        self.update_chat()
        
        def list_users():
            #Lista os usuários na sala atual.
            try:
                with self.server_lock:  # Garante que apenas uma requisição seja feita por vez
                    users = self.chat_server.list_users(self.current_room)
                if users:
                    self.show_custom_message("Usuários na sala", "\n".join(users))
                else:
                    self.show_custom_message("Usuários na sala", "Nenhum usuário encontrado.")
            except xmlrpc.client.Fault as e:
                self.show_custom_message("Erro", f"Erro ao listar usuários: {e}")
            except Exception as e:
                self.show_custom_message("Erro", f"Erro desconhecido: {e}")

        # Botões para enviar mensagem, listar usuários e sair da sala
        button_frame = tk.Frame(self.master, bg="#2c3e50")
        button_frame.pack(pady=20)

        send_button = tk.Button(button_frame, text="Enviar", command=lambda: self.send_message(message_entry, recipient_entry), font=("Arial", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", activebackground="#2980b9")
        send_button.grid(row=0, column=0, padx=10, pady=10, ipadx=15, ipady=10)

        list_users_button = tk.Button(button_frame, text="Listar Usuários", command=list_users, font=("Arial", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", activebackground="#2980b9")
        list_users_button.grid(row=0, column=1, padx=10, pady=10, ipadx=15, ipady=10)

        leave_room_button = tk.Button(button_frame, text="Sair da Sala", command=self.leave_room, font=("Arial", 12, "bold"), fg="#fff", bg="#e74c3c", relief="flat", activebackground="#c0392b")
        leave_room_button.grid(row=0, column=2, padx=10, pady=10, ipadx=15, ipady=10)

        # Efeitos de hover nos botões
        self.add_hover_effect(send_button)
        self.add_hover_effect(list_users_button)
        self.add_hover_effect(leave_room_button)

    def join_room(self):
        #Permite o usuário entrar em uma sala de chat.
        room_name = self.ask_room_name()  # Solicita o nome da sala
        if room_name:
            try:
                self.chat_server.join_room(self.username, room_name)  # Tenta entrar na sala
                self.current_room = room_name
                self.create_chat_screen()  # Cria a tela de chat após entrar na sala
            except xmlrpc.client.Fault as e:
                self.show_custom_message("Erro", f"Erro ao entrar na sala: {e}")

    def leave_room(self):
        #Deixa a sala atual e retorna à tela de criação de salas.
        with self.server_lock:
            self.chat_server.leave_room(self.current_room, self.username)  # Sai da sala
        self.current_room = None  # Limpa a sala atual
        self.create_room_screen()  # Cria a tela de criação de sala

    def send_message(self, message_entry, recipient_entry):
        #Envia uma mensagem para a sala ou um usuário específico.
        message = message_entry.get().strip()  # Obtém a mensagem
        recipient = recipient_entry.get().strip()  # Obtém o destinatário
        
        if message:
            try:
                with self.server_lock:
                    # Verifica se o destinatário é válido (não está vazio)
                    recipient = recipient if recipient != "Para (opcional)" else ""
                    
                    # Verifica se o destinatário está na sala atual
                    if recipient:
                        if not self.chat_server.is_user_in_room(recipient, self.current_room):
                            self.show_custom_message("Erro", f"O usuário '{recipient}' não está na sala atual.")
                            return
                    
                    # Envia a mensagem
                    self.chat_server.send_message(self.username, self.current_room, message, recipient)
                
                # Limpa os campos de entrada após o envio
                message_entry.delete(0, tk.END)
                recipient_entry.delete(0, tk.END)
                recipient_entry.insert(0, "Para (opcional)")  # Redefine o campo do destinatário
            
            except xmlrpc.client.Fault as e:
                messagebox.showerror("Erro", f"Erro ao enviar mensagem: {e}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro desconhecido: {e}")

    def update_chat(self):
        #Atualiza as mensagens da sala em tempo real.
        def fetch_and_update():
            while True:
                try:
                    if self.current_room:  # Verifica se o cliente está em uma sala
                        with self.server_lock:  # Garante que apenas uma thread acesse o servidor
                            new_messages = self.chat_server.receive_messages(self.username, self.current_room)

                        if new_messages is None:
                            new_messages = []  # Inicializa a lista de mensagens se estiver vazia

                        def update_gui():
                            try:
                                self.message_list.delete(0, tk.END)  # Limpa a lista de mensagens
                                for msg in new_messages:
                                    timestamp = msg['timestamp']
                                    if msg['type'] == 'broadcast':
                                        display_message = f"[{timestamp}] {msg['from']}: {msg['message']}"
                                    elif msg['type'] == 'unicast' and msg['to'] == self.username:
                                        display_message = f"[{timestamp}] (Privado) {msg['from']}: {msg['message']}"
                                    else:
                                        continue

                                    self.message_list.insert(tk.END, display_message)  # Adiciona a mensagem à lista
                            except tk.TclError:
                                pass  # Ignora erros se os widgets foram destruídos

                        if self.current_room:
                            self.master.after(0, update_gui)  # Atualiza a GUI com as novas mensagens
                except Exception as e:
                    print(f"Erro ao atualizar mensagens: {e}")
                time.sleep(1)  # Atraso entre as atualizações de mensagens

        # Inicia a thread que atualiza as mensagens
        threading.Thread(target=fetch_and_update, daemon=True).start()

    def clear_screen(self):
        #Limpa todos os widgets da tela.
        for widget in self.master.winfo_children():
            widget.destroy()


    # -------------------     Funções voltadas apenas para o Style da aplicação       --------------------# 

    def ask_room_name(self):
        #Função personalizada para solicitar o nome da sala.
        room_name_window = tk.Toplevel(self.master)
        room_name_window.title("Inserir nome da sala")
        room_name_window.geometry("350x200")
        room_name_window.config(bg="#34495e")

        # Título da janela
        title_label = tk.Label(room_name_window, text="Digite o nome da sala", font=("Helvetica", 14, "bold"), fg="#ecf0f1", bg="#34495e")
        title_label.pack(pady=10)

        # Caixa de entrada para o nome da sala
        room_name_entry = tk.Entry(room_name_window, font=("Helvetica", 12), bg="#FAFAFA", fg="#000000", relief="flat", bd=2, width=20)
        room_name_entry.pack(pady=10)

        # Variável para armazenar o nome da sala
        room_name_var = tk.StringVar()

        # Função para fechar a janela e retornar o nome da sala
        def submit_room_name():
            room_name_var.set(room_name_entry.get().strip())  # Atribui o valor ao StringVar
            room_name_window.destroy()

        # Botão de confirmação
        submit_button = tk.Button(room_name_window, text="Confirmar", font=("Helvetica", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", command=submit_room_name, activebackground="#2980b9")
        submit_button.pack(pady=10)

        # Aguardar o nome da sala ser preenchido
        room_name_window.wait_window()  # Espera até que a janela seja fechada
        return room_name_var.get()  # Retorna o nome da sala digitado
    
    def add_hover_effect(self, button):
        #Função para adicionar efeito de hover aos botões.
        original_bg = button.cget("bg")

        def darken_color(color):
            # Converte a cor hex para RGB
            rgb = self.hex_to_rgb(color)
            # Escurece a cor, reduzindo cada componente
            darkened_rgb = tuple(max(c - 40, 0) for c in rgb)
            return self.rgb_to_hex(darkened_rgb)


        button.bind("<Enter>", lambda e: button.config(bg=darken_color(original_bg)))
        button.bind("<Leave>", lambda e: button.config(bg=original_bg))

    def hex_to_rgb(self, hex_color):
        #Converte uma cor hexadecimal em uma tupla de valores RGB.
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        #Converte uma tupla RGB em uma cor hexadecimal.
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

    def show_custom_message(self, title, message):
        #Função para exibir uma janela personalizada com a mensagem.
        message_window = tk.Toplevel(self.master)
        message_window.title(title)
        message_window.geometry("350x200")
        message_window.config(bg="#34495e")

        # Título da mensagem
        title_label = tk.Label(message_window, text=title, font=("Helvetica", 16, "bold"), fg="#ecf0f1", bg="#34495e")
        title_label.pack(pady=10)

        # Texto da mensagem
        message_label = tk.Label(message_window, text=message, font=("Helvetica", 12), fg="#ecf0f1", bg="#34495e", justify="left")
        message_label.pack(pady=20)

        # Botão de OK
        ok_button = tk.Button(message_window, text="OK", font=("Helvetica", 12, "bold"), fg="#fff", bg="#3498db", relief="flat", command=message_window.destroy)
        ok_button.pack(pady=10, ipadx=10, ipady=5)

        # Arredondar o botão OK
        ok_button.config(relief="flat", activebackground="#2980b9")
        ok_button.bind("<Enter>", lambda e: ok_button.config(bg="#2980b9"))
        ok_button.bind("<Leave>", lambda e: ok_button.config(bg="#3498db"))
    
    #--------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    binder_url = 'http://localhost:5000'  # URL do binder
    root = tk.Tk()
    client_gui = ChatClientGUI(root, binder_url)
    root.protocol("WM_DELETE_WINDOW", lambda: [client_gui.leave_room() if client_gui.current_room else None, root.destroy()])
    root.mainloop()  # Inicia a interface gráfica
