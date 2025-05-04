import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split

def backtest_mlp(df, num_sorteios=100, meta_acertos=11):
    """Executa backtest usando MLP para prever números da Lotofácil."""
    
    # Ordena pelo número do concurso
    df = df.sort_values(by="Concurso", ascending=True)
    
    # Definir as colunas dos números sorteados
    colunas_numeros = [f"Bola{i}" for i in range(1, 16)]
    
    acertos_por_sorteio = []
    
    for i in range(len(df) - num_sorteios, len(df)):  # Últimos `num_sorteios` concursos
        df_treino = df.iloc[:i]  # Usa apenas sorteios anteriores
        df_teste = df.iloc[i]  # Usa o sorteio atual como teste
        
        if len(df_treino) < 50:  # Garante dados mínimos para treinar MLP
            continue
        
        # Converter números sorteados para formato binário
        mlb = MultiLabelBinarizer(classes=np.arange(1, 26))
        X = df_treino["Concurso"].values.reshape(-1, 1)
        y = mlb.fit_transform(df_treino[colunas_numeros].values)
        
        # Treinar o modelo MLP
        mlp = MLPClassifier(hidden_layer_sizes=(50, 30), max_iter=500, random_state=42)
        mlp.fit(X, y)
        
        # Predição para o concurso atual
        X_teste = np.array([[df_teste["Concurso"]]])
        previsao_prob = mlp.predict_proba(X_teste)[0]
        
        # Selecionar os 15 números mais prováveis
        numeros_preditos = set(np.argsort(previsao_prob)[-15:] + 1)
        
        # Números sorteados no concurso real
        numeros_reais = set(df_teste[colunas_numeros].values)
        
        # Calcular acertos
        acertos = len(numeros_preditos.intersection(numeros_reais))
        acertos_por_sorteio.append(acertos)

        print(f"🎯 Sorteio {df_teste['Concurso']}: {acertos} acertos")
    
    # Estatísticas gerais
    acertos_medio = sum(acertos_por_sorteio) / len(acertos_por_sorteio)
    acertos_acima_meta = sum(a >= meta_acertos for a in acertos_por_sorteio)

    print("\n📊 **Resultados do Backtest (MLP)**")
    print(f"- Média de acertos por sorteio: {acertos_medio:.2f}")
    print(f"- Sorteios com >= {meta_acertos} acertos: {acertos_acima_meta}/{num_sorteios}")

    return acertos_por_sorteio

# Carregar dados do histórico de sorteios
df = pd.read_excel("data/Lotofacil.xlsx", engine="openpyxl")

# Rodar o backtest
backtest_mlp(df)