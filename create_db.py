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
        create table if not exists emprestimos (
            id_emprestimo int auto_increment primary key,
            usuario_id int not null,
            livro_id int not null,
            data_emprestimo date not null,
            data_devolucao_prevista date,
            data_devolucao_real date,
            status_emprestimo enum('pendente', 'devolvido', 'atrasado') default 'pendente',

            foreign key (usuario_id) references usuarios(id_usuario)
                on delete restrict on update cascade,

            foreign key (livro_id) references livros(id_livro)
                on delete restrict on update cascade
        );
    """)

def criar_triggers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    create table if not exists logs_auditoria (
        id_log int auto_increment primary key,
        tabela_afetada varchar(50),
        operacao varchar(20),
        data_operacao datetime,
        usuario_afetado int,
        descricao text
    );
    """)

    cursor.execute("drop trigger if exists trg_validar_estoque_livro;")
    cursor.execute("drop trigger if exists trg_log_emprestimo;")
    cursor.execute("drop trigger if exists trg_calcular_devolucao_prevista;")
    cursor.execute("drop procedure if exists registrar_log;")


    cursor.execute("""
    create procedure registrar_log(
        p_tabela varchar(50),
        p_operacao varchar(20),
        p_usuario int,
        p_descricao text
    )
    begin
        insert into logs_auditoria
        (tabela_afetada, operacao, data_operacao, usuario_afetado, descricao)
        values
        (p_tabela, p_operacao, now(), p_usuario, p_descricao);
    end;
    """)


    cursor.execute("""
    create trigger trg_validar_estoque_livro
    before insert on emprestimos
    for each row
    begin
        declare qtd int;

        select quantidade_disponivel
        into qtd
        from livros
        where id_livro = new.livro_id;

        if qtd <= 0 then
            signal sqlstate '45000'
            set message_text = 'livro indisponível para empréstimo';
        end if;
    end;
    """)

 
    cursor.execute("""
    create trigger trg_log_emprestimo
    after insert on emprestimos
    for each row
    begin
        declare nome_livro varchar(255);

        select titulo
        into nome_livro
        from livros
        where id_livro = new.livro_id;

        call registrar_log(
            'emprestimo',
            'inserido',
            new.usuario_id,
            concat('emprestimo realizado do livro "', nome_livro, '"')
        );
    end;

    """)

    cursor.execute("""
    create trigger trg_calcular_devolucao_prevista
    before insert on emprestimos
    for each row
    begin
        set new.data_devolucao_prevista = date_add(new.data_emprestimo, interval 1 month);
    end;
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✓ criados com sucesso")

