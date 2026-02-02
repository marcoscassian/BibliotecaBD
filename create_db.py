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
    create trigger trg_val_usuario_email_formato
    before insert on usuarios
    for each row
    begin
        if new.email is null or trim(new.email) = '' then
            signal sqlstate '45000'
                set message_text = 'email obrigatorio';
        end if;

        if new.email not like '%_@_%._%' then
            signal sqlstate '45000'
                set message_text = 'email em formato invalido';
        end if;
    end
    """)

    #Trigger 12
    # Status inicial do usuário (se vier NULL)
    cursor.execute("""
    create trigger trg_val_usuario_multa_nao_negativa
    before insert on usuarios
    for each row
    begin
        if new.multa_atual is not null and new.multa_atual < 0 then
            signal sqlstate '45000'
                set message_text = 'multa_atual nao pode ser negativa';
        end if;
    end
    """)


    # TRIGGER 13
    # Rmpréstimo: setar data_emprestimo + data_devolucao_prevista + status (tudo em 1)
    
    cursor.execute("""
    create trigger trg_val_emprestimo_datas_consistentes
    before insert on emprestimos
    for each row
    begin
        if new.data_devolucao_prevista is not null and new.data_emprestimo is not null then
            if new.data_devolucao_prevista < new.data_emprestimo then
                signal sqlstate '45000'
                    set message_text = 'data_devolucao_prevista nao pode ser menor que data_emprestimo';
            end if;
        end if;

        if new.data_devolucao_real is not null and new.data_emprestimo is not null then
            if new.data_devolucao_real < new.data_emprestimo then
                signal sqlstate '45000'
                    set message_text = 'data_devolucao_real nao pode ser menor que data_emprestimo';
            end if;
        end if;
    end
    """)

    
    #Trigger 14
    # Bloquear empréstimo se o usuário estiver inativo
    cursor.execute("""
    create trigger trg_val_emprestimo_sem_duplicidade_pendente
    before insert on emprestimos
    for each row
    begin
        if exists (
            select 1
            from emprestimos e
            where e.usuario_id = new.usuario_id
                and e.livro_id = new.livro_id
                and e.status_emprestimo in ('pendente', 'atrasado')
                and e.data_devolucao_real is null
        ) then
            signal sqlstate '45000'
                set message_text = 'emprestimo duplicado: usuario ja possui este livro pendente/atrasado';
        end if;
    end
    """)

    # TRIGGER 15
    # Bloquear empréstimo se não houver estoque disponível do livro
    cursor.execute("""
    create trigger trg_val_emprestimo_usuario_apto
    before insert on emprestimos
    for each row
    begin
        declare v_status varchar(10);
        declare v_multa decimal(10,2);

        select status, multa_atual
            into v_status, v_multa
        from usuarios
        where id_usuario = new.usuario_id;

        if v_status is null then
            signal sqlstate '45000'
                set message_text = 'usuario informado nao existe';
        end if;

        if v_status = 'inativo' then
            signal sqlstate '45000'
                set message_text = 'emprestimo bloqueado: usuario inativo';
        end if;

        if v_multa is not null and v_multa > 0 then
            signal sqlstate '45000'
                set message_text = 'emprestimo bloqueado: usuario com multa pendente';
        end if;
    end
    """)


    # TRIGGER 16
    # Atualizar estoque de livros após empréstimo e devolução
    cursor.execute("""
    CREATE TRIGGER trg_baixa_estoque_emprestimo
    AFTER INSERT ON Emprestimos
    FOR EACH ROW
    BEGIN
        UPDATE Livros
        SET Quantidade_disponivel = Quantidade_disponivel - 1
        WHERE ID_livro = NEW.Livro_id;
    END;
    """)

    # TRIGGER 17
    # Atualizar estoque de livros após devolução
    cursor.execute("""
    CREATE TRIGGER trg_retorno_estoque_devolucao
    AFTER UPDATE ON Emprestimos
    FOR EACH ROW
    BEGIN
        IF OLD.Data_devolucao_real IS NULL
            AND NEW.Data_devolucao_real IS NOT NULL THEN
            UPDATE Livros
            SET Quantidade_disponivel = Quantidade_disponivel + 1
            WHERE ID_livro = NEW.Livro_id;

        END IF;
    END;
    """)

    # TRIGGER 18
    # Inativar usuário sem empréstimos pendentes ou atrasados
    cursor.execute("""
    CREATE TRIGGER trg_inativar_usuario_sem_emprestimo
    AFTER UPDATE ON Emprestimos
    FOR EACH ROW
    BEGIN
        IF NEW.Status_emprestimo = 'devolvido' THEN
            IF NOT EXISTS (
                SELECT 1
                FROM Emprestimos
                WHERE Usuario_id = NEW.Usuario_id
                  AND Status_emprestimo IN ('pendente', 'atrasado')
            ) THEN
                UPDATE Usuarios
                SET Status = 'inativo'
                WHERE ID_usuario = NEW.Usuario_id;
            END IF;

        END IF;
    END;
    """)

    # TRIGGER 19
    # Calcular multa por atraso na devolução
    cursor.execute("""
    CREATE TRIGGER trg_calcular_multa_atraso
    AFTER UPDATE ON Emprestimos
    FOR EACH ROW
    BEGIN
        DECLARE dias_atraso INT;
        IF NEW.Data_devolucao_real IS NOT NULL
           AND NEW.Data_devolucao_real > NEW.Data_devolucao_prevista THEN
            SET dias_atraso = DATEDIFF(
                NEW.Data_devolucao_real,
                NEW.Data_devolucao_prevista
            );
            UPDATE Usuarios
            SET Multa_atual = Multa_atual + (dias_atraso * 2)
            WHERE ID_usuario = NEW.Usuario_id;
        END IF;
    END;
    """)

    # TRIGGER 20
    # Atualizar status do empréstimo com base nas datas de devolução
    cursor.execute("""
    CREATE TRIGGER trg_atualizar_status_emprestimo
    BEFORE UPDATE ON Emprestimos
    FOR EACH ROW
    BEGIN
        IF NEW.Data_devolucao_real IS NOT NULL THEN
            SET NEW.Status_emprestimo = 'devolvido';
        ELSEIF CURDATE() > NEW.Data_devolucao_prevista THEN
            SET NEW.Status_emprestimo = 'atrasado';
        ELSE
            SET NEW.Status_emprestimo = 'pendente';
        END IF;
    END;
    """)


    
    conn.commit() 
    cursor.close() 
    conn.close() 
    print("Triggers criados com sucesso (todas independentes)")