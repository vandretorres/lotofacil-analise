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
# Função para preparar features enriquecidas para cada concurso
# ---------------------------------------------------------------
def prepare_enriched_features(df, windows=[3, 5, 10, 20]):
    """
    Prepara features enriquecidas para cada concurso para os 25 números.
    
    Para cada concurso (i a partir de 1), e para cada número j (1 a 25) calcula:
      - Baseline: flag binária se j apareceu no concurso anterior.
      - Rolling Frequencies: contagem de aparições para cada janela em 'windows'
        nos concursos anteriores (de max(0, i-window) até i-1).
      - Recência: número de concursos desde a última ocorrência de j.
    
    Retorna:
      X_list: lista de amostras; cada amostra é uma lista de 25 vetores de features 
              (cada vetor tem dimensão 1 (baseline) + len(windows) (frequências) + 1 (recência)).
      Y_list: lista de amostras; cada amostra é uma lista de 25 rótulos (0 ou 1), onde
              1 indica que o número j foi sorteado no concurso i.
    """
    cols = [f"Bola{i}" for i in range(1, 16)]
    n = len(df)
    X_list = []
    Y_list = []
    
    # Percorre a partir do segundo concurso (índice 1) 
    for i in range(1, n):
        features_per_sample = []  # Features para os 25 números no concurso i
        targets_per_sample = []   # Rótulos para os 25 números, baseados no concurso i
        
        # Obtenha os números do concurso anterior para o baseline
        prev_draw = df.iloc[i-1][cols].values.astype(int)
        
        # Atualize a recência para cada número: percorre os concursos anteriores até i-1
        last_occurrences = {j: None for j in range(1, 26)}
        for k in range(i):
            current_draw = df.iloc[k][cols].values.astype(int)
            for num in current_draw:
                last_occurrences[int(num)] = k
        
        # Para cada número de 1 a 25, compute as features e o rótulo
        for j in range(1, 26):
            # Baseline: se j apareceu no concurso anterior
            baseline = 1 if j in prev_draw else 0
            
            # Rolling Frequencies para cada janela em windows
            freq_features = []
            for window in windows:
                start_idx = max(0, i - window)
                # Seleciona os concursos no intervalo e achata todos os números sorteados
                window_draws = df.iloc[start_idx:i][cols].values.flatten().astype(int)
                count_j = (window_draws == j).sum()
                freq_features.append(count_j)
            
            # Recência: concursos desde que j apareceu pela última vez
            if last_occurrences[j] is None:
                recency = i  # Se nunca apareceu, definimos como i
            else:
                recency = i - last_occurrences[j]
            
            # Combine as features em um vetor para j
            features_j = [baseline] + freq_features + [recency]
            features_per_sample.append(features_j)
            
            # Rótulo: se j aparece no concurso i
            current_draw = df.iloc[i][cols].values.astype(int)
            target = 1 if j in current_draw else 0
            targets_per_sample.append(target)
        
        X_list.append(features_per_sample)
        Y_list.append(targets_per_sample)
    return X_list, Y_list


# ---------------------------------------------------------------
# Treinamento de modelos binários utilizando features enriquecidas
# ---------------------------------------------------------------
def train_binary_models_enriched(df, windows=[3, 5, 10, 20], **kwargs):
    """
    Treina 25 classificadores (um para cada número) utilizando as features enriquecidas.
    
    Args:
      df: DataFrame com os concursos.
      windows: Lista de janelas para calcular as rolling frequencies.
      kwargs: Parâmetros para o RandomForestClassifier.
      
    Retorna:
      models: Dicionário de modelos treinados.
    """
    X_list, Y_list = prepare_enriched_features(df, windows=windows)
    X_array = np.array(X_list)  # Shape: (n_samples, 25, feature_dim)
    Y_array = np.array(Y_list)  # Shape: (n_samples, 25)
    
    from sklearn.ensemble import RandomForestClassifier
    models = {}
    # Define os hiperparâmetros desejados e combina com quaisquer parâmetros adicionais
    params = {
        'n_estimators': 211,
        'max_depth': 15,
        'max_features': 'log2',
        'min_samples_split': 9,
        'min_samples_leaf': 4,
        **kwargs
    }
    for j in range(25):
        clf = RandomForestClassifier(n_jobs=-1, **params)
        clf.fit(X_array[:, j, :], Y_array[:, j])
        models[j + 1] = clf  # Número 1-indexado
    return models


