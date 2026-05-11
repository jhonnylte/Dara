#from xmlrpc.server import SimpleXMLRPCServer
#import json

# ==========================================================
# A SUA CLASSE ORIGINAL (Sem alterações na lógica interna)
# ==========================================================
class DaraGame:
    def __init__(self):
        self.board = [[0 for _ in range(6)] for _ in range(5)]
        self.current_player = 1
        self.game_phase = "DROP"
        self.pieces_to_drop = {1: 12, 2: 12}
        self.pieces_on_board = {1: 0, 2: 0}
        self.waiting_for_capture = False

    def check_three_in_a_row(self, player):
        for r in range(5):
            count = 0
            for c in range(6):
                if self.board[r][c] == player:
                    count += 1
                    if count >= 3: return True
                else: count = 0
        for c in range(6):
            count = 0
            for r in range(5):
                if self.board[r][c] == player:
                    count += 1
                    if count >= 3: return True
                else: count = 0
        return False

    def is_valid_drop(self, r, c, player):
        if r < 0 or r > 4 or c < 0 or c > 5 or self.board[r][c] != 0:
            return False
        self.board[r][c] = player
        forms_three = self.check_three_in_a_row(player)
        self.board[r][c] = 0
        return not forms_three

    def play_drop(self, r, c):
        if self.game_phase != "DROP":
            return False, "O jogo não está na fase de colocação."
        player = self.current_player
        if self.is_valid_drop(r, c, player):
            self.board[r][c] = player
            self.pieces_to_drop[player] -= 1
            self.pieces_on_board[player] += 1
            if self.pieces_to_drop[1] == 0 and self.pieces_to_drop[2] == 0:
                self.game_phase = "MOVE"
            self.current_player = 2 if player == 1 else 1
            return True, "Jogada realizada com sucesso."
        else:
            return False, "Jogada inválida! Casa ocupada ou forma uma trinca."

    def check_trinca_at(self, r, c, player):
        count = 0
        for col in range(6):
            if self.board[r][col] == player:
                count += 1
                if count >= 3: return True
            else: count = 0
        count = 0
        for row in range(5):
            if self.board[row][c] == player:
                count += 1
                if count >= 3: return True
            else: count = 0
        return False

    def play_move(self, r_from, c_from, r_to, c_to):
        if self.game_phase != "MOVE" or self.waiting_for_capture:
            return False, "Não é possível mover agora."
        player = self.current_player
        if self.board[r_from][c_from] != player:
            return False, "Você deve escolher uma peça sua para mover."
        if self.board[r_to][c_to] != 0:
            return False, "A casa de destino não está vazia."
        distancia = abs(r_to - r_from) + abs(c_to - c_from)
        if distancia != 1:
            return False, "Movimento deve ser adjacente."
        self.board[r_from][c_from] = 0
        self.board[r_to][c_to] = player
        if self.check_trinca_at(r_to, c_to, player):
            self.waiting_for_capture = True
            return True, "Trinca formada! Capture uma peça."
        else:
            self.current_player = 2 if player == 1 else 1
            return True, "Movimento realizado."

    def play_capture(self, r, c):
        if not self.waiting_for_capture:
            return False, "Não há trinca para capturar."
        player = self.current_player
        opponent = 2 if player == 1 else 1
        if self.board[r][c] != opponent:
            return False, "Escolha uma peça do oponente."
        self.board[r][c] = 0
        self.pieces_on_board[opponent] -= 1
        self.waiting_for_capture = False
        if self.pieces_on_board[opponent] <= 2:
            self.game_phase = "END"
            return True, f"FIM DE JOGO! Jogador {player} venceu!"
        self.current_player = opponent
        return True, "Peça capturada!"

