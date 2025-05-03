import random
import pandas as pd

def gerar_jogos(df, modelo, mlb, quantidade=5):
    """
    Gera uma quantidade de jogos (combinações aleatórias) para a Lotofácil.
    
    Como a função simulacao_monte_carlo não será utilizada, 
    optamos por gerar combinações aleatórias de 15 números (de 1 a 25).

    Parâmetros:
      - df: DataFrame com os dados históricos (não utilizado neste exemplo).
      - modelo, mlb: Parâmetros mantidos para compatibilidade, mas não são utilizados.
      - quantidade: Número de jogos a serem gerados.

    Retorna:
      Um DataFrame cuja _index_ contém as combinações geradas.
      Assim, a interface que usa "gerar_jogos(...).index" continua funcionando.
    """
    jogos = []
    for _ in range(quantidade):
        # Gera uma combinação aleatória de 15 números dentre 1 a 25, sem repetição
        jogo = sorted(random.sample(range(1, 26), 15))
        jogos.append(tuple(jogo))
    # Cria um DataFrame vazio e atribui o índice como sendo as combinações geradas
    return pd.DataFrame(index=jogos)

# Teste simples (opcional)
if __name__ == "__main__":
    # Para testar o gerador de jogos sem depender de outros módulos:
    dummy_df = pd.DataFrame()  # Não utilizado realmente
    jogos_gerados = gerar_jogos(dummy_df, None, None, quantidade=5)
    print("Jogos gerados:")
    for jogo in jogos_gerados.index:
        print(list(jogo))