import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

def vetorizar_sorteio(row, total_numeros=25):
    """
    Converte um sorteio em um vetor binário de tamanho total_numeros.
    Cada posição do vetor é 1 se o número correspondente foi sorteado e 0 caso contrário.
    
    Parâmetros:
      row           : Lista/array com os números sorteados (por exemplo, de Bola1 a Bola15).
      total_numeros : Número total de possibilidades (para Lotofácil é 25).

    Retorna:
      vetor_binario : Lista de inteiros (0 ou 1) de tamanho total_numeros.
    """
    vetor = [0] * total_numeros
    for num in row:
        if isinstance(num, (int, float)) and 1 <= num <= total_numeros:
            vetor[int(num) - 1] = 1
    return vetor

def clusterizar_sorteios(df, num_clusters=5):
    """
    Converte cada sorteio em um vetor binário e aplica K-Means para identificar clusters.
    
    Parâmetros:
      df           : DataFrame contendo os sorteios. Espera-se que contenha colunas "Bola1" a "Bola15".
      num_clusters : Número de clusters desejado.

    Retorna:
      labels  : Rótulos do cluster para cada sorteio.
      centers : Centros dos clusters no espaço binário.
    """
    # Seleciona as colunas de sorteio
    colunas = [f"Bola{i}" for i in range(1, 16)]
    
    # Converte cada sorteio em vetor binário usando a função auxiliar
    vetorizados = df[colunas].apply(lambda row: vetorizar_sorteio(row.tolist()), axis=1)
    X = np.array(vetorizados.tolist())
    
    # Aplica o K-Means
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    
    return kmeans.labels_, kmeans.cluster_centers_

if __name__ == "__main__":
    # Teste do módulo individualmente.
    # Certifique-se de que o arquivo de dados 'Lotofacil.xlsx' está no caminho correto.
    from dados import carregar_dados
    
    df = carregar_dados("data/Lotofacil.xlsx")
    if df is not None:
        labels, centers = clusterizar_sorteios(df, num_clusters=5)
        print("Rótulos dos clusters:", labels)
        print("Centros dos clusters:")
        print(centers)
    else:
        print("Erro ao carregar os dados.")