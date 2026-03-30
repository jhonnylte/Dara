class DaraGame:
    def __init__(self):
        self.board = [[0 for _ in range(6)] for _ in range(5)]
        self.current_player = 1
        self.game_phase = "DROP"
        self.pieces_to_drop = {1: 12, 2: 12}
        self.pieces_on_board = {1: 0, 2: 0}
        self.waiting_for_capture = False

    def check_three_in_a_row(self, player):
        """Verifica o tabuleiro inteiro à procura de 3 peças seguidas do mesmo jogador."""
        # Verificar linhas (horizontal)
        for r in range(5):
            count = 0
            for c in range(6):
                if self.board[r][c] == player:
                    count += 1
                    if count >= 3: return True
                else:
                    count = 0
                    
        # Verificar colunas (vertical)
        for c in range(6):
            count = 0
            for r in range(5):
                if self.board[r][c] == player:
                    count += 1
                    if count >= 3: return True
                else:
                    count = 0
                    
        return False

    def is_valid_drop(self, r, c, player):
        """Verifica se a posição está vazia e se a jogada quebra a regra da trinca."""
        # 1. Verifica limites do tabuleiro e se a casa está vazia
        if r < 0 or r > 4 or c < 0 or c > 5 or self.board[r][c] != 0:
            return False
            
        # 2. Simula a jogada
        self.board[r][c] = player
        forms_three = self.check_three_in_a_row(player)
        
        # 3. Desfaz a simulação
        self.board[r][c] = 0
        
        # A jogada é válida se NÃO formar três em linha
        return not forms_three

    def play_drop(self, r, c):
        """Executa a jogada de colocação se for válida."""
        if self.game_phase != "DROP":
            return False, "O jogo não está na fase de colocação."
            
        player = self.current_player
        
        if self.is_valid_drop(r, c, player):
            # Efetiva a jogada
            self.board[r][c] = player
            self.pieces_to_drop[player] -= 1
            self.pieces_on_board[player] += 1
            
            # Verifica se a fase de colocação acabou (ambos os jogadores colocaram 12 peças)
            if self.pieces_to_drop[1] == 0 and self.pieces_to_drop[2] == 0:
                self.game_phase = "MOVE"
            
            # Passa o turno para o outro jogador
            self.current_player = 2 if player == 1 else 1
            
            return True, "Jogada realizada com sucesso."
        else:
            return False, "Jogada inválida! Casa ocupada ou forma uma trinca."
    def check_trinca_at(self, r, c, player):
        """Verifica se há uma trinca na linha ou coluna da última peça movida."""
        # Verifica horizontal na linha r
        count = 0
        for col in range(6):
            if self.board[r][col] == player:
                count += 1
                if count >= 3: return True
            else: count = 0
            
        # Verifica vertical na coluna c
        count = 0
        for row in range(5):
            if self.board[row][c] == player:
                count += 1
                if count >= 3: return True
            else: count = 0
            
        return False

    def play_move(self, r_from, c_from, r_to, c_to):
        """Executa um movimento de uma casa para outra."""
        if self.game_phase != "MOVE" or self.waiting_for_capture:
            return False, "Não é possível mover agora."
            
        player = self.current_player
        
        # 1. Verifica se a peça de origem pertence ao jogador
        if self.board[r_from][c_from] != player:
            return False, "Você deve escolher uma peça sua para mover."
            
        # 2. Verifica se o destino está vazio
        if self.board[r_to][c_to] != 0:
            return False, "A casa de destino não está vazia."
            
        # 3. Verifica se o movimento é adjacente (não diagonal)
        distancia = abs(r_to - r_from) + abs(c_to - c_from)
        if distancia != 1:
            return False, "O movimento deve ser para uma casa adjacente (cima, baixo, lados)."
            
        # Move a peça
        self.board[r_from][c_from] = 0
        self.board[r_to][c_to] = player
        
        # Verifica se formou trinca
        if self.check_trinca_at(r_to, c_to, player):
            self.waiting_for_capture = True
            return True, "Trinca formada! Escolha uma peça do oponente para remover."
        
        # Se não formou trinca, passa a vez
        self.current_player = 2 if player == 1 else 1
        return True, "Movimento realizado."

    def play_capture(self, r, c):
        """Remove uma peça do oponente após formar uma trinca."""
        if not self.waiting_for_capture:
            return False, "Não há trinca formada para capturar."
            
        player = self.current_player
        opponent = 2 if player == 1 else 1
        
        # Verifica se a peça escolhida é do oponente
        if self.board[r][c] != opponent:
            return False, "Você deve escolher uma peça do oponente para remover."
            
        # Remove a peça
        self.board[r][c] = 0
        self.pieces_on_board[opponent] -= 1
        self.waiting_for_capture = False
        
        # Verifica condição de vitória (oponente ficou com 2 peças)
        if self.pieces_on_board[opponent] <= 2:
            self.game_phase = "END"
            return True, f"FIM DE JOGO! Jogador {player} venceu!"
            
        # Passa a vez
        self.current_player = opponent
        return True, "Peça capturada!"
        

def main():
    jogo = DaraGame()
    print("=== BEM-VINDO AO DARA ===")
