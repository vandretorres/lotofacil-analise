import pandas as pd

def backtest_frequencia(df, num_sorteios=100, meta_acertos=11):
    """Executa backtest baseado na frequência dos números mais sorteados."""
    
    # Garantir que os dados estão ordenados pelo número do concurso
    df = df.sort_values(by="Concurso", ascending=True)
    
    # Definir as colunas que representam os números sorteados
    colunas_numeros = [f"Bola{i}" for i in range(1, 16)]
    
    acertos_por_sorteio = []

    for i in range(len(df) - num_sorteios, len(df)):  # Últimos `num_sorteios` concursos
        df_treino = df.iloc[:i]  # Usa todos os sorteios anteriores como treino
        df_teste = df.iloc[i]  # Usa o sorteio atual como teste
        
        # Contagem de frequência dos números sorteados
        contagem_numeros = df_treino[colunas_numeros].apply(pd.Series.value_counts).sum(axis=1).sort_values(ascending=False)
        
        # Selecionar os 15 números mais frequentes
        numeros_preditos = set(contagem_numeros.head(15).index)
        
        # Números sorteados no concurso atual
        numeros_reais = set(df_teste[colunas_numeros].values)
        
        # Calcular acertos
        acertos = len(numeros_preditos.intersection(numeros_reais))
        acertos_por_sorteio.append(acertos)

        print(f"🎯 Sorteio {df_teste['Concurso']}: {acertos} acertos")

    # Resultados gerais
    acertos_medio = sum(acertos_por_sorteio) / len(acertos_por_sorteio)
    acertos_acima_meta = sum(a >= meta_acertos for a in acertos_por_sorteio)

    print("\n📊 **Resultados do Backtest**")
    print(f"- Média de acertos por sorteio: {acertos_medio:.2f}")
    print(f"- Sorteios com >= {meta_acertos} acertos: {acertos_acima_meta}/{num_sorteios}")

    return acertos_por_sorteio

# Carregar dados do histórico de sorteios (ajuste o caminho do arquivo)
df = pd.read_excel("data/Lotofacil.xlsx", engine="openpyxl")

# Rodar o backtest
backtest_frequencia(df)