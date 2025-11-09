
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

livros_bp = Blueprint("livros", __name__, url_prefix="/livros")

@livros_bp.route("/")
def listar_livros():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    sql = (
        "SELECT L.ID_livro, L.Titulo, L.ISBN, L.Ano_publicacao, "
        "L.Quantidade_disponivel, "
        "A.Nome_autor, G.Nome_genero, E.Nome_editora "
        "FROM Livros L "
        "LEFT JOIN Autores A ON L.Autor_id = A.ID_autor "
        "LEFT JOIN Generos G ON L.Genero_id = G.ID_genero "
        "LEFT JOIN Editoras E ON L.Editora_id = E.ID_editora "
        "ORDER BY L.ID_livro"
    )
    cur.execute(sql)
    livros = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("livros_list.html", livros=livros)

def carregar_relacionamentos(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT ID_autor, Nome_autor FROM Autores ORDER BY Nome_autor")
    autores = cur.fetchall()
    cur.execute("SELECT ID_genero, Nome_genero FROM Generos ORDER BY Nome_genero")
    generos = cur.fetchall()
    cur.execute("SELECT ID_editora, Nome_editora FROM Editoras ORDER BY Nome_editora")
    editoras = cur.fetchall()
    cur.close()
    return autores, generos, editoras

@livros_bp.route("/novo", methods=["GET", "POST"])
def novo_livro():
    conn = get_connection()
    autores, generos, editoras = carregar_relacionamentos(conn)

    if request.method == "POST":
        titulo = request.form.get("Titulo")
        autor_id = request.form.get("Autor_id") or None
        isbn = request.form.get("ISBN")
        ano = request.form.get("Ano_publicacao") or None
        genero_id = request.form.get("Genero_id") or None
        editora_id = request.form.get("Editora_id") or None
        quantidade = request.form.get("Quantidade_disponivel") or 0
        resumo = request.form.get("Resumo")

        sql = (
            "INSERT INTO Livros "
            "(Titulo, Autor_id, ISBN, Ano_publicacao, Genero_id, Editora_id, "
            "Quantidade_disponivel, Resumo) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cur = conn.cursor()
        cur.execute(sql, (titulo, autor_id, isbn, ano, genero_id, editora_id, quantidade, resumo))
        conn.commit()
        cur.close()
        conn.close()
        flash("Livro cadastrado com sucesso!", "success")
        return redirect(url_for("livros.listar_livros"))

    conn.close()
    return render_template(
        "livros_form.html",
        livro=None,
        autores=autores,
        generos=generos,
        editoras=editoras,
    )

@livros_bp.route("/editar/<int:id_livro>", methods=["GET", "POST"])
def editar_livro(id_livro):
    conn = get_connection()
    autores, generos, editoras = carregar_relacionamentos(conn)
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        titulo = request.form.get("Titulo")
        autor_id = request.form.get("Autor_id") or None
        isbn = request.form.get("ISBN")
        ano = request.form.get("Ano_publicacao") or None
        genero_id = request.form.get("Genero_id") or None
        editora_id = request.form.get("Editora_id") or None
        quantidade = request.form.get("Quantidade_disponivel") or 0
        resumo = request.form.get("Resumo")

        sql = (
            "UPDATE Livros SET Titulo=%s, Autor_id=%s, ISBN=%s, Ano_publicacao=%s, "
            "Genero_id=%s, Editora_id=%s, Quantidade_disponivel=%s, Resumo=%s "
            "WHERE ID_livro=%s"
        )
        cur2 = conn.cursor()
        cur2.execute(
            sql,
            (titulo, autor_id, isbn, ano, genero_id, editora_id, quantidade, resumo, id_livro),
        )
        conn.commit()
        cur2.close()
        cur.close()
        conn.close()
        flash("Livro atualizado com sucesso!", "success")
        return redirect(url_for("livros.listar_livros"))

    cur.execute("SELECT * FROM Livros WHERE ID_livro=%s", (id_livro,))
    livro = cur.fetchone()
    cur.close()
    conn.close()
    return render_template(
        "livros_form.html",
        livro=livro,
        autores=autores,
        generos=generos,
        editoras=editoras,
    )

@livros_bp.route("/excluir/<int:id_livro>", methods=["POST"])
def excluir_livro(id_livro):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Livros WHERE ID_livro=%s", (id_livro,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Livro excluído com sucesso!", "success")
    return redirect(url_for("livros.listar_livros"))
