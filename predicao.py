from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import pandas as pd

def treinar_modelo(df):
    """ Treina um modelo simples de Machine Learning para prever padrões """
    X = df.shift(1).dropna()  # Usa sorteios anteriores como entrada
    y = df.iloc[X.index]  # Garante que y tenha a mesma dimensão de X
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = RandomForestClassifier()
    modelo.fit(X_train, y_train)

    return modelo

def simulacao_monte_carlo(modelo, n_simulacoes=1000):
    """ Simula combinações possíveis para estimar probabilidades """
    resultados = [tuple(sorted(np.random.choice(range(1, 26), 15, replace=False))) for _ in range(n_simulacoes)]
    frequencias = pd.Series(resultados).value_counts()
    
    return frequencias.head(10)  # Mostra as 10 combinações mais prováveis