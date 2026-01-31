from db import get_connection, criar_banco

criar_banco()

def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    # Remover tabelas existentes para recriar
    cursor.execute("DROP TABLE IF EXISTS Emprestimos")
    cursor.execute("DROP TABLE IF EXISTS Livros")
    cursor.execute("DROP TABLE IF EXISTS Usuarios")
    cursor.execute("DROP TABLE IF EXISTS Editoras")
    cursor.execute("DROP TABLE IF EXISTS Generos")
    cursor.execute("DROP TABLE IF EXISTS Autores")
    cursor.execute("DROP TABLE IF EXISTS logs_auditoria")

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
            Status ENUM('ativo', 'inativo') DEFAULT 'ativo',
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
            Status_emprestimo ENUM('pendente', 'devolvido', 'atrasado') DEFAULT 'pendente',

            FOREIGN KEY (Usuario_id) REFERENCES Usuarios(ID_usuario)
                ON DELETE RESTRICT ON UPDATE CASCADE,

            FOREIGN KEY (Livro_id) REFERENCES Livros(ID_livro)
                ON DELETE RESTRICT ON UPDATE CASCADE
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id_log INT AUTO_INCREMENT PRIMARY KEY,
            tabela_afetada VARCHAR(50),
            operacao VARCHAR(20),
            data_operacao DATETIME,
            usuario_afetado INT,
            descricao TEXT
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Tabelas criadas com sucesso")


def criar_triggers():
    conn = get_connection()
    cursor = conn.cursor()

    #remover triggers antigas
    cursor.execute("DROP TRIGGER IF EXISTS trg_usuario_data_inscricao;")
    cursor.execute("DROP TRIGGER IF EXISTS trg_usuario_status_padrao;")
    cursor.execute("DROP TRIGGER IF EXISTS trg_emprestimo_data;")
    cursor.execute("DROP TRIGGER IF EXISTS trg_emprestimo_data_prevista;")
    cursor.execute("DROP TRIGGER IF EXISTS trg_emprestimo_status_padrao;")

    # TRIGGERS DE GERAÇÃO AUTOMÁTICA DE DADOS - Marcos Cassiano

    # TRIGGER 1
    # Data de inscrição automática

    cursor.execute("""
        CREATE TRIGGER trg_usuario_data_inscricao
        BEFORE INSERT ON Usuarios
        FOR EACH ROW
        BEGIN
            IF NEW.Data_inscricao IS NULL THEN
                SET NEW.Data_inscricao = CURDATE();
            END IF;
        END;
    """)

    # TRIGGER 2
    # Status inicial do usuário

    cursor.execute("""
        CREATE TRIGGER trg_usuario_status_padrao
        BEFORE INSERT ON Usuarios
        FOR EACH ROW
        BEGIN
            IF NEW.Status IS NULL THEN
                SET NEW.Status = 'ativo';
            END IF;
        END;
    """)

    # TRIGGER 3
    # Data do empréstimo

    cursor.execute("""
        CREATE TRIGGER trg_emprestimo_data
        BEFORE INSERT ON Emprestimos
        FOR EACH ROW
        BEGIN
            IF NEW.Data_emprestimo IS NULL THEN
                SET NEW.Data_emprestimo = CURDATE();
            END IF;
        END;
    """)

    # TRIGGER 4
    # Data prevista de devolução

    cursor.execute("""
        CREATE TRIGGER trg_emprestimo_data_prevista
        BEFORE INSERT ON Emprestimos
        FOR EACH ROW
        BEGIN
            IF NEW.Data_devolucao_prevista IS NULL THEN
                SET NEW.Data_devolucao_prevista = DATE_ADD(
                    COALESCE(NEW.Data_emprestimo, CURDATE()),
                    INTERVAL 7 DAY
                );
            END IF;
        END;
    """)

    # TRIGGER 5
    # Status inicial do empréstimo

    cursor.execute("""
        CREATE TRIGGER trg_emprestimo_status_padrao
        BEFORE INSERT ON Emprestimos
        FOR EACH ROW
        BEGIN
            IF NEW.Status_emprestimo IS NULL THEN
                SET NEW.Status_emprestimo = 'pendente';
            END IF;
        END;
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("Triggers criados com sucesso (todas independentes)")
