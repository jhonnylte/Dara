import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432

def receber_mensagens(sock):
    """Thread que roda em segundo plano apenas ouvindo o servidor."""
    while True:
        try:
            mensagem = sock.recv(4096).decode('utf-8')
            if not mensagem:
                print("\n[Servidor desconectado]")
                break
            
            # Imprime a mensagem ou o tabuleiro enviado pelo servidor
            print(f"\n{mensagem}")
            
        except ConnectionAbortedError:
            break
        except Exception as e:
            print(f"\n[Erro na conexão]: {e}")
            break
    
    # Se sair do loop, encerra o programa
    sock.close()
    sys.exit()

def iniciar_cliente():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("[ERRO] Não foi possível conectar ao servidor.")
        return

    # Inicia a thread para receber mensagens do servidor continuamente
    thread_escuta = threading.Thread(target=receber_mensagens, args=(cliente_socket,))
    thread_escuta.daemon = True  # A thread morre quando o programa principal fechar
    thread_escuta.start()

    print("Conectado ao servidor! Aguardando instruções...")

    # O loop principal fica livre para capturar a digitação do usuário
    try:
        while True:
            # Aguarda o jogador digitar algo
            jogada = input()
            if jogada.lower() == 'sair':
                break
            
            # Envia a jogada para o servidor
            cliente_socket.sendall(jogada.encode('utf-8'))
            
    except KeyboardInterrupt:
        print("\nSaindo do jogo...")

    cliente_socket.close()

if __name__ == "__main__":
    iniciar_cliente()