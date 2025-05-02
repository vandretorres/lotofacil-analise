import numpy as np
import pandas as pd
from predicao import simulacao_monte_carlo


def gerar_jogos(df, modelo, quantidade=10):
    """ Gera um conjunto de jogos baseado nas probabilidades aprendidas """
    melhores_combinacoes = simulacao_monte_carlo(modelo, 5000)  # Simulação mais extensa
    jogos_sugeridos = melhores_combinacoes.head(quantidade).index  # Pega as N melhores combinações
    
    return jogos_sugeridos
