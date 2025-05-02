import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar os dados
df = pd.read_excel("data/Lotofacil.xlsx")

# Selecionar apenas as colunas de números sorteados
colunas_numeros = [f"Bola{i}" for i in range(1, 16)]
df_numeros = df[colunas_numeros]

# Criar um DataFrame com todas as ocorrências de números sorteados
numeros_sorteados = df_numeros.melt(value_name="Numero")["Numero"]

# Contagem de frequência dos números
frequencia = numeros_sorteados.value_counts().sort_index()

# Criar gráfico de barras
plt.figure(figsize=(12, 6))
sns.barplot(x=frequencia.index, y=frequencia.values, palette="viridis")

# Adicionar títulos e legendas
plt.title("Distribuição dos Números Sorteados na Lotofácil", fontsize=16)
plt.xlabel("Números Sorteados", fontsize=14)
plt.ylabel("Frequência", fontsize=14)
plt.xticks(rotation=0)
plt.grid(axis="y", linestyle="--", alpha=0.5)

# Exibir o gráfico
plt.show()