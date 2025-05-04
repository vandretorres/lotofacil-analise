import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

def backtest_randomforest(df, num_sorteios=100, meta_acertos=11, n_estimators=200, max_depth=10):
    """Executa backtest usando RandomForest para prever números da Lotofácil."""
    
    # Ordenar pelo número do concurso
    df = df.sort_values(by="Concurso", ascending=True)
    
    # Definir as colunas dos números sorteados
    colunas_numeros = [f"Bola{i}" for i in range(1, 16)]
    
    acertos_por_sorteio = []

    for i in range(len(df) - num_sorteios, len(df)):  # Últimos `num_sorteios` concursos
        df_treino = df.iloc[:i]  # Usa apenas sorteios anteriores
        df_teste = df.iloc[i]  # Usa o sorteio atual como teste
        
        if len(df_treino) < 50:  # Garante dados mínimos para treinar RandomForest
            continue
        
        # Criar matriz de frequência dos números sorteados como entrada para o modelo
        X = df_treino[colunas_numeros].melt()["value"].value_counts().reindex(range(1, 26), fill_value=0).values.reshape(1, -1)
        y = df_treino[colunas_numeros].values  # Saída: números sorteados diretamente
        
        # Treinar o modelo RandomForest com ajustes para melhorar a predição
        rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        rf.fit(X, y)
        
        # Predição para o concurso atual
        X_teste = df_teste[colunas_numeros].melt()["value"].value_counts().reindex(range(1, 26), fill_value=0).values.reshape(1, -1)
        previsao_prob = np.array(rf.predict_proba(X_teste))[0][:25]  # Apenas números de 1 a 25
        
        # Selecionar os 15 números mais prováveis
        numeros_preditos = set((np.argsort(previsao_prob)[-15:] + 1).astype(int))

        # Números sorteados no concurso real
        numeros_reais = set(df_teste[colunas_numeros].values)

        # Calcular acertos
        acertos = len(numeros_preditos.intersection(numeros_reais))
        acertos_por_sorteio.append(acertos)

        print(f"🎯 Sorteio {df_teste['Concurso']}: {acertos} acertos")
    
    # Estatísticas gerais
    acertos_medio = sum(acertos_por_sorteio) / len(acertos_por_sorteio)
    acertos_acima_meta = sum(a >= meta_acertos for a in acertos_por_sorteio)

    print("\n📊 **Resultados do Backtest (RandomForest)**")
    print(f"- Média de acertos por sorteio: {acertos_medio:.2f}")
    print(f"- Sorteios com >= {meta_acertos} acertos: {acertos_acima_meta}/{num_sorteios}")

    return acertos_por_sorteio

# Carregar dados do histórico de sorteios
df = pd.read_excel("data/Lotofacil.xlsx", engine="openpyxl")

# Rodar o backtest
backtest_randomforest(df)