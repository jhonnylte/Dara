from xmlrpc.server import SimpleXMLRPCServer
from dara import DaraGame

class DaraServidorRMI:
    def __init__(self):
        self.jogo = DaraGame()
        self.jogadores_conectados = 0
        self.mensagem_sistema = ""
        self.historico_chat = ""

    def enviar_chat(self, player_id, mensagem):
        """O cliente chama esta função para adicionar uma linha ao histórico."""
        self.historico_chat += f"Jogador {player_id}: {mensagem}\n"
        return True
        
    def entrar_no_jogo(self):
        if self.jogadores_conectados < 2:
            self.jogadores_conectados += 1
            return self.jogadores_conectados # Retorna ID 1 ou 2
        return 0 # Sala cheia

    def play_drop(self, player_id, r, c):
        if player_id != self.jogo.current_player:
            return False, "Aguarde, não é o seu turno!"
        return self.jogo.play_drop(r, c)

    def play_move(self, player_id, r1, c1, r2, c2):
        if player_id != self.jogo.current_player:
            return False, "Aguarde, não é o seu turno!"
        return self.jogo.play_move(r1, c1, r2, c2)

    def play_capture(self, player_id, r, c):
        if player_id != self.jogo.current_player:
            return False, "Aguarde, não é o seu turno!"
        return self.jogo.play_capture(r, c)
    
    def desistir(self, player_id):
        vencedor = 2 if player_id == 1 else 1
        self.mensagem_sistema = f"O Jogador {player_id} desistiu! O Jogador {vencedor} VENCEU!"
        return True

    def obter_estado(self):
        return {
            "board": self.jogo.board,
            "current_player": self.jogo.current_player,
            "game_phase": self.jogo.game_phase,
            "waiting_for_capture": self.jogo.waiting_for_capture,
            "chat_completo": self.historico_chat,
            "mensagem": self.mensagem_sistema
        }
    
    
print("=== Servidor Dara RMI (XML-RPC) Iniciado ===")

server = SimpleXMLRPCServer(("0.0.0.0", 65432), allow_none=True)

# Expõe a classe para a internet
server.register_instance(DaraServidorRMI())

# Fica à espera de chamadas de métodos
server.serve_forever()