import socket
import threading
import json
from dara import DaraGame

HOST = '0.0.0.0' # Pode voltar para localhost para testar a interface
PORT = 65432

jogo = DaraGame()
clientes = {}
lock = threading.Lock()

# Modifique a assinatura e o dicionário da função
def gerar_estado_json(mensagem="", chat_msg=""):
    estado = {
        "board": jogo.board,
        "current_player": jogo.current_player,
        "game_phase": jogo.game_phase,
        "waiting_for_capture": jogo.waiting_for_capture,
        "pieces_p1": jogo.pieces_to_drop[1],
        "pieces_p2": jogo.pieces_to_drop[2],
        "mensagem": mensagem,
        "chat_msg": chat_msg  
    }
    return json.dumps(estado)

def enviar_para_todos(dados_json):
    for conn in clientes.values():
        try:
            # Adicionamos um delimitador \n no final para o cliente saber onde a mensagem acaba
            conn.sendall((dados_json + "\n").encode('utf-8'))
        except:
            pass

def lidar_com_cliente(conn, player_num):
    while True:
        try:
            dados = conn.recv(1024).decode('utf-8').strip()
            if not dados: break

            # --- NOVA LÓGICA DE CHAT ---
            if dados.startswith("CHAT "):
                # Pega em tudo o que vem depois da palavra "CHAT "
                texto_chat = dados[5:] 
                estado_chat = gerar_estado_json(chat_msg=f"Jogador {player_num}: {texto_chat}")
                enviar_para_todos(estado_chat)
                continue # Volta para o início do loop (ignora a lógica de jogada abaixo)
            # ---------------------------
            
            # ==========================================
            # NOVO: VERIFICAÇÃO DE DESISTÊNCIA
            # ==========================================
            if dados == "RESIGN":
                # Descobre quem é o adversário (se o 1 desistiu, o 2 ganha)
                vencedor = 2 if player_num == 1 else 1
                mensagem_fim = f"O Jogador {player_num} desistiu! O Jogador {vencedor} VENCEU!"
                
                with lock:
                    # Gera o JSON com a mensagem de vitória e envia para todos
                    estado_final = gerar_estado_json(mensagem=mensagem_fim)
                    enviar_para_todos(estado_final)
                continue # Volta para o início do loop
            # ==========================================
            
            with lock:
                if jogo.current_player != player_num:
                    msg_erro = gerar_estado_json(f"Erro: Não é o seu turno, Jogador {player_num}!")
                    conn.sendall((msg_erro + "\n").encode('utf-8'))
                    continue

                sucesso = False
                msg = ""

                try:
                    valores = list(map(int, dados.split()))
                    if jogo.game_phase == "DROP":
                        sucesso, msg = jogo.play_drop(valores[0], valores[1])
                    elif jogo.waiting_for_capture:
                        sucesso, msg = jogo.play_capture(valores[0], valores[1])
                    elif jogo.game_phase == "MOVE":
                        sucesso, msg = jogo.play_move(valores[0], valores[1], valores[2], valores[3])
                except:
                    msg_erro = gerar_estado_json("Erro: Formato de comando inválido.")
                    conn.sendall((msg_erro + "\n").encode('utf-8'))
                    continue

                if sucesso:
                    # Se a jogada deu certo, envia o novo tabuleiro para os dois
                    estado_atual = gerar_estado_json(f"Jogador {player_num} jogou: {msg}")
                    enviar_para_todos(estado_atual)
                else:
                    # Se deu erro, avisa só quem tentou jogar errado
                    msg_erro = gerar_estado_json(f"Jogada inválida: {msg}")
                    conn.sendall((msg_erro + "\n").encode('utf-8'))

        except Exception as e:
            print(f"Erro com Jogador {player_num}: {e}")
            break

    print(f"Jogador {player_num} desconectou.")
    conn.close()

def iniciar_servidor():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(2)
    print("=== SERVIDOR DARA INICIADO (Modo JSON) ===")
    
    conn1, addr1 = server_socket.accept()
    clientes[1] = conn1
    print("Jogador 1 conectado.")
    # Envia o estado inicial apenas para o J1 enquanto espera
    conn1.sendall((gerar_estado_json("Bem-vindo Jogador 1. Aguardando oponente...") + "\n").encode('utf-8'))

    conn2, addr2 = server_socket.accept()
    clientes[2] = conn2
    print("Jogador 2 conectado.")
    
    # O jogo começa!
    estado_inicial = gerar_estado_json("O jogo começou! Turno do Jogador 1.")
    enviar_para_todos(estado_inicial)

    threading.Thread(target=lidar_com_cliente, args=(conn1, 1), daemon=True).start()
    threading.Thread(target=lidar_com_cliente, args=(conn2, 2), daemon=True).start()

    try:
        while True: pass
    except KeyboardInterrupt:
        server_socket.close()

if __name__ == "__main__":
    iniciar_servidor()