import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import MultiLabelBinarizer

# --------------------------------------------------
# MÉTODO SUPERVISIONADO
# --------------------------------------------------
def treinar_modelo(df, modelo_escolhido="RandomForest"):
    """
    Treina um modelo supervisionado utilizando os dados de sorteios.
    Usa como features os sorteios deslocados (shift de 1) e como alvo o sorteio corrente.
    """
    # Seleciona somente as colunas dos números sorteados
    colunas = [f"Bola{i}" for i in range(1, 16)]
    
    # Define X como o sorteio anterior e y como o sorteio corrente
    X = df[colunas].shift(1).dropna()
    y = df.loc[X.index, colunas]
    
    # Binariza a saída — cada sorteio é representado como uma lista de 15 números
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
    return modelo, mlb

def predicao_supervisionada(df, modelo_escolhido="RandomForest"):
    """
    Utiliza o modelo supervisionado para gerar uma predição baseada no último sorteio,
    ajustando a saída para retornar exatamente 15 números.
    
    Estratégia:
      1. Treina o modelo utilizando os dados com shift.
      2. Obtém as probabilidades para cada classe do último sorteio.
      3. Ordena as classes (números) pela probabilidade da classe 1.
      4. Seleciona os 15 números com maiores probabilidades e retorna a combinação ordenada.
    """
    modelo, mlb = treinar_modelo(df, modelo_escolhido)
    colunas = [f"Bola{i}" for i in range(1, 16)]
    X = df[colunas].shift(1).dropna()
    last_sample = X.iloc[-1:]
    
    # Verifica se o modelo possui o método 'predict_proba'
    if hasattr(modelo, "predict_proba"):
        probas = modelo.predict_proba(last_sample)
        
        # Se o retorno for uma lista (como acontece com RandomForest):
        if isinstance(probas, list):
            probs = []
            for p in probas:
                # p deve ter o shape (1,2): [prob(0), prob(1)]
                probs.append(p[0][1])
        # Se o retorno for um ndarray (como ocorre para MLP), ele terá shape (n_samples, n_labels)
        elif isinstance(probas, np.ndarray):
            probs = list(probas[0])
        else:
            probs = []
        
        # mlb.classes_ contém os números (por exemplo, array([1, 2, 3, …, 25]))
        classes = mlb.classes_
        prob_dict = dict(zip(classes, probs))
        
        # Seleciona os 15 números com maior probabilidade e monta a predição
        top15 = sorted(prob_dict, key=prob_dict.get, reverse=True)[:15]
        prediction = sorted(top15)
        print("Predição Supervisionada:", prediction)
        return prediction
    else:
        # Fallback: usa o método predict se predict_proba não estiver disponível
        pred_bin = modelo.predict(last_sample)
        prediction = mlb.inverse_transform(pred_bin)[0]
        if len(prediction) != 15:
            prediction = sorted([int(n) for n in prediction])[:15]
        print("Predição Supervisionada:", prediction)
        return prediction

# --------------------------------------------------
# MÉTODO POR FREQUÊNCIA CONDICIONAL
# --------------------------------------------------
def predicao_frequencia(df, n_numeros=15):
    """
    Utiliza a matriz de frequência condicional para sugerir uma combinação baseada no último sorteio.
    
    Estratégia:
      - Calcula a matriz de co-ocorrência dos números usando os dados históricos.
      - Para cada número de 1 a 25, calcula a média das probabilidades condicionais com base no último sorteio.
      - Seleciona os n_numeros com maiores pontuações.
    """
    from frequencia import calcular_frequencia_condicional
    freq_matrix = calcular_frequencia_condicional(df)
    colunas = [f"Bola{i}" for i in range(1, 16)]
    last_draw = df[colunas].iloc[-1].tolist()
    scores = {}
    for j in range(1, 26):
        score = np.mean([freq_matrix.loc[i, j] for i in last_draw])
        scores[j] = score
    sorted_nums = sorted(scores, key=scores.get, reverse=True)
    prediction = sorted(sorted_nums[:n_numeros])
    print("Predição por Frequência Condicional:", prediction)
    return prediction

# --------------------------------------------------
# MÉTODO POR CLUSTERING
# --------------------------------------------------
def predicao_clustering(df, n_numeros=15, num_clusters=5):
    """
    Converte os sorteios em vetores binários e aplica K-Means para identificar clusters.
    Em seguida, usa o centro do cluster mais próximo do último sorteio para sugerir uma combinação.
    
    Estratégia:
      - Converte o último sorteio em vetor binário.
      - Calcula a distância Euclidiana entre esse vetor e cada centro.
      - Seleciona os índices com maiores valores no centro do cluster mais próximo.
    """
    from clustering import clusterizar_sorteios, vetorizar_sorteio
    labels, centers = clusterizar_sorteios(df, num_clusters=num_clusters)
    colunas = [f"Bola{i}" for i in range(1, 16)]
    last_draw = df[colunas].iloc[-1].tolist()
    last_vector = vetorizar_sorteio(last_draw)
    distances = [np.linalg.norm(last_vector - center) for center in centers]
    best_cluster = np.argmin(distances)
    center = centers[best_cluster]
    candidate_order = np.argsort(-center)
    prediction = sorted([int(n + 1) for n in candidate_order[:n_numeros]])
    print("Predição por Clustering:", prediction)
    return prediction

# --------------------------------------------------
# BLOCO DE TESTE INTERATIVO
# --------------------------------------------------
if __name__ == "__main__":
    from dados import carregar_dados
    df = carregar_dados("data/Lotofacil.xlsx")
    if df is not None:
        metodo = input("Escolha o método de predição (supervisionada / frequencia / clustering): ").strip().lower()
        if metodo == "supervisionada":
            predicao_supervisionada(df)
        elif metodo == "frequencia":
            predicao_frequencia(df)
        elif metodo == "clustering":
            predicao_clustering(df)
        else:
            print("Método Inválido!")
    else:
        print("Erro ao carregar os dados.")