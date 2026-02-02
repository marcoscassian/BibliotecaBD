from db import get_connection


def inserir_dados_iniciais():
    """Insere dados iniciais de forma idempotente: verifica se já existem registros e, se não, insere amostras."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        #verifica se já existem autores (idempotência)
        cursor.execute("SELECT COUNT(*) FROM Autores")
        if cursor.fetchone()[0] > 0:
            print("Dados iniciais já presentes. Pulando inserção.")
            return

        #inserir Autores
        autores = [
            ("J.K. Rowling", "Reino Unido", "1965-07-31", "Autora de fantasia."),
            ("George Orwell", "Reino Unido", "1903-06-25", "Autor de distopias."),
            ("Gabriel García Márquez", "Colômbia", "1927-03-06", "Realismo mágico.")
        ]

        cursor.executemany(
            "INSERT INTO Autores (Nome_autor, Nacionalidade, Data_nascimento, Biografia) VALUES (%s, %s, %s, %s)",
            autores
        )

        #inserir Gêneros
        generos = [("Fantasia",), ("Distopia",), ("Realismo Mágico",), ("Ficção Científica",)]
        cursor.executemany("INSERT INTO Generos (Nome_genero) VALUES (%s)", generos)

        #inserir Editoras
        editoras = [("Editora A", "Rua A, 123"), ("Editora B", "Rua B, 456")]
        cursor.executemany("INSERT INTO Editoras (Nome_editora, Endereco_editora) VALUES (%s, %s)", editoras)

        #inserir Usuários (garantir Data_inscricao não nula por causa de triggers de validação)
        usuarios = [
            ("Alice Silva", "alice@example.com", "1234567890", "2025-01-01", "ativo", 0.0),
            ("Bruno Souza", "bruno@example.com", "0987654321", "2025-01-05", "ativo", 0.0),
            ("Carlos Lima", "carlos@example.com", "5555555555", "2025-01-08", "ativo", 0.0)
        ]
        cursor.executemany(
            """INSERT INTO Usuarios (Nome_usuario, Email, Numero_telefone, Data_inscricao, Status, Multa_atual)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            usuarios
        )

        conn.commit()

        #preparar dados para Livros usando IDs inseridos
        cursor.execute("SELECT ID_autor FROM Autores WHERE Nome_autor = %s", ("J.K. Rowling",))
        jk_row = cursor.fetchone()
        jk_id = jk_row[0] if jk_row else None

        cursor.execute("SELECT ID_genero FROM Generos WHERE Nome_genero = %s", ("Fantasia",))
        genero_row = cursor.fetchone()
        genero_id = genero_row[0] if genero_row else None

        cursor.execute("SELECT ID_editora FROM Editoras WHERE Nome_editora = %s", ("Editora A",))
        editora_row = cursor.fetchone()
        editora_id = editora_row[0] if editora_row else None

        livros = [
            ("Harry Potter e a Pedra Filosofal", jk_id, "9780747532743", 1997, genero_id, editora_id, 3, "Primeiro livro da série Harry Potter."),
            ("1984", None, "9780451524935", 1949, genero_id + 1 if genero_id else None, editora_id + 1 if editora_id else None, 2, "Distopia clássica."),
        ]

        cursor.executemany(
            """INSERT INTO Livros (Titulo, Autor_id, ISBN, Ano_publicacao, Genero_id, Editora_id, Quantidade_disponivel, Resumo)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            livros
        )

        conn.commit()

        #inserir um empréstimo de exemplo
        cursor.execute("SELECT ID_usuario FROM Usuarios WHERE Email = %s", ("alice@example.com",))
        usuario_row = cursor.fetchone()
        usuario_id = usuario_row[0] if usuario_row else None

        cursor.execute("SELECT ID_livro FROM Livros WHERE Titulo = %s", ("Harry Potter e a Pedra Filosofal",))
        livro_row = cursor.fetchone()
        livro_id = livro_row[0] if livro_row else None

        if usuario_id and livro_id:
            cursor.execute(
                "INSERT INTO Emprestimos (Usuario_id, Livro_id, Data_emprestimo, Data_devolucao_prevista, Status_emprestimo) VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'pendente')",
                (usuario_id, livro_id)
            )
            conn.commit()

        print("Dados iniciais inseridos com sucesso")

    except Exception as e:
        conn.rollback()
        print("Erro ao inserir dados iniciais:", e)
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    inserir_dados_iniciais()
