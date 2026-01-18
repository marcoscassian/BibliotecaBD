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

    # Tabela Usuarios com campo Status adicionado
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

    # Tabela de logs de auditoria
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

    # Remover triggers existentes para recriar
    triggers_para_remover = [
        'trg_usuarios_before_insert',
        'trg_usuarios_after_insert',
        'trg_usuarios_after_update',
        'trg_emprestimos_before_insert',
        'trg_emprestimos_after_insert',
        'trg_emprestimos_before_update',
        'trg_emprestimos_after_update',
        'trg_emprestimos_after_delete',
        'trg_autores_before_delete',
        'trg_livros_after_delete',
        # Triggers antigos
        'trg_validar_estoque_livro',
        'trg_log_emprestimo',
        'trg_calcular_devolucao_prevista',
        'trg_set_data_emprestimo',
        'trg_prevent_duplicate_loan',
        'trg_gerar_status_emprestimo',
        'trg_gerar_multa_atraso',
        'trg_set_data_inscricao_usuario',
        'trg_valida_usuario_ativo',
        'trg_valida_data_devolucao',
        'trg_bloqueia_exclusao_autor',
        'trg_log_usuario_insert',
        'trg_log_usuario_update',
        'trg_log_emprestimo_update',
        'trg_log_livro_delete',
        'trg_baixa_estoque_livro',
        'trg_retorna_estoque_livro',
        'trg_inativa_usuario',
        'trg_status_padrao_usuario',
        'trg_status_padrao_emprestimo'
    ]

    for trigger in triggers_para_remover:
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger};")

    cursor.execute("DROP PROCEDURE IF EXISTS registrar_log;")

    # ============================================
    # PROCEDURE DE APOIO PARA AUDITORIA
    # ============================================
    cursor.execute("""
        CREATE PROCEDURE registrar_log(
            p_tabela VARCHAR(50),
            p_operacao VARCHAR(20),
            p_usuario INT,
            p_descricao TEXT
        )
        BEGIN
            INSERT INTO logs_auditoria
            (tabela_afetada, operacao, data_operacao, usuario_afetado, descricao)
            VALUES
            (p_tabela, p_operacao, NOW(), p_usuario, p_descricao);
        END;
    """)

    # ============================================
    # TRIGGERS PARA TABELA USUARIOS
    # ============================================

    # BEFORE INSERT - Consolidado (triggers 16 e 17)
    # - Define data de inscrição automaticamente
    # - Define status inicial como 'ativo'
    cursor.execute("""
        CREATE TRIGGER trg_usuarios_before_insert
        BEFORE INSERT ON Usuarios
        FOR EACH ROW
        BEGIN
            -- 16: Definir data de inscrição do usuário
            IF NEW.Data_inscricao IS NULL THEN
                SET NEW.Data_inscricao = CURDATE();
            END IF;

            -- 17: Definir status inicial do usuário como 'ativo'
            IF NEW.Status IS NULL THEN
                SET NEW.Status = 'ativo';
            END IF;
        END;
    """)

    # AFTER INSERT - Trigger 6: Log de cadastro de usuário
    cursor.execute("""
        CREATE TRIGGER trg_usuarios_after_insert
        AFTER INSERT ON Usuarios
        FOR EACH ROW
        BEGIN
            CALL registrar_log(
                'usuarios',
                'INSERT',
                NEW.ID_usuario,
                CONCAT('Novo usuário cadastrado: ', NEW.Nome_usuario)
            );
        END;
    """)

    # AFTER UPDATE - Trigger 7: Log de alteração de usuário
    cursor.execute("""
        CREATE TRIGGER trg_usuarios_after_update
        AFTER UPDATE ON Usuarios
        FOR EACH ROW
        BEGIN
            CALL registrar_log(
                'usuarios',
                'UPDATE',
                NEW.ID_usuario,
                CONCAT('Dados do usuário alterados: ', NEW.Nome_usuario)
            );
        END;
    """)

    # ============================================
    # TRIGGERS PARA TABELA EMPRESTIMOS
    # ============================================

    # BEFORE INSERT - Consolidado (triggers 1, 2, 3, 18, 19, 20)
    # - Valida usuário ativo
    # - Valida empréstimo duplicado
    # - Valida estoque do livro
    # - Define data do empréstimo
    # - Define data prevista de devolução
    # - Define status inicial
    cursor.execute("""
        CREATE TRIGGER trg_emprestimos_before_insert
        BEFORE INSERT ON Emprestimos
        FOR EACH ROW
        BEGIN
            DECLARE user_status VARCHAR(10);
            DECLARE qtd_disponivel INT;
            DECLARE emprestimo_existente INT;

            -- 1: Impedir empréstimo para usuário inativo
            SELECT Status INTO user_status
            FROM Usuarios
            WHERE ID_usuario = NEW.Usuario_id;

            IF user_status IS NULL OR user_status <> 'ativo' THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Usuário inativo não pode realizar empréstimos';
            END IF;

            -- 2: Impedir empréstimo duplicado do mesmo livro
            SELECT COUNT(*) INTO emprestimo_existente
            FROM Emprestimos
            WHERE Usuario_id = NEW.Usuario_id
            AND Livro_id = NEW.Livro_id
            AND Status_emprestimo != 'devolvido';

            IF emprestimo_existente > 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Empréstimo duplicado: usuário já possui empréstimo ativo para este livro';
            END IF;

            -- 3: Bloquear empréstimo sem estoque
            SELECT Quantidade_disponivel INTO qtd_disponivel
            FROM Livros
            WHERE ID_livro = NEW.Livro_id;

            IF qtd_disponivel IS NULL OR qtd_disponivel <= 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Livro indisponível para empréstimo - sem estoque';
            END IF;

            -- 18: Definir data do empréstimo
            IF NEW.Data_emprestimo IS NULL THEN
                SET NEW.Data_emprestimo = CURDATE();
            END IF;

            -- 19: Definir data prevista de devolução (7 dias após empréstimo)
            IF NEW.Data_devolucao_prevista IS NULL THEN
                SET NEW.Data_devolucao_prevista = DATE_ADD(
                    COALESCE(NEW.Data_emprestimo, CURDATE()),
                    INTERVAL 7 DAY
                );
            END IF;

            -- 20: Gerar status inicial do empréstimo como 'pendente'
            IF NEW.Status_emprestimo IS NULL THEN
                SET NEW.Status_emprestimo = 'pendente';
            END IF;
        END;
    """)

    # AFTER INSERT - Consolidado (triggers 8 e 11)
    # - Log de novo empréstimo
    # - Atualizar estoque ao emprestar livro
    cursor.execute("""
        CREATE TRIGGER trg_emprestimos_after_insert
        AFTER INSERT ON Emprestimos
        FOR EACH ROW
        BEGIN
            DECLARE nome_livro VARCHAR(255);

            -- Obter nome do livro para o log
            SELECT Titulo INTO nome_livro
            FROM Livros
            WHERE ID_livro = NEW.Livro_id;

            -- 8: Log de novo empréstimo
            CALL registrar_log(
                'emprestimos',
                'INSERT',
                NEW.Usuario_id,
                CONCAT('Empréstimo realizado do livro "', nome_livro, '"')
            );

            -- 11: Atualizar estoque ao emprestar livro (baixa)
            UPDATE Livros
            SET Quantidade_disponivel = Quantidade_disponivel - 1
            WHERE ID_livro = NEW.Livro_id;
        END;
    """)

    # BEFORE UPDATE - Consolidado (triggers 4 e 15)
    # - Impedir devolução antes do empréstimo
    # - Atualizar status do empréstimo automaticamente
    cursor.execute("""
        CREATE TRIGGER trg_emprestimos_before_update
        BEFORE UPDATE ON Emprestimos
        FOR EACH ROW
        BEGIN
            -- 4: Impedir devolução antes do empréstimo
            IF NEW.Data_devolucao_real IS NOT NULL
               AND NEW.Data_devolucao_real < OLD.Data_emprestimo THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Data de devolução não pode ser anterior à data do empréstimo';
            END IF;

            -- 15: Atualizar status do empréstimo automaticamente
            IF NEW.Data_devolucao_real IS NOT NULL THEN
                SET NEW.Status_emprestimo = 'devolvido';
            ELSEIF NEW.Data_devolucao_prevista < CURDATE() THEN
                SET NEW.Status_emprestimo = 'atrasado';
            ELSE
                SET NEW.Status_emprestimo = 'pendente';
            END IF;
        END;
    """)

    # AFTER UPDATE - Consolidado (triggers 9, 12 e 14)
    # - Log de devolução de livro
    # - Atualizar estoque ao devolver livro
    # - Calcular multa por atraso
    cursor.execute("""
        CREATE TRIGGER trg_emprestimos_after_update
        AFTER UPDATE ON Emprestimos
        FOR EACH ROW
        BEGIN
            DECLARE nome_livro VARCHAR(255);
            DECLARE dias_atraso INT;
            DECLARE valor_multa DECIMAL(10,2);

            -- Verificar se é uma devolução (data_devolucao_real foi preenchida)
            IF OLD.Data_devolucao_real IS NULL AND NEW.Data_devolucao_real IS NOT NULL THEN

                -- Obter nome do livro para o log
                SELECT Titulo INTO nome_livro
                FROM Livros
                WHERE ID_livro = NEW.Livro_id;

                -- 9: Log de devolução de livro
                CALL registrar_log(
                    'emprestimos',
                    'UPDATE',
                    NEW.Usuario_id,
                    CONCAT('Livro devolvido: "', nome_livro, '"')
                );

                -- 12: Atualizar estoque ao devolver livro
                UPDATE Livros
                SET Quantidade_disponivel = Quantidade_disponivel + 1
                WHERE ID_livro = NEW.Livro_id;

                -- 14: Calcular multa por atraso
                IF NEW.Data_devolucao_real > NEW.Data_devolucao_prevista THEN
                    SET dias_atraso = DATEDIFF(
                        NEW.Data_devolucao_real,
                        NEW.Data_devolucao_prevista
                    );
                    SET valor_multa = dias_atraso * 2.00;

                    UPDATE Usuarios
                    SET Multa_atual = Multa_atual + valor_multa
                    WHERE ID_usuario = NEW.Usuario_id;
                END IF;
            END IF;
        END;
    """)

    # AFTER DELETE - Trigger 13: Inativar usuário sem empréstimos
    cursor.execute("""
        CREATE TRIGGER trg_emprestimos_after_delete
        AFTER DELETE ON Emprestimos
        FOR EACH ROW
        BEGIN
            DECLARE qtd_emprestimos INT;

            SELECT COUNT(*) INTO qtd_emprestimos
            FROM Emprestimos
            WHERE Usuario_id = OLD.Usuario_id;

            IF qtd_emprestimos = 0 THEN
                UPDATE Usuarios SET Status = 'inativo'
                WHERE ID_usuario = OLD.Usuario_id;
            END IF;
        END;
    """)

    # ============================================
    # TRIGGERS PARA TABELA AUTORES
    # ============================================

    # BEFORE DELETE - Trigger 5: Bloquear exclusão de autor com livros cadastrados
    cursor.execute("""
        CREATE TRIGGER trg_autores_before_delete
        BEFORE DELETE ON Autores
        FOR EACH ROW
        BEGIN
            DECLARE qtd_livros INT;

            SELECT COUNT(*) INTO qtd_livros
            FROM Livros
            WHERE Autor_id = OLD.ID_autor;

            IF qtd_livros > 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Não é possível excluir autor com livros cadastrados';
            END IF;
        END;
    """)

    # ============================================
    # TRIGGERS PARA TABELA LIVROS
    # ============================================

    # AFTER DELETE - Trigger 10: Log de exclusão de livro
    cursor.execute("""
        CREATE TRIGGER trg_livros_after_delete
        AFTER DELETE ON Livros
        FOR EACH ROW
        BEGIN
            CALL registrar_log(
                'livros',
                'DELETE',
                NULL,
                CONCAT('Livro removido do sistema: "', OLD.Titulo, '"')
            );
        END;
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("Triggers criados com sucesso (20 funcionalidades em 10 triggers consolidados)")
    print("")
    print("RESUMO DOS TRIGGERS:")
    print("=" * 60)
    print("")
    print("VALIDACOES:")
    print("  1. Impedir empréstimo para usuário inativo")
    print("  2. Impedir empréstimo duplicado do mesmo livro")
    print("  3. Bloquear empréstimo sem estoque")
    print("  4. Impedir devolução antes do empréstimo")
    print("  5. Bloquear exclusão de autor com livros")
    print("")
    print("AUDITORIA:")
    print("  6. Log de cadastro de usuário")
    print("  7. Log de alteração de usuário")
    print("  8. Log de novo empréstimo")
    print("  9. Log de devolução de livro")
    print(" 10. Log de exclusão de livro")
    print("")
    print("ATUALIZACAO AUTOMATICA:")
    print(" 11. Baixa de estoque ao emprestar")
    print(" 12. Retorno de estoque ao devolver")
    print(" 13. Inativar usuário sem empréstimos")
    print(" 14. Calcular multa por atraso (R$ 2,00/dia)")
    print(" 15. Atualizar status do empréstimo")
    print("")
    print("GERACAO AUTOMATICA:")
    print(" 16. Data de inscrição do usuário")
    print(" 17. Status inicial do usuário (ativo)")
    print(" 18. Data do empréstimo")
    print(" 19. Data prevista de devolução (7 dias)")
    print(" 20. Status inicial do empréstimo (pendente)")
    print("")
    print("=" * 60)


# Executar criação
criar_tabelas()
criar_triggers()
