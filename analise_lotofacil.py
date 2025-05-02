from dados import carregar_dados
from estatisticas import analisar_frequencia, verificar_padroes
from predicao import treinar_modelo, simulacao_monte_carlo
from gerador_jogos import gerar_jogos

# Perguntar ao usuário qual modelo ele quer utilizar
modelo_escolhido = input("Escolha o modelo preditivo ('RandomForest' ou 'MLP'): ")

# 1. Carregar dados
df = carregar_dados()

# 2. Estatísticas
frequencia = analisar_frequencia(df)
print("📊 Frequência dos números sorteados:\n", frequencia.head(10))

padroes = verificar_padroes(df)
print("🔍 Padrões de sorteios recorrentes:\n", padroes.head(5))

# 3. Treinar modelo preditivo com a escolha do usuário
modelo, mlb = treinar_modelo(df, modelo_escolhido)

# 4. Simulação de Monte Carlo
simulacao = simulacao_monte_carlo(modelo, mlb, df)
print("🎲 Simulação de Monte Carlo - combinações prováveis:\n", simulacao.head(10))

# 5. Gerar jogos para apostar
jogos = gerar_jogos(df, modelo, mlb, quantidade=5)

print("🎯 Sugestões de apostas:\n", jogos)