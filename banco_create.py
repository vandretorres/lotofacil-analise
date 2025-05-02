import sqlite3

def criar_banco():
    """Cria as tabelas do banco de dados SQLite se não existirem."""
    conexao = sqlite3.connect("lotofacil.db")
    cursor = conexao.cursor()

    # Tabela de sugestões de apostas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SugestoesApostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numeros TEXT NOT NULL,  -- Exemplo: "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15"
            data_geracao DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Sugerida' -- Pode ser 'Sugerida', 'Apostada', 'Conferida'
        )
    """)

    # Tabela de apostas realizadas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ApostasRealizadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sugestao INTEGER NOT NULL,
            sorteio INTEGER NOT NULL, -- Número do concurso
            FOREIGN KEY (id_sugestao) REFERENCES SugestoesApostas(id)
        )
    """)

    # Tabela de resultados dos sorteios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ResultadosSorteios (
            sorteio INTEGER PRIMARY KEY,
            numeros TEXT NOT NULL -- Exemplo: "1,3,5,7,9,10,12,14,15,18,19,21,22,24,25"
        )
    """)

    conexao.commit()
    conexao.close()

def conectar_banco():
    """Abre uma conexão com o banco de dados."""
    return sqlite3.connect("lotofacil.db")

# Executa a criação do banco de dados na primeira inicialização
criar_banco()
