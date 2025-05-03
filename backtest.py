from predicao import backtest_sliding_window, predicao_supervisionada, gerar_previsao
from dados import carregar_dados

# Carrega os dados da Lotofácil
df = carregar_dados("data/Lotofacil.xlsx")

# Executa o backtest com uma janela de treino de 100 concursos
resultado = backtest_sliding_window(
    df,
    train_size=100,
    model_fn=predicao_supervisionada,
    predict_fn=gerar_previsao
)

print(f"Média de acertos por concurso: {resultado['media_acertos']:.2f} números")
print(f"(Desvio padrão: {resultado['desvio_padrao']:.2f}, folds: {resultado['total_folds']})")