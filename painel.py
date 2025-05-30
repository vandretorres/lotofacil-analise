import streamlit as st
import uuid
import datetime
from dados import carregar_dados
from estatisticas import obter_estatisticas
from predicao import predicao_supervisionada, predicao_frequencia, predicao_clustering
from gerador_jogos import gerar_jogos
from banco import listar_grupos_apostas, salvar_grupo_apostas, remover_grupo_apostas, listar_sorteios_com_apostas, listar_apostas_por_sorteio

# 📌 Carregar dados históricos da Lotofácil
df = carregar_dados()
estatisticas = obter_estatisticas(df)

# 📌 Inicializa variáveis do sorteio
print("\n🔎 DEBUG: Retorno de estatisticas:\n", estatisticas)
ultimo_sorteio = estatisticas["ultimo_sorteio"] if estatisticas["ultimo_sorteio"] else 0
proximo_sorteio = ultimo_sorteio + 1 if ultimo_sorteio > 0 else "Indisponível"

# 📊 Configuração inicial do painel
st.set_page_config(page_title="Painel Lotofácil", layout="wide")
st.title("🎲 Painel de Controle - Lotofácil")
st.sidebar.title("📌 Menu de Navegação")

# 📌 Criar menu de navegação na sidebar
menu_opcao = st.sidebar.radio("Escolha uma seção:", ["Dashboard", "Gerar Apostas", "Gerenciar Apostas"])

### **1️⃣ Dashboard - Exibição de Estatísticas**
if menu_opcao == "Dashboard":
    st.header("📊 Informações do Histórico")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📅 Último Sorteio", ultimo_sorteio)
        st.metric("🔜 Próximo Sorteio", proximo_sorteio)
    with col2:
        st.metric("📊 Total de Jogos", estatisticas['total_jogos'])
        st.metric("⭐ Números mais Frequentes", ", ".join(map(str, estatisticas['mais_sorteados'])))

### **2️⃣ Gerar novas apostas**
elif menu_opcao == "Gerar Apostas":
    st.header("🧠 Escolher Método de Predição")
    
    # Novo select box com 3 opções: Supervisionada, Frequência Condicional e Clustering
    metodo_predicao = st.selectbox(
        "Selecione o método de predição:",
        ["Supervisionada", "Frequência Condicional", "Clustering"]
    )
    
    # Caso o método seja supervisionado, exibe uma opção adicional para escolher o modelo
    if metodo_predicao == "Supervisionada":
        modelo_escolhido = st.radio("Selecione o modelo supervisionado:", ["RandomForest", "MLP"])
    
    # Opcional: Definir quantidade de simulações se aplicável (você pode manter ou remover esse slider, conforme a necessidade)
    n_simulacoes = st.slider("Quantidade de simulações (se aplicável):", min_value=100, max_value=5000, step=100, value=1000)

    if st.button("🔄 Gerar sugestão de aposta"):
        # Chama a função de predição de acordo com a escolha do usuário
        if metodo_predicao == "Supervisionada":
            previsao = predicao_supervisionada(df, modelo_escolhido=modelo_escolhido)
        elif metodo_predicao == "Frequência Condicional":
            previsao = predicao_frequencia(df)
        elif metodo_predicao == "Clustering":
            previsao = predicao_clustering(df)
        else:
            previsao = []
        
        # Gerar apostas sugeridas: aqui usamos a função gerar_jogos que foi atualizada para combinações aleatórias
        sugestao_jogos = [list(jogo) for jogo in gerar_jogos(df, None, None, quantidade=5).index]

        id_grupo = str(uuid.uuid4())
        data_geracao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["grupo_apostas"] = {
            "id_grupo": id_grupo,
            "data_geracao": data_geracao,
            "sorteio_vinculado": proximo_sorteio,
            "modelo_utilizado": f"{metodo_predicao}" + (f" - {modelo_escolhido}" if metodo_predicao == "Supervisionada" else ""),
            "sugestao_gerada": previsao,
            "apostas_sugeridas": sugestao_jogos
        }
        st.success(f"✅ Grupo de apostas gerado! ID: {id_grupo[-8:]} | Vinculado ao Sorteio {proximo_sorteio}")
    
    if "grupo_apostas" in st.session_state:
        st.subheader("📜 Grupo de Apostas Gerado")
        st.write(f"**ID:** `{st.session_state['grupo_apostas']['id_grupo'][-8:]}`")
        st.write(f"**Data da geração:** `{st.session_state['grupo_apostas']['data_geracao']}`")
        st.write(f"**Modelo utilizado:** `{st.session_state['grupo_apostas']['modelo_utilizado']}`")
        st.write(f"**Sugestão Gerada:** `{', '.join(map(str, st.session_state['grupo_apostas']['sugestao_gerada']))}`")
        
        st.write("**Apostas Sugeridas:**")
        for i, jogo in enumerate(st.session_state["grupo_apostas"]["apostas_sugeridas"], start=1):
            st.write(f"✅ **Jogo {i}:** {', '.join(map(str, jogo))}")
        
        if st.button("💾 Salvar Grupo de Apostas no Banco"):
            salvar_grupo_apostas(st.session_state["grupo_apostas"])
            st.success(f"✅ Grupo `{st.session_state['grupo_apostas']['id_grupo'][-8:]}` salvo!")

### **3️⃣ Gerenciar Apostas**
elif menu_opcao == "Gerenciar Apostas":
    st.header("📂 Seleção de Sorteios com Apostas")
    
    sorteios_disponiveis = listar_sorteios_com_apostas()
    if sorteios_disponiveis:
        sorteio_escolhido = st.selectbox("Escolha um sorteio para visualizar apostas:", sorteios_disponiveis)
        grupos_por_sorteio = listar_apostas_por_sorteio(sorteio_escolhido)
        if grupos_por_sorteio:
            opcoes_grupo = {f"{g['id_grupo'][-8:]} - {g['modelo_utilizado']} - {g['data_geracao']}": g for g in grupos_por_sorteio}
            id_escolhido = st.selectbox("Selecione o grupo de apostas:", list(opcoes_grupo.keys()))
            grupo_selecionado = opcoes_grupo[id_escolhido]
            st.write(f"**Data de Geração:** `{grupo_selecionado['data_geracao']}`")
            st.write(f"**Vinculado ao Sorteio:** `{grupo_selecionado['sorteio_vinculado']}`")
            st.write(f"**Sugestão Gerada:** `{', '.join(map(str, grupo_selecionado['sugestao_gerada']))}`")
            st.write(f"**Modelo utilizado:** `{grupo_selecionado['modelo_utilizado']}`")
            
            st.write("**Apostas Sugeridas:**")
            for i, jogo in enumerate(grupo_selecionado["apostas_sugeridas"], start=1):
                st.write(f"✅ **Jogo {i}:** {', '.join(map(str, jogo))}")
            
            if st.button("🗑️ Remover Grupo de Apostas"):
                remover_grupo_apostas(grupo_selecionado["id_grupo"])
                st.success(f"❌ Grupo `{grupo_selecionado['id_grupo'][-8:]}` removido do banco!")
                st.rerun()
    else:
        st.write("⚠️ Nenhum sorteio com apostas registradas ainda.")