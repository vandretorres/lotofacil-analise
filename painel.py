import streamlit as st
import uuid
from dados import carregar_dados
from estatisticas import obter_estatisticas
from predicao import treinar_modelo, simulacao_monte_carlo
from gerador_jogos import gerar_jogos
from banco import listar_grupos_apostas, salvar_grupo_apostas, remover_grupo_apostas

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

# 📌 Gerar novas sugestões de aposta
if st.button("🔄 Gerar sugestão de aposta"):
    modelo, mlb = treinar_modelo(df, modelo_escolhido)
    resultado_simulacao = simulacao_monte_carlo(modelo, mlb, df, n_simulacoes)

    melhores_numeros = resultado_simulacao.index[0] if not resultado_simulacao.empty else []    
    sugestao_jogos = gerar_jogos(df, modelo, mlb, quantidade=5).index.tolist()

    # 🔍 DEBUG: Exibir a estrutura das apostas sugeridas no terminal
    print("DEBUG - Apostas sugeridas:", sugestao_jogos)



    # Criar identificador único para o grupo de apostas
    id_grupo = str(uuid.uuid4())

    st.session_state["grupo_apostas"] = {
        "id_grupo": id_grupo,
        "sugestao_gerada": melhores_numeros,
        "apostas_sugeridas": sugestao_jogos
    }

    st.success(f"✅ Grupo de apostas gerado! ID: {id_grupo}")

# 📜 Exibir sugestões geradas
if "grupo_apostas" in st.session_state:
    st.header("📜 Grupo de Apostas Gerado")
    st.write(f"**ID:** `{st.session_state['grupo_apostas']['id_grupo']}`")
    st.write(f"**Sugestão Gerada:** `{', '.join(map(str, st.session_state['grupo_apostas']['sugestao_gerada']))}`")

    st.write("**Apostas Sugeridas:**")
    for i, jogo in enumerate(st.session_state["grupo_apostas"]["apostas_sugeridas"], start=1):
        if isinstance(jogo, (list, tuple)):  # Certifica que jogo é uma lista antes de iterar
            st.write(f"✅ **Jogo {i}:** {', '.join(map(str, jogo))}")
        else:
            st.write(f"⚠️ Erro ao exibir Jogo {i}: O formato da aposta não é uma lista.")

    # Opção de salvar o grupo no banco
    if st.button("💾 Salvar Grupo de Apostas no Banco"):
        salvar_grupo_apostas(st.session_state["grupo_apostas"])
        st.success(f"✅ Grupo de apostas `{st.session_state['grupo_apostas']['id_grupo']}` salvo!")

# 📂 Listar grupos de apostas salvos
st.header("📂 Visualizar Grupos de Apostas Salvos")
grupos_salvos = listar_grupos_apostas()
if grupos_salvos:
    id_escolhido = st.selectbox("Selecione o grupo para visualizar:", [g["id_grupo"] for g in grupos_salvos])

    grupo_selecionado = next(g for g in grupos_salvos if g["id_grupo"] == id_escolhido)
    st.write(f"**Sugestão Gerada:** `{', '.join(map(str, grupo_selecionado['sugestao_gerada']))}`")

    st.write("**Apostas Sugeridas:**")
    for i, jogo in enumerate(grupo_selecionado["apostas_sugeridas"], start=1):
        st.write(f"✅ **Jogo {i}:** {', '.join(map(str, jogo))}")

    # Opção de remover grupo de apostas
    if st.button("🗑️ Remover Grupo de Apostas"):
        remover_grupo_apostas(grupo_selecionado["id_grupo"])
        st.success(f"❌ Grupo `{grupo_selecionado['id_grupo']}` removido do banco!")

else:
    st.write("⚠️ Nenhum grupo de apostas salvo ainda.")