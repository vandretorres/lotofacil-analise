import sqlite3
import json
import datetime

# 📌 Função auxiliar para conectar ao banco
def conectar_banco():
    return sqlite3.connect("lotofacil.db")

### **1. Criar tabela para grupos de apostas**
def criar_tabela_grupos():
    """Cria a tabela de grupos de apostas no banco"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS GruposApostas (
            id_grupo TEXT PRIMARY KEY,
            data_geracao TEXT NOT NULL,
            sorteio_vinculado INTEGER NOT NULL,
            sugestao_gerada TEXT NOT NULL,
            apostas_sugeridas TEXT NOT NULL
        )
    """)
    
    conexao.commit()
    conexao.close()

# 📌 Executar criação da tabela
criar_tabela_grupos()

### **2. Salvar grupo de apostas no banco**
def salvar_grupo_apostas(grupo):
    """Salva um grupo de apostas no banco incluindo data e sorteio vinculado"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    data_geracao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "INSERT INTO GruposApostas (id_grupo, data_geracao, sorteio_vinculado, sugestao_gerada, apostas_sugeridas) VALUES (?, ?, ?, ?, ?)",
        (
            grupo["id_grupo"],
            data_geracao,
            grupo["sorteio_vinculado"],
            json.dumps([int(n) for n in grupo["sugestao_gerada"]]),  # Converte números para `int`
            json.dumps([[int(n) for n in jogo] for jogo in grupo["apostas_sugeridas"]])  # Lista correta de apostas
        )
    )
    
    conexao.commit()
    conexao.close()

### **3. Listar grupos de apostas salvos**
def listar_grupos_apostas():
    """Lista todos os grupos de apostas registrados no banco"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT id_grupo, data_geracao, sorteio_vinculado FROM GruposApostas")
    grupos = cursor.fetchall()
    
    conexao.close()
    
    return [{"id_grupo": g[0], "data_geracao": g[1], "sorteio_vinculado": g[2]} for g in grupos]

### **4. Listar sorteios que possuem apostas salvas**
def listar_sorteios_com_apostas():
    """Retorna os números de sorteios que possuem apostas registradas"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT DISTINCT sorteio_vinculado FROM GruposApostas ORDER BY sorteio_vinculado DESC")
    sorteios = cursor.fetchall()
    
    conexao.close()
    
    return [s[0] for s in sorteios]

### **5. Listar grupos de apostas vinculados a um determinado sorteio**
def listar_apostas_por_sorteio(sorteio):
    """Lista todos os grupos de apostas associados a um determinado sorteio"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT * FROM GruposApostas WHERE sorteio_vinculado = ?", (sorteio,))
    grupos = cursor.fetchall()
    
    conexao.close()
    
    return [
        {
            "id_grupo": g[0],
            "data_geracao": g[1],
            "sorteio_vinculado": g[2],
            "sugestao_gerada": json.loads(g[3]),
            "apostas_sugeridas": json.loads(g[4])
        }
        for g in grupos
    ]

### **6. Remover grupo de apostas do banco**
def remover_grupo_apostas(id_grupo):
    """Remove um grupo de apostas pelo ID"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("DELETE FROM GruposApostas WHERE id_grupo = ?", (id_grupo,))
    
    conexao.commit()
    conexao.close()