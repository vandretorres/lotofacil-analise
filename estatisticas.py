import pandas as pd

def obter_estatisticas(df):
    """Calcula estatísticas gerais dos sorteios."""
    
    #print("\n🔎 DEBUG: Iniciando análise de estatísticas...\n")
    
    # Exibir os tipos das colunas
    print("\n➡️ Tipos das colunas:\n", df.dtypes)
    
    total_jogos = len(df)
    print("\n➡️ Total de Jogos:", total_jogos)
    
    # Definir as colunas que representam os números sorteados
    colunas_numeros = [f"Bola{i}" for i in range(1, 16)]
    
    # Exibir valores únicos em cada coluna dos números sorteados antes de convertê-los
    for coluna in colunas_numeros:
        #print(f"\n🔎 DEBUG: Valores únicos em '{coluna}':\n", df[coluna].unique())
    
    # Converter as colunas de números sorteados para garantir o tipo numérico
    df[colunas_numeros] = df[colunas_numeros].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int)
    
    # Contagem de frequência dos números sorteados
    contagem_numeros = df[colunas_numeros].apply(pd.Series.value_counts).sum(axis=1).sort_values(ascending=False)
    print("\n✅ Contagem de números mais sorteados:\n", contagem_numeros.head(10))
    
    mais_sorteados = contagem_numeros.head(10).index.tolist()
    menos_sorteados = contagem_numeros.tail(10).index.tolist()
    
    # Processamento do último sorteio baseado na coluna "Concurso"
    if not df.empty and "Concurso" in df.columns:
        df_temp = df.copy()  # Use uma cópia para não modificar o DataFrame original
        df_temp["Concurso"] = pd.to_numeric(df_temp["Concurso"], errors="coerce")
        df_temp.dropna(subset=["Concurso"], inplace=True)  # Remove linhas onde 'Concurso' não é numérico
        df_temp = df_temp[df_temp["Concurso"] > 0]  # Filtra valores inválidos (zero e negativos)
        df_temp.drop_duplicates(subset=["Concurso"], keep="last", inplace=True)  # Remove duplicatas, se houver
        df_temp.sort_values(by="Concurso", ascending=True, inplace=True)  # Ordena corretamente pelo número do concurso
        ultimo_sorteio = int(df_temp["Concurso"].max()) if not df_temp.empty else None
    else:
        ultimo_sorteio = None  # Garante que a variável sempre será definida
    
    print("\n🔎 DEBUG: Último sorteio identificado antes do retorno:", ultimo_sorteio)
    
    media_acertos = round(contagem_numeros.mean(), 2)
    
    return {
         "total_jogos": total_jogos,
         "ultimo_sorteio": ultimo_sorteio if ultimo_sorteio is not None else 0,
         "mais_sorteados": mais_sorteados,
         "media_acertos": media_acertos
    }