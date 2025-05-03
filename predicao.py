from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
import pandas as pd

def treinar_modelo(df, modelo_escolhido="RandomForest"):
    """
    Treina um modelo baseado na escolha do usuário, utilizando apenas as colunas de bolas.
    Para isso, utiliza o resultado do sorteio anterior (X) para tentar prever os números do sorteio corrente (y).
    """
    # Definir as colunas referentes aos números sorteados
    colunas_bolas = [f"Bola{i}" for i in range(1, 16)]
    
    # Obtém as features: sorteio anterior (shift) e remove as linhas onde o shift resulte em NA
    X = df[colunas_bolas].shift(1).dropna()
    # Como alvo (target), utiliza o sorteio atual correspondente às mesmas colunas
    y = df.loc[X.index, colunas_bolas]
    
    # Debug: Verifica os tipos e valores da variável alvo
    print("DEBUG: Tipos dos valores de y:", y.dtypes.to_dict())
    print("DEBUG: Primeira linha de y:", y.iloc[0].tolist())
    
    # Binariza os números sorteados utilizando MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    # y.values.tolist() deve retornar uma lista de listas de inteiros
    y_list = y.values.tolist()
    y_bin = mlb.fit_transform(y_list)
    
    # Divisão em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_bin, test_size=0.2, random_state=42
    )
    
    # Seleciona o modelo conforme a escolha do usuário
    if modelo_escolhido == "RandomForest":
        modelo = RandomForestClassifier()
    elif modelo_escolhido == "MLP":
        modelo = MLPClassifier(hidden_layer_sizes=(50, 50), max_iter=500)
    else:
        raise ValueError("Modelo inválido! Escolha 'RandomForest' ou 'MLP'.")
    
    modelo.fit(X_train, y_train)
    return modelo, mlb

def simulacao_monte_carlo(modelo, mlb, df, n_simulacoes=1000):
    """
    Simula combinações possíveis para prever padrões de sorteio.
    Utiliza somente as colunas de bolas para manter a consistência dos dados.
    """
    colunas_bolas = [f"Bola{i}" for i in range(1, 16)]
    
    simulacoes = []
    for _ in range(n_simulacoes):
        # Seleciona aleatoriamente um sorteio como entrada para a predição
        entrada_simulada = df[colunas_bolas].sample(n=1).values
        entrada_simulada_df = pd.DataFrame(entrada_simulada, columns=colunas_bolas)
        
        predicao_binaria = modelo.predict(entrada_simulada_df)
        numeros_sorteados = mlb.inverse_transform(predicao_binaria)[0]
        
        # Se o conjunto de números resultante tiver 15 ou mais elementos, sorteia 15 sem reposição;
        # caso contrário, ordena e utiliza todos os números retornados.
        if len(numeros_sorteados) >= 15:
            numeros_sorteados = sorted(np.random.choice(numeros_sorteados, 15, replace=False))
        else:
            numeros_sorteados = sorted(numeros_sorteados)
        
        simulacoes.append(tuple(numeros_sorteados))
    
    frequencias = pd.Series(simulacoes).value_counts()
    return frequencias.head(10)