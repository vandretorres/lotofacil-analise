import numpy as np
import pandas as pd
from predicao import simulacao_monte_carlo


def gerar_jogos(df, modelo, mlb, quantidade=5):
    melhores_combinacoes = simulacao_monte_carlo(modelo, mlb, df, 5000)
    return melhores_combinacoes.head(quantidade)

