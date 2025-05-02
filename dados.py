import pandas as pd

def carregar_dados(arquivo="data/Lotofacil.xlsx"):
    """ Carrega os dados do arquivo da Lotofácil """
    df = pd.read_excel(arquivo)
    
    # Selecionando apenas colunas de números sorteados
    colunas_numeros = [f"Bola{i}" for i in range(1, 16)]
    df_numeros = df[colunas_numeros]
    
    return df_numeros