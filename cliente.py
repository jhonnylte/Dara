import tkinter as tk
from tkinter import messagebox
import threading
import xmlrpc.client 
import time

PORT = 65432 

class DaraClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dara - Jogo em Rede")
        self.root.geometry("600x850")

        # Variáveis de estado local
        self.fase_atual = "DROP"
        self.esperando_captura = False
        self.peca_selecionada = None
        self.jogo_terminou = False

        # ==========================================
        # TELA 1: MENU DE LIGAÇÃO
        # ==========================================
        self.frame_conexao = tk.Frame(root)
        self.frame_conexao.pack(expand=True, fill="both") # Mostra este tela primeiro

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
        # TELA 2: O JOGO (Escondido inicialmente)
        # ==========================================
        self.frame_jogo = tk.Frame(root)

        self.lbl_titulo = tk.Label(self.frame_jogo, text="Dara - Multijogador", font=("Helvetica", 20, "bold"))
        self.lbl_titulo.pack(pady=10)

        self.lbl_info = tk.Label(self.frame_jogo, text="Aguardando oponente...", font=("Helvetica", 16), fg="blue")
        self.lbl_info.pack(pady=5)

        self.lbl_status = tk.Label(self.frame_jogo, text="", font=("Helvetica", 12))
        self.lbl_status.pack(pady=5)

        # ==========================================
        # BOTÕES LADO A LADO (Chat e Desistir)
        # ==========================================
        self.ultimo_chat_visto = ""

        self.frame_botoes = tk.Frame(self.frame_jogo)
        self.frame_botoes.pack(pady=10)

        self.btn_abrir_chat = tk.Button(self.frame_botoes, text="💬 Mostrar Chat", font=("Helvetica", 14), command=self.alternar_chat)
        self.btn_abrir_chat.pack(side=tk.LEFT, padx=10)

        self.btn_desistir = tk.Button(self.frame_botoes, text="🏴 Desistir", font=("Helvetica", 14), command=self.desistir)
        self.btn_desistir.pack(side=tk.LEFT, padx=10)

        # O Tabuleiro
        self.frame_tabuleiro = tk.Frame(self.frame_jogo, bg="black")
        self.frame_tabuleiro.pack(pady=5)

        self.botoes = [[None for _ in range(6)] for _ in range(5)]
        self.criar_tabuleiro()

        # O Frame do chat fica por baixo do tabuleiro
        self.frame_chat = tk.Frame(self.frame_jogo)
        self.chat_visivel = False
        
        self.caixa_chat = tk.Text(self.frame_chat, height=5, width=40, state=tk.DISABLED, font=("Helvetica", 10))
        self.caixa_chat.pack(side=tk.TOP, pady=5)

        self.entrada_chat = tk.Entry(self.frame_chat, font=("Helvetica", 14), width=35)
        self.entrada_chat.pack(side=tk.BOTTOM, pady=5)
        self.entrada_chat.bind("<Return>", self.enviar_chat)

    def alternar_chat(self):
        """Abre ou fecha o painel do chat dentro da mesma janela."""
        if self.chat_visivel:
            self.frame_chat.pack_forget()
            self.btn_abrir_chat.config(text="💬 Mostrar Chat", bg="white")
            self.chat_visivel = False
        else:
            self.frame_chat.pack(pady=10, before=self.frame_tabuleiro)
            self.btn_abrir_chat.config(text="💬 Esconder Chat", bg="white")
            self.chat_visivel = True
            self.entrada_chat.focus()

    def criar_tabuleiro(self):
        # Cria a grelha visual 5x6
        for r in range(5):
            for c in range(6):
                btn = tk.Button(
                    self.frame_tabuleiro, text="", width=4, height=1,
                    font=("Helvetica", 16, "bold"), bg="white",
                    command=lambda row=r, col=c: self.ao_clicar(row, col)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.botoes[r][c] = btn

    # --- LÓGICA DE REDE E TRANSIÇÃO DE TELAS ---

    def tentar_ligacao(self):
        ip_digitado = self.entry_ip.get().strip()
        
        try:
            self.servidor = xmlrpc.client.ServerProxy(f"http://{ip_digitado}:{PORT}")
            meu_id = self.servidor.entrar_no_jogo()
            
            if meu_id > 0:
                self.definir_meu_id(meu_id)
                self.frame_conexao.pack_forget()
                self.frame_jogo.pack(expand=True, fill="both")
                
                threading.Thread(target=self.vigiar_servidor, daemon=True).start()
            else:
                self.lbl_erro_conexao.config(text="Erro: Sala cheia.")
                
        except Exception as e:
            self.lbl_erro_conexao.config(text="Erro de ligação.")
    
    def definir_meu_id(self, id_recebido):
        self.meu_id = id_recebido
        cor = "blue" if self.meu_id == 1 else "red"
        self.lbl_titulo.config(text=f"Jogador {self.meu_id}", fg=cor)

    def atualizar_interface(self, estado):
        self.fase_atual = estado.get("game_phase", "DROP")
        self.esperando_captura = estado.get("waiting_for_capture", False)

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

        # --- ATUALIZA O CHAT (Versão RMI) ---
        chat_atual = estado.get("chat_completo", "")
        
        if chat_atual != self.ultimo_chat_visto:
            self.caixa_chat.config(state=tk.NORMAL)
            self.caixa_chat.delete(1.0, tk.END) 
            self.caixa_chat.insert(tk.END, chat_atual) 
            self.caixa_chat.see(tk.END)
            self.caixa_chat.config(state=tk.DISABLED)
            
            if not self.chat_visivel:
                self.btn_abrir_chat.config(text="💬 Nova Mensagem!", bg="yellow")
                
            self.ultimo_chat_visto = chat_atual

        tabuleiro = estado.get("board", [])
        if tabuleiro:
            for r in range(5):
                for c in range(6):
                    valor = tabuleiro[r][c]
                    btn = self.botoes[r][c]
                    if self.peca_selecionada == (r, c):
                        btn.config(bg="yellow")
                    else:
                        if valor == 0: btn.config(text="", bg="white")
                        elif valor == 1: btn.config(text="X", bg="lightblue", fg="blue")
                        elif valor == 2: btn.config(text="O", bg="lightcoral", fg="red")
                    
        # ==========================================
        # VERIFICAÇÃO DE FIM DE JOGO
        # ==========================================
        mensagem_min = msg_servidor.lower()
        if not self.jogo_terminou and ("venceu" in mensagem_min or "ganhou" in mensagem_min):
            
            self.jogo_terminou = True 
            messagebox.showinfo("Fim de Partida!", msg_servidor)
            
            for r in range(5):
                for c in range(6):
                    self.botoes[r][c].config(state=tk.DISABLED)
            
            self.btn_abrir_chat.config(text="Sair do Jogo", bg="red", command=self.root.quit)

    def enviar_chat(self, event=None):
        """Envia a mensagem chamando a função RMI diretamente."""
        msg = self.entrada_chat.get().strip()
        if msg:
            self.servidor.enviar_chat(self.meu_id, msg)
            self.entrada_chat.delete(0, tk.END) 

    def desistir(self):
        """Pede confirmação e avisa o servidor RMI da desistência."""
        confirmacao = messagebox.askyesno("Desistir", "Tem a certeza que quer desistir da partida?")
        if confirmacao:
            try:
                self.servidor.desistir(self.meu_id)
            except Exception as e:
                print("Erro ao comunicar desistência.")

    def ao_clicar(self, r, c):
        # A nova verificação de modo captura (inserida aqui no topo para ganhar prioridade)
        if self.esperando_captura:
            sucesso, msg = self.servidor.play_capture(self.meu_id, r, c)
            if not sucesso:
                self.lbl_status.config(text=msg)

        elif self.fase_atual == "DROP":
            sucesso, msg = self.servidor.play_drop(self.meu_id, r, c)
            if not sucesso:
                self.lbl_status.config(text=msg) 

        elif self.fase_atual == "MOVE":
            if self.peca_selecionada is None:
                self.peca_selecionada = (r, c)
                self.botoes[r][c].config(bg="yellow")
            else:
                r_origem, c_origem = self.peca_selecionada
                sucesso, msg = self.servidor.play_move(self.meu_id, r_origem, c_origem, r, c)
                if not sucesso:
                    self.lbl_status.config(text=msg)
                self.peca_selecionada = None

    def vigiar_servidor(self):
        while True:
            try:
                estado_jogo = self.servidor.obter_estado()
                self.root.after(0, self.atualizar_interface, estado_jogo)
                time.sleep(0.5) 
            except:
                break

if __name__ == "__main__":
    janela = tk.Tk()
    app = DaraClientGUI(janela)
    janela.mainloop()