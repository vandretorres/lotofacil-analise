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

    # Definir as colunas críticas (sorteio, data e bolas)
    colunas_bolas = [f"Bola{i}" for i in range(1, 16)]
    colunas_criticas = ["Concurso", "Data Sorteio"] + colunas_bolas

    for coluna in colunas_criticas:
        if coluna in df.columns:
            missing = df[coluna].isna().sum()
            if missing > 0:
                print(f"⚠️ AVISO: A coluna '{coluna}' possui {missing} valores ausentes.")

    # Verifica registros duplicados na coluna "Concurso"
    if "Concurso" in df.columns:
        duplicados = df["Concurso"].duplicated().sum()
        if duplicados > 0:
            print(f"⚠️ AVISO: Encontrado(s) {duplicados} registro(s) duplicado(s) na coluna 'Concurso'.")
            # Se desejar, descomente as linhas abaixo para remover duplicatas automaticamente.
            # df.drop_duplicates(subset=["Concurso"], inplace=True)
            # print("Duplicatas removidas com base na coluna 'Concurso'.")

    # Tenta converter a coluna "Data Sorteio" para datetime com o formato correto
    if "Data Sorteio" in df.columns:
        try:
            df["Data Sorteio"] = pd.to_datetime(df["Data Sorteio"], errors="coerce", dayfirst=True)
            inconsistentes = df["Data Sorteio"].isna().sum()
            if inconsistentes > 0:
                print(f"⚠️ AVISO: Encontrados {inconsistentes} registro(s) com formato de data inconsistente em 'Data Sorteio'.")
        except Exception as e:
            print("Erro ao converter 'Data Sorteio' para datetime:", e)

    # Converter as colunas de bolas para numérico e tratar possíveis inconsistências
    for coluna in colunas_bolas:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
            inconsistentes = df[coluna].isna().sum()
            if inconsistentes > 0:
                print(f"⚠️ AVISO: Coluna '{coluna}' possui {inconsistentes} valor(es) inconsistentes que foram convertidos para NaN.")
            df[coluna] = df[coluna].fillna(0).astype(int)

    return df

def carregar_dados(arquivo="data/Lotofacil.xlsx"):
    """Carrega e valida os dados da Lotofácil, exibindo debug essencial para a validação do dataset completo."""
    try:
        df = pd.read_excel(arquivo, header=0)  # Garante que a primeira linha seja o cabeçalho
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo} não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao carregar arquivo: {e}")
        return None

    # Debug mínimo para validar se a base está completa
    print("\n🔎 DEBUG: Número total de linhas lidas:", df.shape[0])
    print("🔎 DEBUG: Colunas carregadas:", df.columns.tolist())

    if "Concurso" not in df.columns:
        print("⚠️ ERRO: Coluna 'Concurso' não encontrada no arquivo! Verifique o cabeçalho da planilha.")
        return None

    # Converter a coluna "Concurso" para numérico
    df["Concurso"] = pd.to_numeric(df["Concurso"], errors="coerce").fillna(0).astype(int)
    print("🔎 DEBUG: Valores únicos em 'Concurso' após conversão:", df["Concurso"].unique())
    print("🔎 DEBUG: Maior valor em 'Concurso':", df["Concurso"].max())

    # Validação adicional dos dados
    df = validar_dados(df)
    
    return df