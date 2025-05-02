from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
import pandas as pd

def treinar_modelo(df, modelo_escolhido="RandomForest"):
    """ Treina um modelo baseado na escolha do usuário, garantindo compatibilidade dos dados. """
    
    X = df.shift(1).dropna()
    y = df.iloc[X.index]

    # Converte os números sorteados em formato binário
    mlb = MultiLabelBinarizer()
    y_bin = mlb.fit_transform(y.values.tolist())

    X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)

    if modelo_escolhido == "RandomForest":
        modelo = RandomForestClassifier()
    elif modelo_escolhido == "MLP":
        modelo = MLPClassifier(hidden_layer_sizes=(50, 50), max_iter=500)
    else:
        raise ValueError("Modelo inválido! Escolha 'RandomForest' ou 'MLP'.")

    modelo.fit(X_train, y_train)
    return modelo, mlb  # Retorna o modelo treinado e o binarizador

def simulacao_monte_carlo(modelo, mlb, df, n_simulacoes=1000):
    """ Simula combinações possíveis para prever padrões de sorteio """
    
    simulacoes = []
    for _ in range(n_simulacoes):
        entrada_simulada = df.sample(n=1).values  # Pegamos um sorteio existente para garantir formato
        
        # Ajusta formato para corresponder às features do treinamento
        entrada_simulada_df = pd.DataFrame(entrada_simulada, columns=df.columns)
        
        predicao_binaria = modelo.predict(entrada_simulada_df)
        numeros_sorteados = mlb.inverse_transform(predicao_binaria)[0]
        
        #numeros_sorteados = sorted(np.random.choice(numeros_sorteados, 15, replace=False))  # Seleciona 15 dezenas
        if len(numeros_sorteados) >= 15:
            numeros_sorteados = sorted(np.random.choice(numeros_sorteados, 15, replace=False))
        else:
            numeros_sorteados = sorted(numeros_sorteados)  # Retorna todos disponíveis se menos de 15
        
        simulacoes.append(tuple(sorted(numeros_sorteados)))

    frequencias = pd.Series(simulacoes).value_counts()
    return frequencias.head(10)  # Retorna as combinações mais frequentes