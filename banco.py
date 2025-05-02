import sqlite3
import json

# Função auxiliar para conectar ao banco
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
            sugestao_gerada TEXT NOT NULL,
            apostas_sugeridas TEXT NOT NULL
        )
    """)
    
    conexao.commit()
    conexao.close()

# Executar a criação da tabela
criar_tabela_grupos()

### **2. Salvar grupo de apostas no banco**
def salvar_grupo_apostas(grupo):
    """Salva um grupo de apostas no banco"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute(
        "INSERT INTO GruposApostas (id_grupo, sugestao_gerada, apostas_sugeridas) VALUES (?, ?, ?)",
        (
            grupo["id_grupo"],
            json.dumps([int(n) for n in grupo["sugestao_gerada"]]),  # Converte todos os números para `int`
            json.dumps([[int(n) for n in jogo] for jogo in grupo["apostas_sugeridas"]])  # Garante listas corretas
        )
    )
    



    conexao.commit()
    conexao.close()

### **3. Listar grupos de apostas salvos**
def listar_grupos_apostas():
    """Lista todos os grupos de apostas registrados no banco"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("SELECT * FROM GruposApostas")
    grupos = cursor.fetchall()
    
    conexao.close()
    
    return [
        {"id_grupo": g[0], "sugestao_gerada": json.loads(g[1]), "apostas_sugeridas": json.loads(g[2])}
        for g in grupos
    ]

### **4. Remover grupo de apostas do banco**
def remover_grupo_apostas(id_grupo):
    """Remove um grupo de apostas pelo ID"""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    cursor.execute("DELETE FROM GruposApostas WHERE id_grupo = ?", (id_grupo,))
    
    conexao.commit()
    conexao.close()