# ---------------------------------------------------------------
# Preparar features enriquecidas para o teste (último concurso disponível)
# ---------------------------------------------------------------
def get_enriched_features_for_test(treino, windows=[3, 5, 10, 20]):
    """
    Prepara as features enriquecidas para o último concurso em 'treino', para cada número 1-25.
    Retorna uma matriz de shape (25, feature_dim).
    """
    cols = [f"Bola{i}" for i in range(1, 16)]
    n = len(treino)
    
    # Baseline: os números do último concurso
    prev_draw = treino.iloc[-1][cols].values.astype(int)
    
    # Determina recência com base em todos os concursos
    last_occurrences = {j: None for j in range(1, 26)}
    for k in range(n):
        current_draw = treino.iloc[k][cols].values.astype(int)
        for num in current_draw:
            last_occurrences[int(num)] = k
            
    features_test = []
    for j in range(1, 26):
        baseline = 1 if j in prev_draw else 0
        freq_features = []
        for window in windows:
            start_idx = max(0, n - window)
            window_draws = treino.iloc[start_idx:n][cols].values.flatten().astype(int)
            count_j = (window_draws == j).sum()
            freq_features.append(count_j)
        if last_occurrences[j] is None:
            recency = n
        else:
            recency = n - last_occurrences[j]
        features_j = [baseline] + freq_features + [recency]
        features_test.append(features_j)
    return np.array(features_test)  # Shape: (25, feature_dim)


# ---------------------------------------------------------------
# Predição a partir dos modelos binários enriquecidos
# ---------------------------------------------------------------
def predict_binary_enriched(models, treino, windows=[3, 5, 10, 20], n_numeros=15):
    """
    Gera a previsão para o próximo concurso a partir dos modelos treinados com features enriquecidas.
    
    Args:
      models: Dicionário dos modelos treinados.
      treino: DataFrame contendo os concursos de treinamento.
      windows: Lista de janelas utilizadas para as features.
      n_numeros: Quantidade de números a prever.
      
    Retorna:
      selected: Lista com os n_numeros (ordenados) selecionados com maior probabilidade.
    """
    features_test = get_enriched_features_for_test(treino, windows=windows)  # Shape (25, feature_dim)
    probabilities = {}
    for num, clf in models.items():
        prob = clf.predict_proba(features_test[num-1].reshape(1, -1))[0][1]
        probabilities[num] = prob
    selected = sorted(probabilities, key=probabilities.get, reverse=True)[:n_numeros]
    return sorted(selected)


# ---------------------------------------------------------------
# Backtest com janela móvel (sliding window) com relatório detalhado
# ---------------------------------------------------------------
def backtest_sliding_window(df, train_size, model_fn, predict_fn, *,
                            step=1, n_numeros=15, report_path="backtest_detalhes.csv",
                            max_folds=None, **model_kwargs):
    """
    Executa um backtest temporal com janelas móveis e gera relatório CSV.

    Treina o modelo com concursos de 1 até N e testa no concurso N+1, 
    avançando a janela de treino de 'step' em 'step'.

    Args:
        df (pd.DataFrame): Base histórica de sorteios.
        train_size (int): Número de concursos usados para o treino inicial.
        model_fn (callable): Função que treina o modelo.
        predict_fn (callable): Função que gera previsão.
        step (int): Passo do sliding window.
        n_numeros (int): Quantos números prever.
        report_path (str): Caminho para salvar relatório CSV.
        max_folds (int ou None): Número máximo de folds a serem executados. Se None, executa todos.
        model_kwargs: Parâmetros adicionais para o model_fn.

    Returns:
        dict: Estatísticas do backtest, com média, desvio, mediana, histograma e folds.
    """
    from tqdm import tqdm

    all_scores = []

    # Loop de backtest com limite de folds se especificado
    for fold_idx, end in enumerate(tqdm(range(train_size, len(df) - 1, step), desc="Backtest folds"), start=1):
        if max_folds is not None and fold_idx > max_folds:
            break
        treino = df.iloc[:end]
        teste  = df.iloc[end]
        modelo = model_fn(treino, **model_kwargs)
        previsao = predict_fn(modelo, treino, n_numeros)

        # números reais
        cols = [f"Bola{i}" for i in range(1, 16)]
        real = teste[cols].tolist()
        score = hit_rate(previsao, real)
        all_scores.append(score)

    # Estatísticas
    mean_score   = np.mean(all_scores)
    std_score    = np.std(all_scores)
    median_score = np.median(all_scores)
    hist_counts  = Counter(all_scores)
    folds        = len(all_scores)

    # Percentis
    p25 = np.percentile(all_scores, 25)
    p50 = np.percentile(all_scores, 50)
    p75 = np.percentile(all_scores, 75)

    # Imprime percentis
    print(f"\nBacktest completo ({folds} folds):")
    print(f"  25º percentil: {p25:.3f}")
    print(f"  Mediana (50º): {p50:.3f}")
    print(f"  75º percentil: {p75:.3f}\n")

    # Gera DataFrame detalhado e salva
    df_report = pd.DataFrame({
        "fold":     list(range(1, folds + 1)),
        "hit_rate": all_scores
    })
    df_report.to_csv(report_path, index=False)
    print(f"Relatório detalhado salvo em: {report_path}")

    return {
        "mean":   mean_score,
        "std":    std_score,
        "median": median_score,
        "hist":   hist_counts,
        "folds":  folds,
        "scores": all_scores,
        "percentiles": {"25%": p25, "50%": p50, "75%": p75}
    }


