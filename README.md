# Introdução
Este projeto foi desenvolvido como parte da disciplina de Sistemas Distribuídos da faculdade. O objetivo é implementar um sistema de chat distribuído utilizando RPC (Remote Procedure Call), permitindo que múltiplos clientes se conectem a servidores de chat de forma coordenada através de um binder central.

# Sistema de Chat Distribuído

Este é um sistema de chat distribuído utilizando RPC (Remote Procedure Call) para comunicação entre cliente e servidor. O sistema é composto por um **binder** para gerenciar a localização dos serviços disponíveis, um **servidor de chat** para o gerenciamento de usuários e salas de chat, e um **cliente de chat** que se conecta ao servidor para enviar e receber mensagens.

## Como Executar o Sistema

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado em seu sistema. Se ainda não o tiver, [baixe e instale o Python 3](https://www.python.org/downloads/).

### Passos para Executar

1. **Executar o Binder:**

   O binder gerencia os serviços registrados e permite que os clientes localizem os procedimentos disponíveis. Para executar o binder:

   - Navegue até o diretório onde o arquivo `binder.py` está localizado.
   - Execute o seguinte comando no terminal:

     python binder.py

   O binder será executado na porta **5000** e ficará aguardando registros e consultas de procedimentos.

2. **Executar o Servidor de Chat:**

   O servidor de chat gerencia os usuários e as salas de chat. Para executar o servidor de chat:

   - Navegue até o diretório onde o arquivo `chat_server.py` está localizado.
   - Execute o seguinte comando no terminal:

    python chat_server.py

   O servidor de chat será executado na porta **8000** e ficará aguardando conexões de clientes.

3. **Executar o Cliente de Chat:**

   O cliente de chat se conecta ao servidor de chat para enviar e receber mensagens. Para executar o cliente, basta rodar o script do cliente de acordo com sua implementação, utilizando o endereço do binder e do servidor de chat.

---

## Organização dos Métodos RPC no Binder

O **Binder** é responsável por registrar os serviços e permitir que os clientes os encontrem. Ele oferece dois métodos principais:

- **`register_procedure(procedure_name, address, port)`**

  Este método registra um procedimento RPC no binder. O nome do procedimento (como `chat_server`) é associado ao endereço e à porta onde o serviço está hospedado.

  **Parâmetros:**
  - `procedure_name`: Nome do procedimento a ser registrado.
  - `address`: Endereço IP ou hostname do servidor onde o procedimento está hospedado.
  - `port`: Porta onde o servidor está escutando.

  **Exemplo de uso:**

  binder.register_procedure('chat_server', 'localhost', 8000)

### `lookup_procedure(procedure_name)`

Este método permite que o cliente ou outro servidor procure um procedimento registrado pelo seu nome. Ele retorna o endereço e a porta do serviço registrado ou `None` se o serviço não for encontrado.

#### Parâmetros:
- `procedure_name`: Nome do procedimento que está sendo procurado.

#### Exemplo de uso:

procedure_info = binder.lookup_procedure('chat_server')
if procedure_info:
    address, port = procedure_info
else:
    print("Procedimento não encontrado.")


## Estrutura dos Arquivos

### `binder.py`

Este arquivo contém a implementação do binder, que gerencia os serviços RPC registrados. O binder mantém um dicionário de procedimentos registrados e permite que os clientes localizem serviços pelos seus nomes.

- **Métodos principais:**
  - `register_procedure`: Registra um procedimento RPC.
  - `lookup_procedure`: Procura um procedimento registrado.

### `chat_server.py`

Este arquivo contém a implementação do servidor de chat. O servidor gerencia usuários, salas de chat e as mensagens enviadas entre os usuários. Ele usa RPC para interagir com o binder e para permitir que os clientes se conectem ao chat.

- **Métodos principais:**
  - `register_user`: Registra um novo usuário no sistema.
  - `login_user`: Faz o login de um usuário ou o registra se não existir.
  - `create_room`: Cria uma nova sala de chat.
  - `join_room`: Permite que um usuário entre em uma sala.
  - `send_message`: Envia mensagens públicas ou privadas.
  - `receive_messages`: Recupera mensagens de uma sala para um usuário.
  - `list_rooms`: Lista todas as salas disponíveis.
  - `list_users`: Lista os usuários de uma sala específica.
  - `leave_room`: Permite que um usuário saia de uma sala.
  - `monitor_inactive_rooms`: Monitora e remove salas sem usuários após 5 minutos de inatividade.

### `client.py`

Este arquivo é responsável por implementar o cliente de chat. O cliente se conecta ao servidor, envia e recebe mensagens, e pode interagir com as salas de chat. O cliente utiliza a informação do binder para encontrar o servidor de chat.
