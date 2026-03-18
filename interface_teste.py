import tkinter as tk

class DaraGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dara - Interface Gráfica")
        self.root.geometry("500x650") # Largura x Altura
        
        # --- Título ---
        titulo = tk.Label(self.root, text="Jogo Dara", font=("Arial", 24, "bold"))
        titulo.pack(pady=10)
        
        # --- Painel de Informações ---
        self.info_label = tk.Label(self.root, text="Aguardando conexão...", font=("Arial", 14), fg="blue")
        self.info_label.pack(pady=5)

        # --- Frame do Tabuleiro ---
        # Um Frame é como uma "caixa" onde vamos agrupar os botões
        self.board_frame = tk.Frame(self.root, bg="black") 
        self.board_frame.pack(pady=20)
        
        # Matriz para guardar os botões, assim como guardamos os números no servidor
        self.botoes = [[None for _ in range(6)] for _ in range(5)]
        
        self.criar_tabuleiro()

    def criar_tabuleiro(self):
        """Cria uma grade 5x6 de botões."""
        for r in range(5):
            for c in range(6):
                # O comando lambda é crucial aqui para o botão "lembrar" a sua própria posição
                btn = tk.Button(
                    self.board_frame, 
                    text="", 
                    width=4, height=2, 
                    font=("Arial", 20, "bold"), 
                    bg="white",
                    command=lambda row=r, col=c: self.ao_clicar(row, col)
                )
                # Posiciona o botão na grade
                btn.grid(row=r, column=c, padx=2, pady=2)
                
                # Salva o botão na nossa matriz
                self.botoes[r][c] = btn

    def ao_clicar(self, r, c):
        """Função disparada quando qualquer botão é clicado."""
        self.info_label.config(text=f"Você clicou na Linha {r}, Coluna {c}!")
        
        # Apenas para testarmos o visual, vamos mudar a cor e o texto do botão clicado
        botao_atual = self.botoes[r][c]
        if botao_atual["text"] == "":
            botao_atual.config(text="X", bg="lightblue")
        else:
            botao_atual.config(text="", bg="white")

# --- LOOP PRINCIPAL DO TKINTER ---
if __name__ == "__main__":
    janela = tk.Tk()
    app = DaraGUI(janela)
    janela.mainloop() # Mantém a janela aberta ouvindo os cliques do mouse