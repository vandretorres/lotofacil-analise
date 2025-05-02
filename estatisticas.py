import pandas as pd

def analisar_frequencia(df):
    """ Calcula a frequência de cada número sorteado """
    frequencia = df.melt(value_name="Numero")["Numero"].value_counts()
    return frequencia.sort_values(ascending=False)

def verificar_padroes(df):
    """ Identifica repetições e padrões comuns nos sorteios """
    sequencias = df.apply(lambda row: tuple(sorted(row)), axis=1)
    padroes_comuns = sequencias.value_counts()
    return padroes_comuns.head(10)  # Mostra os 10 padrões mais comuns