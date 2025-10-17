import json
import logging
import os
import sys
import xmlrpc.server
from datetime import datetime, timedelta
import threading
import time

class ChatServer:
    def __init__(self):
        self.users = {}  # Armazena os usuários registrados
        self.rooms = {}  # Armazena as salas de chat
        self.lock = threading.Lock()  # Lock para garantir acesso seguro de múltiplas threads

        # Criação e carregamento do arquivo JSON de dados
        self.load_or_create_user_data()
        
        # Inicia a thread de monitoramento de salas inativas
        threading.Thread(target=self.monitor_inactive_rooms, daemon=True).start()

    def load_or_create_user_data(self):
        #Cria ou carrega dados de usuários e salas do arquivo JSON.
        if not os.path.exists('user_data.json'):
            # Cria o arquivo JSON caso não exista
            with open('user_data.json', 'w') as f:
                json.dump({'users': {}}, f)
        
        # Carrega os dados do arquivo JSON
        with open('user_data.json', 'r') as f:
            data = json.load(f)
            self.users = data.get('users', {})

    def save_user_data(self):
        #Salva os dados de usuários no arquivo JSON.
        data = {
            'users': self.users,
        }
        with open('user_data.json', 'w') as f:
            json.dump(data, f)

    def register_user(self, username, password):
        #Registra um novo usuário.
        if username in self.users:
            raise Exception(f"Nome de usuário '{username}' já está em uso.")
        self.users[username] = {'password': password}
        print(f"Usuário '{username}' registrado com sucesso!")
        self.save_user_data()  # Salva os dados após o registro
        return True

    def login_user(self, username, password):
        #Realiza o login ou registro do usuário. Se o usuário não existir, ele é registrado.
        if username not in self.users:
            # Se o usuário não existir, realiza o registro
            print(f"Usuário '{username}' não encontrado. Registrando...")  
            return self.register_user(username, password)  # Registra o usuário se não existir

        # Verifica a senha caso o usuário exista
        if self.users[username]['password'] != password:
            raise Exception("Senha incorreta.")
        
        print(f"Usuário '{username}' logado com sucesso!")
        return True

    def create_room(self, room_name):
        #Cria uma nova sala de chat.
        if room_name in self.rooms:
            raise Exception(f"Já existe uma sala com o nome '{room_name}'.")
        with self.lock:
            self.rooms[room_name] = {
                'users': [],  # Lista de usuários na sala
                'messages': [],  # Lista de mensagens na sala
                'last_active': datetime.now()  # Hora da última atividade
            }
        print(f"Sala '{room_name}' criada com sucesso!")
        self.save_user_data()  # Salva os dados após a criação da sala
        return True

    def join_room(self, username, room_name):
        #Permite que um usuário entre em uma sala de chat.
        if room_name not in self.rooms:
            raise Exception(f"A sala '{room_name}' não existe.")
        if username not in self.users:
            raise Exception(f"Usuário '{username}' não registrado.")
        
        with self.lock:
            room = self.rooms[room_name]
            if username not in room['users']:
                room['users'].append(username)

            # Adiciona a sala à lista de salas do usuário, caso não exista
            if 'rooms' not in self.users[username]:
                self.users[username]['rooms'] = []
            
            self.users[username]['rooms'].append(room_name)  # Adiciona a sala à lista do usuário
            room['last_active'] = datetime.now()

        print(f"Usuário '{username}' entrou na sala '{room_name}'.")
        return {
            'users': room['users'],
            'messages': room['messages'][-50:]  # Exibe as últimas 50 mensagens
        }

    def send_message(self, username, room_name, message, recipient=None):
        #Envia uma mensagem para uma sala (ou privada).
        if room_name not in self.rooms:
            raise Exception(f"A sala '{room_name}' não existe.")
        if username not in self.users:
            raise Exception(f"Usuário '{username}' não registrado.")
        
        timestamp = datetime.now().strftime("%H:%M")  # Formata o timestamp da mensagem

        with self.lock:
            room = self.rooms[room_name]
            room['last_active'] = datetime.now()  # Atualiza a última atividade da sala
            msg = {
                'type': 'unicast' if recipient else 'broadcast',  # Tipo de mensagem: unicast ou broadcast
                'from': username,
                'to': recipient if recipient else None,  # Definindo o destinatário, se houver
                'message': message,
                'timestamp': timestamp  # Adiciona o timestamp à mensagem
            }
            room['messages'].append(msg)

        # Exibe a mensagem no console
        if recipient:
            print(f"Mensagem privada enviada por {username} para {recipient} na sala '{room_name}'")
        else:
            print(f"Mensagem enviada por {username} na sala '{room_name}': {message} ({'Pública'})")

    def receive_messages(self, username, room_name):
        #Recupera mensagens de uma sala para um usuário específico.
        if room_name not in self.rooms:
            raise Exception(f"A sala '{room_name}' não existe.")
        if username not in self.users:
            raise Exception(f"Usuário '{username}' não registrado.")
        
        room = self.rooms[room_name]
        relevant_messages = [
            msg for msg in room['messages'] 
            if msg.get('to') == username or msg['type'] == 'broadcast'
        ]
        return relevant_messages

    def list_rooms(self):
        #Lista todas as salas disponíveis.
        return list(self.rooms.keys())

    def list_users(self, room_name):
        #Lista todos os usuários em uma sala específica.
        if room_name not in self.rooms:
            raise Exception(f"A sala '{room_name}' não existe.")
        return self.rooms[room_name]['users']

    def leave_room(self, room_name, username):
        #Permite que um usuário saia de uma sala de chat.
        if room_name not in self.rooms:
            raise Exception(f"A sala '{room_name}' não existe.")
        if username not in self.users:
            raise Exception(f"Usuário '{username}' não registrado.")
        with self.lock:
            room = self.rooms[room_name]
            if username in room['users']:
                room['users'].remove(username)

            # Remove a sala da lista de salas do usuário
            if 'rooms' in self.users[username]:
                if room_name in self.users[username]['rooms']:
                    self.users[username]['rooms'].remove(room_name)

            if not room['users']:  # Atualiza a inatividade se a sala ficou vazia
                room['last_active'] = datetime.now()
        
        print(f"Usuário '{username}' saiu da sala '{room_name}'.")
        return True

    def is_user_in_room(self, username, room_name):
        #Verifica se um usuário está em uma sala específica.
        return room_name in self.rooms and username in self.rooms[room_name]['users']

    def monitor_inactive_rooms(self):
        #Monitora e remove salas sem usuários conectados após 5 minuto de inatividade."""
        while True:
            time.sleep(60)  # Verifica a cada minuto
            with self.lock:
                now = datetime.now()
                inactive_rooms = [
                    room_name for room_name, room_data in self.rooms.items()
                    if not room_data['users'] and now - room_data['last_active'] > timedelta(minutes=5)
                ]
                for room_name in inactive_rooms:
                    del self.rooms[room_name]
                    print(f"Sala '{room_name}' removida por inatividade.")
                self.save_user_data()  # Salva os dados após remover salas inativas

    def setup_logger(self):
        # Configura o logger para redirecionar logs para um arquivo e o console.
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)  # Cria a pasta "logs" se não existir

        # Nome do arquivo de log com timestamp
        timestamp = datetime.now().strftime("%H-%M_%d-%m-%Y")
        log_file = os.path.join(log_dir, f"{timestamp}.txt")

        # Obtém o logger principal
        logger = logging.getLogger()

        # Verifica se o logger já está configurado
        if logger.hasHandlers():
            return  # Evita reconfiguração e múltiplos handlers

        logger.setLevel(logging.INFO)

        # Configura um FileHandler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        # Configura um StreamHandler para o console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(file_format)
        logger.addHandler(console_handler)

        # Redireciona o print para logging.info
        global print
        print = logger.info


def main():
    
    # Configura o logger
    ChatServer().setup_logger()

    logging.basicConfig(level=logging.CRITICAL)  # Ignora logs repetitivos de requisição no server.
    server = xmlrpc.server.SimpleXMLRPCServer(('localhost', 8000), allow_none=True)
    server.register_instance(ChatServer())
    print("Servidor de chat em execução na porta 8000...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo administrador.")
        # Deleta o arquivo JSON quando o servidor for encerrado
        if os.path.exists('user_data.json'):
            os.remove('user_data.json')

if __name__ == '__main__':
    main()
