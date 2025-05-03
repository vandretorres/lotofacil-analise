import streamlit as st
from zoneinfo import ZoneInfo
from datetime import datetime
import uuid

from dados import carregar_dados
from estatisticas import obter_estatisticas
from predicao import predicao_supervisionada, predicao_frequencia, predicao_clustering
from gerador_jogos import gerar_jogos
from banco import listar_sorteios_com_apostas, listar_apostas_por_sorteio, salvar_grupo_apostas, remover_grupo_apostas

# Carrega e cacheia dados e estatísticas
@st.cache_data
def get_data(path: str = "data/Lotofacil.xlsx"):
    return carregar_dados(path)

@st.cache_data
def get_stats(df):
    return obter_estatisticas(df)

# Gera metadados para cada grupo
def criar_metadata(modelo: str, sorteio: int) -> dict:
    return {
        "id_grupo": str(uuid.uuid4()),
        "data_geracao": datetime.now(tz=ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S"),
        "sorteio_vinculado": sorteio,
        "modelo_utilizado": modelo,
    }

# Exibe painel de estatísticas
def show_dashboard(stats: dict):
    st.header("📊 Histórico de Sorteios da Lotofácil")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Último Sorteio", stats["ultimo_sorteio"])
        prox = stats["ultimo_sorteio"] + 1 if stats["ultimo_sorteio"] else "N/A"
        st.metric("Próximo Sorteio", prox)
    with col2:
        st.metric("Total de Concursos", stats["total_jogos"])
        st.metric("Números Mais Frequentes", ", ".join(map(str, stats["mais_sorteados"])))

# Exibe formulário e resultados de geração
def show_generate(df, stats: dict):
    st.header("🧠 Gerar Novas Apostas")
    metodo = st.selectbox("Método de Predição", ["Supervisionada", "Frequência Condicional", "Clustering"])
    modelo = None
    if metodo == "Supervisionada":
        modelo = st.radio("Modelo Supervisionado", ["RandomForest", "MLP"], horizontal=True)

    if st.button("🔄 Gerar Sugestões"):
        with st.spinner("Processando..."):
            if metodo == "Supervisionada":
                previsao = predicao_supervisionada(df, modelo_escolhido=modelo)
                label = f"{metodo} - {modelo}"
            elif metodo == "Frequência Condicional":
                previsao = predicao_frequencia(df)
                label = metodo
            else:
                previsao = predicao_clustering(df)
                label = metodo

            # garante lista de ints
            try:
                sugestoes = [int(x) for x in previsao.tolist()]
            except Exception:
                sugestoes = [int(x) for x in previsao]

            # gera apostas (5 jogos por padrão)
            jogos_df = gerar_jogos(df, None, None, quantidade=5)
            apostas = [list(idx) for idx in jogos_df.index]

            grupo = {**criar_metadata(label, stats["ultimo_sorteio"] + 1 if stats["ultimo_sorteio"] else 0),
                     "sugestao_gerada": sugestoes,
                     "apostas_sugeridas": apostas}
            st.session_state["grupo_temp"] = grupo
            st.success(f"✅ Grupo gerado! ID {grupo['id_grupo'][-8:]} | Sorteio {grupo['sorteio_vinculado']}")

    if grp := st.session_state.get("grupo_temp"):
        st.subheader("📜 Detalhes do Grupo Gerado")
        st.write(f"**ID:** {grp['id_grupo']}")
        st.write(f"**Data:** {grp['data_geracao']}")
        st.write(f"**Modelo:** {grp['modelo_utilizado']}")
        st.write(f"**Sugestão Gerada:** {', '.join(map(str, grp['sugestao_gerada']))}")
        st.write("**Apostas Sugeridas:**")
        for i, jogo in enumerate(grp['apostas_sugeridas'], 1):
            st.write(f"✅ Jogo {i}: {', '.join(map(str, jogo))}")

        if st.button("💾 Salvar no Banco"):
            salvar_grupo_apostas(grp)
            st.success("✅ Grupo salvo no banco!")
            # limpa temporário
            del st.session_state["grupo_temp"]

# Exibe e gerencia apostas salvas
def show_manage():
    st.header("📂 Gerenciar Apostas")
    sorteios = listar_sorteios_com_apostas()
    if not sorteios:
        st.info("Nenhum sorteio com apostas registradas.")
        return

    sel = st.selectbox("Selecione o Sorteio", sorteios)
    grupos = listar_apostas_por_sorteio(sel)
    if not grupos:
        st.info("Nenhum grupo para este sorteio.")
        return

    op = {f"{g['id_grupo'][-8:]} - {g['modelo_utilizado']}": g for g in grupos}
    chave = st.selectbox("Selecione o Grupo", list(op.keys()))
    g = op[chave]

    st.write(f"**ID:** {g['id_grupo']}")
    st.write(f"**Data:** {g['data_geracao']}")
    st.write(f"**Sorteio:** {g['sorteio_vinculado']}")
    st.write(f"**Modelo:** {g['modelo_utilizado']}")
    st.write(f"**Sugestão Gerada:** {', '.join(map(str, g['sugestao_gerada']))}")
    st.write("**Apostas Sugeridas:**")
    for i, jogo in enumerate(g['apostas_sugeridas'], 1):
        st.write(f"✅ Jogo {i}: {', '.join(map(str, jogo))}")

    if st.button("🗑️ Remover Grupo"):
        remover_grupo_apostas(g['id_grupo'])
        st.success("❌ Grupo removido com sucesso!")
        st.rerun()

# Função principal
if __name__ == "__main__":
    st.set_page_config(page_title="Painel Lotofácil", layout="wide")
    df = get_data()
    stats = get_stats(df)

    st.title("🎲 Painel Lotofácil")
    menu = st.sidebar.radio("Menu", ["Dashboard", "Gerar Apostas", "Gerenciar Apostas"])

    if menu == "Dashboard":
        show_dashboard(stats)
    elif menu == "Gerar Apostas":
        show_generate(df, stats)
    else:
        show_manage()
