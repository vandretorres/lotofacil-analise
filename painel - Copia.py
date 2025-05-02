import streamlit as st
from dados import carregar_dados
from estatisticas import obter_estatisticas
from predicao import treinar_modelo, simulacao_monte_carlo
from gerador_jogos import gerar_jogos
from banco import listar_sugestoes, salvar_sugestao, registrar_aposta, salvar_resultado_sorteio, conferir_apostas

# 📌 Carregar dados históricos da Lotofácil
df = carregar_dados()  # Obtém os sorteios registrados
estatisticas = obter_estatisticas(df)  # Calcula estatísticas sobre os sorteios

# 📊 Configuração inicial do painel
st.title("🎲 Painel de Controle - Lotofácil")
st.write("Gerencie suas apostas e acompanhe os resultados.")

# 📊 Exibir estatísticas do histórico
st.header("📊 Informações do Histórico")
st.write(f"- **Total de jogos analisados:** {estatisticas['total_jogos']}")
st.write(f"- **Último sorteio registrado:** {estatisticas['ultimo_sorteio']}")
st.write(f"- **Números mais frequentes:** {estatisticas['mais_sorteados']}")
st.write(f"- **Média de acertos por sorteio:** {estatisticas['media_acertos']}")

# 🧠 Escolher modelo preditivo e definir simulações
st.header("🧠 Escolher Modelo de Previsão")
modelo_escolhido = st.selectbox("Selecione o modelo:", ["RandomForest", "MLP"])
n_simulacoes = st.slider("Quantidade de simulações para previsão:", min_value=100, max_value=5000, step=100, value=1000)

# 📌 Gerar novas sugestões de aposta usando `predicao.py`
if st.button("🔄 Gerar sugestão de aposta"):
    modelo, mlb = treinar_modelo(df, modelo_escolhido)
    resultado_simulacao = simulacao_monte_carlo(modelo, mlb, df, n_simulacoes)
    
    # Selecionando os números mais prováveis e gerando jogos recomendados
    melhores_numeros = resultado_simulacao.index[0] if not resultado_simulacao.empty else []    
    sugestao_jogos = gerar_jogos(df, modelo, mlb, quantidade=5)


    salvar_sugestao(list(melhores_numeros))  # Salvar no banco    
    st.success(f"✅ Sugestão de aposta gerada! {', '.join(map(str, melhores_numeros))}")

# 📜 Exibir sugestões registradas de forma aprimorada
st.header("📜 Apostas Sugeridas")
sugestoes = listar_sugestoes()
if sugestoes:
    for s in sugestoes:
        st.write(f"**ID:** `{s[0]}` | **Números:** `{s[1]}` | **Status:** `{s[3]}`")
else:
    st.write("⚠️ Nenhuma sugestão registrada.")

# 📌 Registrar aposta realizada
st.header("🎟️ Marcar Aposta Realizada")
id_sugestao = st.number_input("Digite o ID da sugestão que foi apostada:", min_value=1)
sorteio = st.number_input("Digite o número do sorteio:", min_value=3000)
if st.button("Registrar aposta"):
    registrar_aposta(id_sugestao, sorteio)
    st.success(f"✅ Aposta ID {id_sugestao} registrada no sorteio {sorteio}!")

# 📌 Salvar resultado do sorteio
st.header("🏆 Registrar Resultado do Sorteio")
sorteio_resultado = st.number_input("Número do sorteio:", min_value=3000, key="sorteio_resultado")
numeros_sorteados = st.text_input("Digite os números sorteados (separados por vírgula):")
if st.button("Salvar resultado"):
    lista_numeros = list(map(int, numeros_sorteados.split(",")))
    salvar_resultado_sorteio(sorteio_resultado, lista_numeros)
    st.success(f"✅ Resultado do sorteio {sorteio_resultado} salvo!")

# 📌 Conferir apostas realizadas
st.header("🔍 Conferir Apostas no Sorteio")
sorteio_conferir = st.number_input("Número do sorteio para conferência:", min_value=3000, key="sorteio_conferir")
if st.button("Verificar apostas"):
    resultado = conferir_apostas(sorteio_conferir)
    if resultado:
        for id_aposta, acertos in resultado:
            st.write(f"✅ **Aposta ID {id_aposta}:** Acertou `{len(acertos)}` números {acertos}")
    else:
        st.write("⚠️ Nenhuma aposta acertou números nesse sorteio.")