# ------------------------------------------------------------------
# Treinamento de modelos binários: um classificador por número (1 a 25)
# ------------------------------------------------------------------
def train_binary_models(df, **kwargs):
    cols = [f"Bola{i}" for i in range(1, 16)]
    X_list, Y_list = [], []
    n = len(df)
    for i in range(1, n):
        prev = df.iloc[i - 1][cols].values
        curr = df.iloc[i][cols].values
        X_vec = [0] * 25
        Y_vec = [0] * 25
        for num in prev:
            X_vec[int(num) - 1] = 1
        for num in curr:
            Y_vec[int(num) - 1] = 1
        X_list.append(X_vec)
        Y_list.append(Y_vec)

    X_array = np.array(X_list)
    Y_array = np.array(Y_list)
    from sklearn.ensemble import RandomForestClassifier
    models = {}
    # Define os hiperparâmetros desejados e combina com quaisquer parâmetros adicionais
    params = {
        'n_estimators': 211,
        'max_depth': 15,
        'max_features': 'log2',
        'min_samples_split': 9,
        'min_samples_leaf': 4,
        **kwargs
    }
    for j in range(25):
        clf = RandomForestClassifier(n_jobs=-1, **params)
        clf.fit(X_array, Y_array[:, j])
        models[j + 1] = clf
    return models


# ---------------------------------------------------------------
# Predição a partir dos modelos binários treinados
# ---------------------------------------------------------------
def predict_binary(models, treino, n_numeros):
    cols = [f"Bola{i}" for i in range(1, 16)]
    last = treino.iloc[-1][cols].values
    X_vec = [0] * 25
    for num in last:
        X_vec[int(num) - 1] = 1
    X_vec = np.array(X_vec).reshape(1, -1)

    probabilities = {}
    for num, clf in models.items():
        prob = clf.predict_proba(X_vec)[0][1]
        probabilities[num] = prob

    selected = sorted(probabilities, key=probabilities.get, reverse=True)[:n_numeros]
    return sorted(selected)


# ---------------------------------------------------------------
# Exemplo de execução com backtest e argumentos de linha de comando
# ---------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    from dados import carregar_dados

    parser = argparse.ArgumentParser(
        description="Backtest Lotofácil usando modelos binários"
    )
    parser.add_argument("--train_size", type=int, default=100, help="Concursos iniciais para treino")
    parser.add_argument("--step", type=int, default=1, help="Passo do sliding window")
    parser.add_argument("--n_numeros", type=int, default=15, help="Quantidade de números a prever")
    parser.add_argument("--data_path", type=str, default="data/Lotofacil.xlsx", help="Caminho dos dados")
    parser.add_argument("--n_estimators", type=int, default=211, help="Estimadores do RandomForest")
    parser.add_argument("--max_depth", type=lambda x: None if x=="None" else int(x), default=15, help="Profundidade máxima do RF")
    parser.add_argument("--report_path", type=str, default="backtest_detalhes.csv", help="CSV de saída")
    parser.add_argument("--max_folds", type=lambda x: None if x=="None" else int(x), default=None, help="Número máximo de folds a executar; se None, executa todos")
    args = parser.parse_args()

    df = carregar_dados(args.data_path)

    results = backtest_sliding_window(
        df,
        train_size=args.train_size,
        step=args.step,
        n_numeros=args.n_numeros,
        report_path=args.report_path,
        max_folds=args.max_folds,  # Novo parâmetro para limitar folds
        model_fn=train_binary_models,  # Se desejar testar a versão enriquecida, altere para train_binary_models_enriched
        predict_fn=predict_binary,       # Ou para predict_binary_enriched, conforme sua necessidade
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )

    from pprint import pprint
    pprint(results)