import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

def backtest_clustering(df, num_sorteios=100, meta_acertos=11, num_clusters=10):
    """Executa backtest baseado em agrupamento de números (Clustering) usando K-Means."""
    
    # Ordenar pelo número do concurso
    df = df.sort_values(by="Concurso", ascending=True)
    
    # Definir as colunas dos números sorteados
    colunas_numeros = [f"Bola{i}" for i in range(1, 16)]
    
    acertos_por_sorteio = []

    for i in range(len(df) - num_sorteios, len(df)):  # Últimos `num_sorteios` concursos
        df_treino = df.iloc[:i]  # Usa somente sorteios anteriores até `i`
        df_teste = df.iloc[i]  # Usa o sorteio atual como teste
        
        # Garantindo que temos dados suficientes para aplicar clustering
        if len(df_treino) < num_clusters:
            continue
        
        # Convertendo números sorteados para matriz numérica
        matriz_treino = df_treino[colunas_numeros].values
        
        # Aplicar K-Means para identificar padrões
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        kmeans.fit(matriz_treino)
        
        # Selecionar os números dos centroides mais comuns
        centroides = kmeans.cluster_centers_.astype(int)
        numeros_preditos = set(np.unique(centroides.flatten()))  # Pegamos os números agrupados
        
        # Reduzindo para apenas **15 números** preditos
        numeros_preditos = set(sorted(numeros_preditos)[:15])
        
        # Números reais do sorteio atual
        numeros_reais = set(df_teste[colunas_numeros].values)
        
        # Contar acertos
        acertos = len(numeros_preditos.intersection(numeros_reais))
        acertos_por_sorteio.append(acertos)

        print(f"🎯 Sorteio {df_teste['Concurso']}: {acertos} acertos")
    
    # Estatísticas gerais
    acertos_medio = sum(acertos_por_sorteio) / len(acertos_por_sorteio)
    acertos_acima_meta = sum(a >= meta_acertos for a in acertos_por_sorteio)

    print("\n📊 **Resultados do Backtest (Clustering)**")
    print(f"- Média de acertos por sorteio: {acertos_medio:.2f}")
    print(f"- Sorteios com >= {meta_acertos} acertos: {acertos_acima_meta}/{num_sorteios}")

    return acertos_por_sorteio

# Carregar dados do histórico de sorteios
df = pd.read_excel("data/Lotofacil.xlsx", engine="openpyxl")

# Rodar o backtest
backtest_clustering(df)