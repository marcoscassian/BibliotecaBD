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
        create trigger trg_usuario_data_inscricao
        before insert ON Usuarios
        for each row
        BEGIN
            IF NEW.Data_inscricao IS NULL THEN
                SET NEW.Data_inscricao = CURDATE();
            END IF;
        END;
    """)

    # TRIGGER 2
    # Status inicial do usuário

    cursor.execute("""
        create trigger trg_usuario_status_padrao
        before insert ON Usuarios
        for each row
        BEGIN
            IF NEW.Status IS NULL THEN
                SET NEW.Status = 'ativo';
            END IF;
        END;
    """)

    # TRIGGER 3
    # Data do empréstimo

    cursor.execute("""
        create trigger trg_emprestimo_data
        before insert ON Emprestimos
        for each row
        BEGIN
            IF NEW.Data_emprestimo IS NULL THEN
                SET NEW.Data_emprestimo = CURDATE();
            END IF;
        END;
    """)

    # TRIGGER 4
    # Data prevista de devolução

    cursor.execute("""
        create trigger trg_emprestimo_data_prevista
        before insert ON Emprestimos
        for each row
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
        create trigger trg_emprestimo_status_padrao
        before insert ON Emprestimos
        for each row
        BEGIN
            IF NEW.Status_emprestimo IS NULL THEN
                SET NEW.Status_emprestimo = 'pendente';
            END IF;
        END;
    """)


    #TRIGGER 6
    #log de cadastro de usuário
    cursor.execute("""
        create trigger log_insert_usuario
        AFTER INSERT ON Usuarios
        for each row
        BEGIN
            INSERT INTO logs_auditoria
            (tabela_afetada, operacao, data_operacao, usuario_afetado, descricao)
            VALUES
            ('Usuarios', 'Insert', NOW(), NEW.ID_usuario,
            CONCAT('Novo Usuário Cadastrado: ', NEW.Nome_usuario));
        END;
    """)
    # TRIGGER 7
    # log de atualizacao de nome do usuario
    cursor.execute("""
        create trigger log_update_usuario
        AFTER UPDATE ON Usuarios
        for each row
        BEGIN
            IF OLD.Nome_usuario != NEW.Nome_usuario THEN
                INSERT INTO logs_auditoria
                (tabela_afetada, operacao, data_operacao, usuario_afetado, descricao)
                VALUES
                ('Usuarios', 'Update', NOW(), NEW.ID_usuario,
                CONCAT(
                    'Nome alterado de "', OLD.Nome_usuario,
                    '" para "', NEW.Nome_usuario, '"'
                ));
            END IF;
        END;
    """)

    # TRIGGER 8
    # log de criacao de emprestimo
    cursor.execute("""
        create trigger log_insert_emprestimo
        AFTER INSERT ON Emprestimos
        for each row
        BEGIN
            INSERT INTO logs_auditoria
            (tabela_afetada, operacao, data_operacao, usuario_afetado, descricao)
            VALUES
            ('Emprestimos', 'Insert', NOW(), NEW.Usuario_id,
            CONCAT(
                'Emprestimo criado  ',
                ' | Data: ',
                NEW.Data_emprestimo
            ));
        END;
    """)

    # TRIGGER 9
    # log de atualizacao do status do emprestimo
    cursor.execute("""
        create trigger log_update_emprestimo
        AFTER UPDATE ON Emprestimos
        for each row
        BEGIN
            IF OLD.Status_emprestimo != NEW.Status_emprestimo THEN
                INSERT INTO logs_auditoria
                (tabela_afetada, operacao, data_operacao, usuario_afetado, descricao)
                VALUES
                ('Emprestimos', 'Update', NOW(), NEW.Usuario_id,
                CONCAT(
                    'Status do emprestimo alterado de ',
                    OLD.Status_emprestimo,
                    ' para ',
                    NEW.Status_emprestimo
                ));
            END IF;
        END;
    """)

    # TRIGGER 10
    # log de exclusao de livro
    cursor.execute("""
        create trigger log_delete_livro
        AFTER DELETE ON Livros
        for each row
        BEGIN
            INSERT INTO logs_auditoria
            (tabela_afetada, operacao, data_operacao, usuario_afetado, descricao)
            VALUES
            ('Livros', 'Delete', NOW(), NULL,
            CONCAT(
                'Livro removido: ',
                OLD.Titulo,
                ' (ID ',
                OLD.ID_livro,
                ')'
            ));
        END;
    """)

    # Trigger 11
    # Data de inscrição automática do usuário
    cursor.execute("""
    create trigger trg_val_usuario_data_inscricao
    before insert on usuarios
    for each row
    begin
        if new.data_inscricao is null then
            signal sqlstate '45000'
                set message_text = 'data_inscricao obrigatoria';
        end if;
    end
    """)

    #Trigger 12
    # Status inicial do usuário (se vier NULL)
    cursor.execute("""
    create trigger trg_val_usuario_status
    before insert on usuarios
    for each row
    begin
        if new.status is null then
            signal sqlstate '45000'
                set message_text = 'status do usuario obrigatorio';
        end if;

        if new.status not in ('ativo', 'inativo') then
            signal sqlstate '45000'
                set message_text = 'status do usuario invalido';
        end if;
    end
    """)

    # TRIGGER 13
    # Rmpréstimo: setar data_emprestimo + data_devolucao_prevista + status (tudo em 1)
    
    cursor.execute("""
    create trigger trg_val_emprestimo_dados_obrigatorios
    before insert on emprestimos
    for each row
    begin
        if new.data_emprestimo is null then
            signal sqlstate '45000'
                set message_text = 'data_emprestimo obrigatoria';
        end if;

        if new.data_devolucao_prevista is null then
            signal sqlstate '45000'
                set message_text = 'data_devolucao_prevista obrigatoria';
        end if;

        if new.status_emprestimo is null then
            signal sqlstate '45000'
                set message_text = 'status_emprestimo obrigatorio';
        end if;

        if new.status_emprestimo not in ('pendente', 'devolvido', 'atrasado') then
            signal sqlstate '45000'
                set message_text = 'status_emprestimo invalido';
        end if;
    end
    """)
    
    #Trigger 14
    # Bloquear empréstimo se o usuário estiver inativo
    cursor.execute("""
    create trigger trg_val_emprestimo_usuario_ativo
    before insert ON Emprestimos
    for each row
    begin
        DECLARE v_status VARCHAR(10);

        SELECT Status
        INTO v_status
        FROM Usuarios
        WHERE ID_usuario = NEW.Usuario_id;

        IF v_status IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Usuário informado não existe.';
        END IF;

        IF v_status = 'inativo' THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Validação falhou: usuário inativo não pode realizar empréstimos.';
        END IF;
    END
    """)
    
    # TRIGGER 15
    # Bloquear empréstimo se não houver estoque disponível do livro
    cursor.execute("""
    CREATE TRIGGER trg_val_emprestimo_livro_com_estoque
    BEFORE INSERT ON Emprestimos
    FOR EACH ROW
    BEGIN
        DECLARE v_qtd INT;

        SELECT Quantidade_disponivel
        INTO v_qtd
        FROM Livros
        WHERE ID_livro = NEW.Livro_id;

        IF v_qtd IS NULL THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Livro informado não existe.';
        END IF;

        IF v_qtd <= 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Validação falhou: livro sem estoque disponível.';
        END IF;
    END
    """)
    
    conn.commit() 
    cursor.close() 
    conn.close() 
    print("Triggers criados com sucesso (todas independentes)")