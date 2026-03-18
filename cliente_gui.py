import tkinter as tk
import socket
import threading
import json

PORT = 65432 # A porta mantém-se a mesma

class DaraClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dara - Jogo em Rede")
        self.root.geometry("600x650")

        # Variáveis de estado local
        self.fase_atual = "DROP"
        self.esperando_captura = False
        self.peca_selecionada = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # ==========================================
        # ECRÃ 1: MENU DE LIGAÇÃO
        # ==========================================
        self.frame_conexao = tk.Frame(root)
        self.frame_conexao.pack(expand=True, fill="both") # Mostra este ecrã primeiro

        lbl_boas_vindas = tk.Label(self.frame_conexao, text="Bem-vindo ao Dara", font=("Helvetica", 24, "bold"))
        lbl_boas_vindas.pack(pady=(150, 20))

        lbl_ip = tk.Label(self.frame_conexao, text="Introduza o IP do Servidor:", font=("Helvetica", 14))
        lbl_ip.pack(pady=5)

        # Caixa de texto para o utilizador escrever o IP
        self.entry_ip = tk.Entry(self.frame_conexao, font=("Helvetica", 14), justify="center")
        self.entry_ip.insert(0, "127.0.0.1") # Preenche com localhost por defeito
        self.entry_ip.pack(pady=10)

        btn_ligar = tk.Button(self.frame_conexao, text="Ligar ao Jogo", font=("Helvetica", 14, "bold"), bg="lightgreen", command=self.tentar_ligacao)
        btn_ligar.pack(pady=20)

        self.lbl_erro_conexao = tk.Label(self.frame_conexao, text="", font=("Helvetica", 12), fg="red")
        self.lbl_erro_conexao.pack(pady=5)

        # ==========================================
        # ECRÃ 2: O JOGO (Escondido inicialmente)
        # ==========================================
        self.frame_jogo = tk.Frame(root)
        # Note que NÃO usamos o .pack() aqui ainda!

        self.lbl_titulo = tk.Label(self.frame_jogo, text="Dara - Multijogador", font=("Helvetica", 20, "bold"))
        self.lbl_titulo.pack(pady=10)

        self.lbl_info = tk.Label(self.frame_jogo, text="Aguardando oponente...", font=("Helvetica", 16), fg="blue")
        self.lbl_info.pack(pady=5)

        self.lbl_status = tk.Label(self.frame_jogo, text="", font=("Helvetica", 12))
        self.lbl_status.pack(pady=5)

        self.frame_tabuleiro = tk.Frame(self.frame_jogo, bg="black")
        self.frame_tabuleiro.pack(pady=20)

        self.botoes = [[None for _ in range(6)] for _ in range(5)]
        self.criar_tabuleiro()

    def criar_tabuleiro(self):
        """Cria a grelha visual 5x6"""
        for r in range(5):
            for c in range(6):
                btn = tk.Button(
                    self.frame_tabuleiro, text="", width=4, height=2,
                    font=("Helvetica", 24, "bold"), bg="white",
                    command=lambda row=r, col=c: self.ao_clicar(row, col)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.botoes[r][c] = btn

    # --- LÓGICA DE REDE E TRANSIÇÃO DE ECRÃS ---

    def tentar_ligacao(self):
        """Lê o IP digitado e tenta ligar ao servidor."""
        ip_digitado = self.entry_ip.get().strip()
        self.lbl_erro_conexao.config(text="A ligar...")
        self.root.update() # Força o Tkinter a atualizar o texto imediatamente

        try:
            self.sock.connect((ip_digitado, PORT))
            
            # Se a ligação for bem-sucedida:
            # 1. Esconde o ecrã de ligação
            self.frame_conexao.pack_forget()
            
            # 2. Mostra o ecrã do jogo
            self.frame_jogo.pack(expand=True, fill="both")
            
            # 3. Inicia a Thread para ouvir o servidor
            threading.Thread(target=self.receber_mensagens, daemon=True).start()
            
        except Exception as e:
            # Se falhar (IP errado ou servidor desligado)
            self.lbl_erro_conexao.config(text="Erro: Servidor não encontrado neste IP.")
            # Reiniciamos o socket para permitir uma nova tentativa
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receber_mensagens(self):
        buffer = ""
        while True:
            try:
                dados = self.sock.recv(4096).decode('utf-8')
                if not dados: break
                
                buffer += dados
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    if linha.strip():
                        estado_jogo = json.loads(linha)
                        self.root.after(0, self.atualizar_interface, estado_jogo)
            except:
                break

    def atualizar_interface(self, estado):
        self.fase_atual = estado.get("game_phase", "DROP")
        self.esperando_captura = estado.get("waiting_for_capture", False)
        self.peca_selecionada = None

        jogador_atual = estado.get("current_player", 1)
        msg_servidor = estado.get("mensagem", "")
        cor_turno = "blue" if jogador_atual == 1 else "red"
        
        texto_info = f"Turno do Jogador {jogador_atual} "
        if self.fase_atual == "DROP": texto_info += "(Fase de Colocação)"
        elif self.esperando_captura:
            texto_info += "!!! MODO CAPTURA !!!"
            cor_turno = "orange"
        else: texto_info += "(Fase de Movimento)"

        self.lbl_info.config(text=texto_info, fg=cor_turno)
        self.lbl_status.config(text=msg_servidor)

        tabuleiro = estado.get("board", [])
        if tabuleiro:
            for r in range(5):
                for c in range(6):
                    valor = tabuleiro[r][c]
                    btn = self.botoes[r][c]
                    if valor == 0: btn.config(text="", bg="white")
                    elif valor == 1: btn.config(text="X", bg="lightblue", fg="blue")
                    elif valor == 2: btn.config(text="O", bg="lightcoral", fg="red")

    def ao_clicar(self, r, c):
        if self.fase_atual == "DROP" or self.esperando_captura:
            self.sock.sendall(f"{r} {c}".encode('utf-8'))
        elif self.fase_atual == "MOVE":
            if self.peca_selecionada is None:
                self.peca_selecionada = (r, c)
                self.botoes[r][c].config(bg="yellow")
                self.lbl_status.config(text=f"Peça em ({r},{c}) selecionada. Escolha o destino.")
            else:
                r_origem, c_origem = self.peca_selecionada
                self.sock.sendall(f"{r_origem} {c_origem} {r} {c}".encode('utf-8'))
                self.peca_selecionada = None 

if __name__ == "__main__":
    janela = tk.Tk()
    app = DaraClientGUI(janela)
    janela.mainloop()