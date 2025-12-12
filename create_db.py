from db import get_connection, criar_banco

criar_banco()
def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Autores (
            ID_autor INT AUTO_INCREMENT PRIMARY KEY,
            Nome_autor VARCHAR(255) NOT NULL,
            Nacionalidade VARCHAR(100),
            Data_nascimento DATE,
            Biografia TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Generos (
            ID_genero INT AUTO_INCREMENT PRIMARY KEY,
            Nome_genero VARCHAR(255) NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Editoras (
            ID_editora INT AUTO_INCREMENT PRIMARY KEY,
            Nome_editora VARCHAR(255) NOT NULL,
            Endereco_editora VARCHAR(255)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            ID_usuario INT AUTO_INCREMENT PRIMARY KEY,
            Nome_usuario VARCHAR(255) NOT NULL,
            Email VARCHAR(255) NOT NULL UNIQUE,
            Numero_telefone VARCHAR(50),
            Data_inscricao DATE,
            Multa_atual DECIMAL(10,2) DEFAULT 0
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Livros (
            ID_livro INT AUTO_INCREMENT PRIMARY KEY,
            Titulo VARCHAR(255) NOT NULL,
            Autor_id INT,
            ISBN VARCHAR(50),
            Ano_publicacao YEAR,
            Genero_id INT,
            Editora_id INT,
            Quantidade_disponivel INT DEFAULT 0,
            Resumo TEXT,

            FOREIGN KEY (Autor_id) REFERENCES Autores(ID_autor)
                ON DELETE RESTRICT ON UPDATE CASCADE,

            FOREIGN KEY (Genero_id) REFERENCES Generos(ID_genero)
                ON DELETE RESTRICT ON UPDATE CASCADE,

            FOREIGN KEY (Editora_id) REFERENCES Editoras(ID_editora)
                ON DELETE RESTRICT ON UPDATE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Emprestimos (
            ID_emprestimo INT AUTO_INCREMENT PRIMARY KEY,
            Usuario_id INT NOT NULL,
            Livro_id INT NOT NULL,

            Data_emprestimo DATE NOT NULL,
            Data_devolucao_prevista DATE,
            Data_devolucao_real DATE,
            Status_emprestimo VARCHAR(50),

            FOREIGN KEY (Usuario_id) REFERENCES Usuarios(ID_usuario)
                ON DELETE RESTRICT ON UPDATE CASCADE,

            FOREIGN KEY (Livro_id) REFERENCES Livros(ID_livro)
                ON DELETE RESTRICT ON UPDATE CASCADE
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✓ Todas as tabelas foram criadas com sucesso!")
