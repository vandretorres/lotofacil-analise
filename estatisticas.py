import pandas as pd

def obter_estatisticas(df):
    """Calcula estatísticas gerais dos sorteios."""
    total_jogos = len(df)
    ultimo_sorteio = df.index[-1] if not df.empty else "Nenhum sorteio encontrado"
    
    # Identificar números mais sorteados
    contagem_numeros = df.iloc[:, 1:].apply(pd.Series.value_counts).sum(axis=1).sort_values(ascending=False)
    mais_sorteados = contagem_numeros.head(10).index.tolist()

    # Média de acertos por sorteio (quantidade de números sorteados por concurso)
    media_acertos = contagem_numeros.mean()

    return {
        "total_jogos": total_jogos,
        "ultimo_sorteio": ultimo_sorteio,
        "mais_sorteados": mais_sorteados,
        "media_acertos": round(media_acertos, 2)
    }