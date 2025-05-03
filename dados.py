import pandas as pd

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
    
    # Debug para garantir que os sorteios foram lidos corretamente
    print("🔎 DEBUG: Valores únicos em 'Concurso' após conversão:", df["Concurso"].unique())
    print("🔎 DEBUG: Maior valor em 'Concurso':", df["Concurso"].max())
    
    return df