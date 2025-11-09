
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

emprestimos_bp = Blueprint("emprestimos", __name__, url_prefix="/emprestimos")

@emprestimos_bp.route("/")
def listar_emprestimos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    sql = (
        "SELECT E.ID_emprestimo, U.Nome_usuario, L.Titulo, "
        "E.Data_emprestimo, E.Data_devolucao_prevista, "
        "E.Data_devolucao_real, E.Status_emprestimo "
        "FROM Emprestimos E "
        "JOIN Usuarios U ON E.Usuario_id = U.ID_usuario "
        "JOIN Livros L ON E.Livro_id = L.ID_livro "
        "ORDER BY E.ID_emprestimo DESC"
    )
    cur.execute(sql)
    emprestimos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("emprestimos_list.html", emprestimos=emprestimos)

def carregar_usuarios_livros(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT ID_usuario, Nome_usuario FROM Usuarios ORDER BY Nome_usuario")
    usuarios = cur.fetchall()
    cur.execute("SELECT ID_livro, Titulo FROM Livros ORDER BY Titulo")
    livros = cur.fetchall()
    cur.close()
    return usuarios, livros

@emprestimos_bp.route("/novo", methods=["GET", "POST"])
def novo_emprestimo():
    conn = get_connection()
    usuarios, livros = carregar_usuarios_livros(conn)

    if request.method == "POST":
        usuario_id = request.form.get("Usuario_id")
        livro_id = request.form.get("Livro_id")
        data_emp = request.form.get("Data_emprestimo") or None
        data_prev = request.form.get("Data_devolucao_prevista") or None
        data_real = request.form.get("Data_devolucao_real") or None
        status = request.form.get("Status_emprestimo")

        sql = (
            "INSERT INTO Emprestimos "
            "(Usuario_id, Livro_id, Data_emprestimo, Data_devolucao_prevista, "
            "Data_devolucao_real, Status_emprestimo) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        cur = conn.cursor()
        cur.execute(sql, (usuario_id, livro_id, data_emp, data_prev, data_real, status))
        conn.commit()
        cur.close()
        conn.close()
        flash("Empréstimo cadastrado com sucesso!", "success")
        return redirect(url_for("emprestimos.listar_emprestimos"))

    conn.close()
    return render_template(
        "emprestimos_form.html",
        emprestimo=None,
        usuarios=usuarios,
        livros=livros,
    )

@emprestimos_bp.route("/editar/<int:id_emprestimo>", methods=["GET", "POST"])
def editar_emprestimo(id_emprestimo):
    conn = get_connection()
    usuarios, livros = carregar_usuarios_livros(conn)
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        usuario_id = request.form.get("Usuario_id")
        livro_id = request.form.get("Livro_id")
        data_emp = request.form.get("Data_emprestimo") or None
        data_prev = request.form.get("Data_devolucao_prevista") or None
        data_real = request.form.get("Data_devolucao_real") or None
        status = request.form.get("Status_emprestimo")

        sql = (
            "UPDATE Emprestimos SET Usuario_id=%s, Livro_id=%s, "
            "Data_emprestimo=%s, Data_devolucao_prevista=%s, "
            "Data_devolucao_real=%s, Status_emprestimo=%s "
            "WHERE ID_emprestimo=%s"
        )
        cur2 = conn.cursor()
        cur2.execute(
            sql,
            (usuario_id, livro_id, data_emp, data_prev, data_real, status, id_emprestimo),
        )
        conn.commit()
        cur2.close()
        cur.close()
        conn.close()
        flash("Empréstimo atualizado com sucesso!", "success")
        return redirect(url_for("emprestimos.listar_emprestimos"))

    cur.execute("SELECT * FROM Emprestimos WHERE ID_emprestimo=%s", (id_emprestimo,))
    emprestimo = cur.fetchone()
    cur.close()
    conn.close()
    return render_template(
        "emprestimos_form.html",
        emprestimo=emprestimo,
        usuarios=usuarios,
        livros=livros,
    )

@emprestimos_bp.route("/excluir/<int:id_emprestimo>", methods=["POST"])
def excluir_emprestimo(id_emprestimo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Emprestimos WHERE ID_emprestimo=%s", (id_emprestimo,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Empréstimo excluído com sucesso!", "success")
    return redirect(url_for("emprestimos.listar_emprestimos"))
