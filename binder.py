import xmlrpc.server
import xmlrpc.client


class Binder:
    def __init__(self):
        # Dicionário para armazenar os procedimentos registrados, onde a chave é o nome do procedimento
        # e o valor é uma tupla contendo o endereço e a porta onde o procedimento está hospedado
        self.procedures = {}

    def register_procedure(self, procedure_name, address, port):
        # Registra um método RPC no binder com seu nome, endereço e porta.
        self.procedures[procedure_name] = (address, port)
        print(f"Procedure {procedure_name} registered at {address}:{port}")

    def lookup_procedure(self, procedure_name):
        # Consulta um procedimento registrado no binder.
        if procedure_name in self.procedures:
            return self.procedures[procedure_name]  # Retorna o endereço e a porta do procedimento
        else:
            return None  # Retorna None se o procedimento não for encontrado


def run_binder():
    # Cria uma instância do Binder
    binder = Binder()

    # Endereço e porta do servidor de chat
    server_address = 'localhost'
    server_port = 8000

    # Registro do servidor de chat no binder com o nome 'chat_server'
    binder.register_procedure('chat_server', server_address, server_port)

    # Configura o servidor XML-RPC para escutar na porta 5000
    server = xmlrpc.server.SimpleXMLRPCServer(('localhost', 5000))
    # Registra a instância do binder como um serviço RPC que pode ser acessado remotamente
    server.register_instance(binder)

    print("Binder is running on port 5000...")
    # Inicia o servidor para escutar e responder as requisições
    server.serve_forever()


if __name__ == '__main__':
    # Executa a função run_binder quando o script é chamado
    run_binder()
