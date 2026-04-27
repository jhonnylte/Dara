from xmlrpc.server import SimpleXMLRPCServer
from dara import DaraGame

class DaraServidorRMI:
    def __init__(self):
        self.jogo = DaraGame()
        self.jogadores_conectados = 0

    # 1. Função para os clientes se registarem
    def entrar_no_jogo(self):
        if self.jogadores_conectados < 2:
            self.jogadores_conectados += 1
            return self.jogadores_conectados # Retorna ID 1 ou 2
        return 0 # Sala cheia

    # 2. Funções de jogada (Chamadas DIRETAMENTE pelo cliente!)
    def play_drop(self, r, c):
        return self.jogo.play_drop(r, c)

    def play_move(self, r1, c1, r2, c2):
        return self.jogo.play_move(r1, c1, r2, c2)

    def play_capture(self, r, c):
        return self.jogo.play_capture(r, c)

    # 3. Função para o cliente "perguntar" como está o jogo
    def obter_estado(self):
        return {
            "board": self.jogo.board,
            "current_player": self.jogo.current_player,
            "game_phase": self.jogo.game_phase,
            "waiting_for_capture": self.jogo.waiting_for_capture
        }

# --- Inicialização da Magia do RMI ---
print("=== Servidor Dara RMI (XML-RPC) Iniciado ===")
# Cria o Skeleton na porta 65432
server = SimpleXMLRPCServer(("0.0.0.0", 65432), allow_none=True)

# Expõe a nossa classe para a internet!
server.register_instance(DaraServidorRMI())

# Fica à espera de chamadas de métodos
server.serve_forever()