import pandas as pd
import random
from dados import carregar_dados
from predicao import predicao_supervisionada, predicao_frequencia, predicao_clustering

# Parâmetros iniciais
SORTEIO_INICIAL = 3000  # Primeiro sorteio a ser testado
INTERVALO_SORTEIO = 10  # Intervalo entre os testes (ex.: 1000, 1050, 1100, ...)
NUM_SORTEIOS = 38       # Quantidade de sorteios a testar
#METODOS = ["supervisionada", "frequencia", "clustering"]
METODOS = ["frequencia"]

def gerar_apostas(predicao, quantidade=5):
    """
    Gera apostas com base na predição, adicionando pequenas variações aleatórias.

    Parâmetros:
      - predicao: Lista de números preditos pelo modelo.
      - quantidade: Número de apostas a gerar.

    Retorna:
      - Lista de apostas geradas.
    """
    apostas = []
    for _ in range(quantidade):
        aposta = sorted(random.sample(predicao + random.sample(range(1, 26), 10), 15))
        apostas.append(aposta)
    return apostas

def testar_predicao(df, metodo):
    """
    Executa testes de predição para diferentes sorteios históricos e registra os acertos.

    Parâmetros:
      - df: DataFrame com os dados históricos da Lotofácil.
      - metodo: Método de predição a ser testado.

    Retorna:
      - DataFrame com os resultados das simulações.
    """
    resultados = []
    
    for i in range(NUM_SORTEIOS):
        sorteio_atual = SORTEIO_INICIAL + (i * INTERVALO_SORTEIO)
        df_treino = df[df["Concurso"] < sorteio_atual]  # Usa apenas sorteios anteriores como base
        resultado_real = df[df["Concurso"] == sorteio_atual]  # Obtém o resultado oficial do sorteio

        if resultado_real.empty:
            continue  # Se o sorteio não existir nos dados, pula a iteração

        # Aplicação do método de predição escolhido
        if metodo == "supervisionada":
            previsao = predicao_supervisionada(df_treino, modelo_escolhido="RandomForest")
        elif metodo == "frequencia":
            previsao = predicao_frequencia(df_treino)
        elif metodo == "clustering":
            previsao = predicao_clustering(df_treino)
        else:
            raise ValueError("Método inválido!")

        # Gerando 5 apostas baseadas na predição
        apostas_geradas = gerar_apostas(previsao, quantidade=10)

        # Obtém os números reais sorteados
        numeros_sorteados = resultado_real.iloc[0][[f"Bola{i}" for i in range(1, 16)]].tolist()

        # Calcula os acertos de cada aposta gerada
        acertos_lista = [len(set(aposta) & set(numeros_sorteados)) for aposta in apostas_geradas]

        # Registra os resultados
        resultados.append({
            "Sorteio": sorteio_atual,
            "Metodo": metodo,
            "Predicao": previsao,
            "Numeros_Reais": numeros_sorteados,
            "Apostas_Geradas": apostas_geradas,
            "Acertos_Por_Aposta": acertos_lista
        })

    return pd.DataFrame(resultados)

# 🚀 Executa os testes e salva os resultados
if __name__ == "__main__":
    df = carregar_dados("data/Lotofacil.xlsx")

    if df is not None:
        tabela_resultados = pd.DataFrame()

        for metodo in METODOS:
            print(f"\n🔍 Testando método: {metodo}")
            df_resultado = testar_predicao(df, metodo)
            tabela_resultados = pd.concat([tabela_resultados, df_resultado], ignore_index=True)

            # Exibir os resultados em tempo real
            for _, row in df_resultado.iterrows():
                print(f"\n🎯 Sorteio {row['Sorteio']} - Método: {row['Metodo']}")
                print(f"   🔢 Predição: {row['Predicao']}")
                print(f"   🎲 Números Sorteados: {row['Numeros_Reais']}")
                print("   ✅ Apostas Geradas e Acertos:")
                for i, aposta in enumerate(row["Apostas_Geradas"], start=1):
                    print(f"      🃏 Jogo {i}: {aposta} 🎯 Acertos: {row['Acertos_Por_Aposta'][i-1]}")

        # Salvar os resultados
        tabela_resultados.to_csv("resultados_predicao.csv", index=False)

        # Exibe um resumo dos acertos
        print("\n📈 Resumo de acertos por método:")
        print(tabela_resultados.groupby("Metodo")["Acertos_Por_Aposta"].apply(lambda x: sum(map(sum, x)) / len(x)))

    else:
        print("Erro ao carregar os dados.")
