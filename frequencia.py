import pandas as pd
import numpy as np

def calcular_frequencia_condicional(df):
    """
    Calcula a probabilidade condicional de co-ocorrência dos números sorteados.
    
    Assumindo que o DataFrame 'df' possui as colunas 'Bola1' a 'Bola15' e que os
    números possíveis variam de 1 a 25 (para Lotofácil), essa função percorre cada sorteio,
    contabiliza as co-ocorrências entre os números, e normaliza os resultados para obter a 
    probabilidade condicional.
    
    Retorna:
      - Um DataFrame onde cada célula (i, j) representa a probabilidade de o número j ser sorteado
        dado que o número i saiu.
    """
    # Definir as colunas dos números sorteados
    colunas = [f"Bola{i}" for i in range(1, 16)]
    
    # Os números possíveis são de 1 a 25 (Lotofácil)
    numeros = range(1, 26)
    # Inicializa a matriz de contagem com zeros
    frequencias = pd.DataFrame(0, index=numeros, columns=numeros, dtype=float)
    
    # Atualiza as contagens para cada sorteio
    for _, row in df[colunas].iterrows():
        sorteio = row.tolist()
        # Para cada par de números distintos dentro do mesmo sorteio
        for i in sorteio:
            for j in sorteio:
                if i != j:
                    frequencias.loc[i, j] += 1
    
    # Normaliza as contagens em cada linha para obter a probabilidade condicional
    soma_por_numero = frequencias.sum(axis=1)
    # Evita divisão por zero (caso algum número nunca tenha saído)
    soma_por_numero[soma_por_numero == 0] = 1
    prob_cond = frequencias.div(soma_por_numero, axis=0)
    
    return prob_cond

if __name__ == "__main__":
    # Teste do módulo individualmente
    # Importa a função que carrega os dados (assegure que o caminho e o nome do arquivo estão corretos)
    from dados import carregar_dados

    df = carregar_dados("data/Lotofacil.xlsx")
    if df is not None:
        prob_condicional = calcular_frequencia_condicional(df)
        print("\nMatriz de Frequência Condicional (Probabilidades):")
        print(prob_condicional)
    else:
        print("Erro ao carregar os dados.")