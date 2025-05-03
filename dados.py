import pandas as pd

def validar_dados(df):
    """
    Valida o DataFrame verificando:
      - Valores ausentes em colunas críticas
      - Registros duplicados (baseados na coluna 'Concurso')
      - Inconsistências de formatação, especialmente em 'Data Sorteio' e colunas de bolas
    """
    print("\n🔎 VALIDACAO: Verificando valores ausentes em cada coluna:")
    print(df.isna().sum())

    # Definir as colunas críticas: Concurso, Data Sorteio e as colunas das bolas
    colunas_bolas = [f"Bola{i}" for i in range(1, 16)]
    colunas_criticas = ["Concurso", "Data Sorteio"] + colunas_bolas

    for coluna in colunas_criticas:
        if coluna in df.columns:
            missing = df[coluna].isna().sum()
            if missing > 0:
                print(f"⚠️ AVISO: A coluna '{coluna}' possui {missing} valor(es) ausente(s).")

    # Verifica registros duplicados com base na coluna "Concurso"
    if "Concurso" in df.columns:
        duplicados = df["Concurso"].duplicated().sum()
        if duplicados > 0:
            print(f"⚠️ AVISO: Encontrado(s) {duplicados} registro(s) duplicado(s) na coluna 'Concurso'.")
            # Caso deseje remover duplicatas automaticamente, descomente o código abaixo:
            # df.drop_duplicates(subset=["Concurso"], inplace=True)
            # print("Duplicatas removidas com base na coluna 'Concurso'.")

    # Converte a coluna "Data Sorteio" para datetime
    if "Data Sorteio" in df.columns:
        try:
            df["Data Sorteio"] = pd.to_datetime(df["Data Sorteio"], errors="coerce", dayfirst=True)
            inconsistentes = df["Data Sorteio"].isna().sum()
            if inconsistentes > 0:
                print(f"⚠️ AVISO: Encontrados {inconsistentes} registro(s) com data inconsistente em 'Data Sorteio'.")
        except Exception as e:
            print("Erro ao converter 'Data Sorteio' para datetime:", e)

    # Converte as colunas de bolas para numérico, tratando inconsistências
    for coluna in colunas_bolas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
            inconsistentes = df[coluna].isna().sum()
            if inconsistentes > 0:
                print(f"⚠️ AVISO: Coluna '{coluna}' possui {inconsistentes} valor(es) inconsistentes convertidos para NaN.")
            df[coluna] = df[coluna].fillna(0).astype(int)

    return df

def carregar_dados(arquivo="data/Lotofacil.xlsx"):
    """
    Carrega e valida os dados da Lotofácil, exibindo debug essencial para a validação do dataset.
    """
    try:
        df = pd.read_excel(arquivo, header=0)  # A primeira linha é considerada o cabeçalho
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo} não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return None

    if "Concurso" not in df.columns:
        print("⚠️ ERRO: Coluna 'Concurso' não encontrada. Verifique o cabeçalho da planilha.")
        return None

    # Converte a coluna "Concurso" para numérico
    df["Concurso"] = pd.to_numeric(df["Concurso"], errors="coerce").fillna(0).astype(int)

    # Valida os dados e retorna o DataFrame processado
    df = validar_dados(df)
    
    return df

if __name__ == "__main__":
    # Exemplo de execução para teste
    caminho = "data/Lotofacil.xlsx"  # Ajuste o caminho conforme sua estrutura de diretórios
    dados = carregar_dados(caminho)
    if dados is not None:
        print("\n🔎 Dados carregados com sucesso!")
        print(f"Total de registros: {dados.shape[0]}")
    else:
        print("\n⚠️ Não foi possível carregar os dados.")