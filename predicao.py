import numpy as np
import pandas as pd
from collections import Counter

# -------------------------------
# Função para calcular hit-rate
# -------------------------------
def hit_rate(predito, real):
    """
    Calcula quantos números previstos aparecem entre os números sorteados.
    
    Args:
        predito (list): Lista com os números previstos.
        real (list): Lista com os números sorteados reais.
        
    Returns:
        int: Quantidade de acertos.
    """
    return len(set(predito) & set(real))

# ---------------------------------------------------------------
# Backtest com janela móvel (sliding window) com parâmetros flexíveis
# ---------------------------------------------------------------
def backtest_sliding_window(df, train_size, model_fn, predict_fn, *, step=1, n_numeros=15, **model_kwargs):
    """
    Executa um backtest temporal com janelas móveis.
    
    Treina o modelo com concursos de 1 até N e testa no concurso N+1, avançando a janela de treino de 'step' em 'step'.
    
    Args:
        df (pd.DataFrame): Base histórica de sorteios.
        train_size (int): Número de concursos usados para o treino inicial.
        model_fn (callable): Função que treina o modelo (ex.: train_binary_models).
        predict_fn (callable): Função que gera previsão (ex.: predict_binary).
        step (int): Passo do sliding window.
        n_numeros (int): Número de inteiros que se deseja prever.
        model_kwargs: Parâmetros adicionais para o model_fn.
        
    Returns:
        dict: Estatísticas do backtest, com média, desvio, mediana, histórico (Counter) e outros.
    """
    from tqdm import tqdm
    all_scores = []
    
    for end in tqdm(range(train_size, len(df) - 1, step), desc="Backtest folds"):
        treino = df.iloc[:end]
        teste  = df.iloc[end]
        modelo = model_fn(treino, **model_kwargs)   # Treina o modelo usando os dados até 'end'
        # Gera previsão usando o último concurso de 'treino' para prever o N+1
        previsao = predict_fn(modelo, treino, n_numeros)
        
        # Extrai os 15 números sorteados reais do concurso de teste
        colunas = [f"Bola{i}" for i in range(1, 16)]
        real = teste[colunas].tolist()
        score = hit_rate(previsao, real)
        all_scores.append(score)
    
    return {
        "mean":   np.mean(all_scores),
        "std":    np.std(all_scores),
        "median": np.median(all_scores),
        "hist":   Counter(all_scores),
        "folds":  len(all_scores),
        "scores": all_scores,
    }

# ------------------------------------------------------------------
# Treinamento de modelos binários: um classificador por número (1 a 25)
# ------------------------------------------------------------------
def train_binary_models(df, **kwargs):
    """
    Treina, para cada número de 1 a 25, um classificador binário que decide
    se o número aparecerá ou não no próximo concurso.
    
    Para criar as features, usamos a abordagem de usar o concurso anterior como
    entrada (one-hot vector de 25 posições) e o concurso corrente como rótulo (vetor binário de 25 posições).
    
    Args:
        df (pd.DataFrame): DataFrame contendo as colunas "Bola1" a "Bola15".
        kwargs: Parâmetros adicionais para o RandomForestClassifier (ex.: n_estimators, max_depth).
        
    Returns:
        dict: Dicionário mapeando cada número (de 1 a 25) para seu classificador treinado.
    """
    cols = [f"Bola{i}" for i in range(1, 16)]
    X_list = []
    Y_list = []
    n = len(df)
    # Utilizando concursos consecutivos: X = concurso anterior, Y = próximo concurso
    for i in range(1, n):
        previous_draw = df.iloc[i - 1][cols].values
        current_draw  = df.iloc[i][cols].values
        X_vec = [0] * 25
        Y_vec = [0] * 25
        for num in previous_draw:
            X_vec[int(num) - 1] = 1
        for num in current_draw:
            Y_vec[int(num) - 1] = 1
        X_list.append(X_vec)
        Y_list.append(Y_vec)
    
    X_array = np.array(X_list)
    Y_array = np.array(Y_list)
    
    from sklearn.ensemble import RandomForestClassifier
    models = {}
    for j in range(25):
        clf = RandomForestClassifier(n_jobs=-1, **kwargs)
        clf.fit(X_array, Y_array[:, j])
        models[j + 1] = clf  # número é 1-indexado
    return models

# ---------------------------------------------------------------
# Predição a partir dos modelos binários treinados
# ---------------------------------------------------------------
def predict_binary(models, treino, n_numeros):
    """
    Gera a previsão para o próximo concurso com base no último concurso de 'treino'.
    
    Converte o último concurso em um vetor one-hot (tamanho 25) e, para cada número de 1 a 25,
    obtém a probabilidade de ocorrência. Retorna os n_numeros com maiores probabilidades.
    
    Args:
        models (dict): Dicionário dos modelos treinados, mapeando números 1 a 25.
        treino (pd.DataFrame): DataFrame de treinamento (usado para extrair o último concurso).
        n_numeros (int): Número de inteiros (top n) a serem selecionados.
        
    Returns:
        list: Lista com os n_numeros previstos (ordenados em ordem crescente).
    """
    cols = [f"Bola{i}" for i in range(1, 16)]
    last_draw = treino.iloc[-1][cols].values
    X_vec = [0] * 25
    for num in last_draw:
        X_vec[int(num) - 1] = 1
    X_vec = np.array(X_vec).reshape(1, -1)
    
    probabilities = {}
    for num, clf in models.items():
        prob = clf.predict_proba(X_vec)[0][1]  # probabilidade de ocorrência (classe 1)
        probabilities[num] = prob
    # Seleciona os números com maior probabilidade
    selected = sorted(probabilities, key=lambda x: probabilities[x], reverse=True)[:n_numeros]
    return sorted(selected)

# ---------------------------------------------------------------
# Exemplo de execução com backtest e argumentos de linha de comando
# ---------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    from dados import carregar_dados  # Certifique-se de que o módulo 'dados' contenha a função carregar_dados
    
    parser = argparse.ArgumentParser(description="Backtest para predição da Lotofácil usando modelos binários")
    parser.add_argument("--train_size", type=int, default=100, help="Tamanho da janela de treino (número de concursos)")
    parser.add_argument("--step", type=int, default=1, help="Passo para o sliding window")
    parser.add_argument("--n_numeros", type=int, default=15, help="Quantidade de números a serem previstos")
    parser.add_argument("--data_path", type=str, default="data/Lotofacil.xlsx", help="Caminho do arquivo de dados")
    parser.add_argument("--n_estimators", type=int, default=100, help="Número de estimadores para o RandomForest")
    parser.add_argument("--max_depth", type=int, default=10, help="Máxima profundidade para o RandomForest")
    args = parser.parse_args()
    
    df = carregar_dados(args.data_path)
    
    resultado = backtest_sliding_window(
        df,
        train_size=args.train_size,
        step=args.step,
        n_numeros=args.n_numeros,
        model_fn=train_binary_models,
        predict_fn=predict_binary,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    
    from pprint import pprint
    pprint(resultado)