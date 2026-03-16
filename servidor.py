import socket
import threading
from dara import DaraGame  # Importa a lógica que criamos na Fase 2

HOST = '127.0.0.1'
PORT = 65432

# Variáveis globais para gerenciar o jogo e os clientes
jogo = DaraGame()
clientes = {}  # Mapeia {numero_do_jogador: conexao_socket}
lock = threading.Lock()  # Protege o jogo para que duas threads não mexam nele ao mesmo tempo

def formatar_tabuleiro():
    """Cria uma string do tabuleiro para enviar aos clientes via rede."""
    simbolos = {0: '.', 1: 'X', 2: 'O'}
    texto = "\n  0 1 2 3 4 5\n"
    for i, row in enumerate(jogo.board):
        linha_formatada = " ".join([simbolos[cell] for cell in row])
        texto += f"{i} {linha_formatada}\n"
    
    texto += f"\nTurno: Jogador {jogo.current_player} ({simbolos[jogo.current_player]})"
    texto += f" | Fase: {jogo.game_phase}"
    if jogo.waiting_for_capture:
        texto += " | [!] ESPERANDO CAPTURA!"
    texto += f"\nPeças fora do tabuleiro -> J1: {jogo.pieces_to_drop[1]} | J2: {jogo.pieces_to_drop[2]}\n"
    return texto

def enviar_para_todos(mensagem):
    """Envia uma mensagem para os dois jogadores."""
    for conn in clientes.values():
        try:
            conn.sendall(mensagem.encode('utf-8'))
        except:
            pass

def lidar_com_cliente(conn, player_num):
    """Função que roda em uma Thread separada para cada jogador."""
    while True:
        try:
            dados = conn.recv(1024).decode('utf-8').strip()
            if not dados:
                break

            # Bloqueia outras threads enquanto processa esta jogada
            with lock:
                # Verifica se é o turno deste jogador
                if jogo.current_player != player_num:
                    conn.sendall("[ERRO] Não é o seu turno!\n".encode('utf-8'))
                    continue

                sucesso = False
                msg = ""

                # Tenta processar o comando baseado na fase atual do jogo
                try:
                    valores = list(map(int, dados.split()))
                    
                    if jogo.game_phase == "DROP":
                        sucesso, msg = jogo.play_drop(valores[0], valores[1])
                    elif jogo.waiting_for_capture:
                        sucesso, msg = jogo.play_capture(valores[0], valores[1])
                    elif jogo.game_phase == "MOVE":
                        sucesso, msg = jogo.play_move(valores[0], valores[1], valores[2], valores[3])
                except:
                    conn.sendall("[ERRO] Formato inválido. Digite os números separados por espaço.\n".encode('utf-8'))
                    continue

                # Se a jogada deu certo, atualiza todos. Se deu erro, avisa só o jogador atual.
                if sucesso:
                    estado_atual = formatar_tabuleiro()
                    enviar_para_todos(f"\n--- Jogador {player_num} realizou uma ação ---\n{msg}\n{estado_atual}")
                    enviar_para_todos(f"Sua vez, Jogador {jogo.current_player}! Digite sua jogada:")
                else:
                    conn.sendall(f"[ERRO] {msg}\n".encode('utf-8'))

        except Exception as e:
            print(f"Erro com Jogador {player_num}: {e}")
            break

    print(f"Jogador {player_num} desconectou.")
    enviar_para_todos(f"O Jogador {player_num} desconectou. O jogo terminou.")
    conn.close()

def iniciar_servidor():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)
    
    print("=== SERVIDOR DARA INICIADO ===")
    
    # Conecta Jogador 1
    conn1, addr1 = server_socket.accept()
    clientes[1] = conn1
    print("Jogador 1 conectado.")
    conn1.sendall("Bem-vindo! Você é o Jogador 1 (X). Aguardando oponente...".encode('utf-8'))

    # Conecta Jogador 2
    conn2, addr2 = server_socket.accept()
    clientes[2] = conn2
    print("Jogador 2 conectado.")
    
    # Inicia o jogo
    estado_inicial = formatar_tabuleiro()
    enviar_para_todos("\n=== O JOGO COMEÇOU! ===\n" + estado_inicial)
    enviar_para_todos(f"Sua vez, Jogador {jogo.current_player}! Digite sua jogada:")

    # Inicia uma thread para cada cliente
    threading.Thread(target=lidar_com_cliente, args=(conn1, 1), daemon=True).start()
    threading.Thread(target=lidar_com_cliente, args=(conn2, 2), daemon=True).start()

    # Mantém o servidor rodando
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Desligando o servidor...")
        server_socket.close()

if __name__ == "__main__":
    iniciar_servidor()