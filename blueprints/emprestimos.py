
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection
import mysql.connector
emprestimos_bp = Blueprint("emprestimos", __name__, url_prefix="/emprestimos")

@emprestimos_bp.route("/")
def listar_emprestimos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    sql = (
        "select E.ID_emprestimo, U.Nome_usuario, L.Titulo, "
        "E.Data_emprestimo, E.Data_devolucao_prevista, "
        "E.Data_devolucao_real, E.Status_emprestimo "
        "from Emprestimos E "
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
    cur.execute("select ID_usuario, Nome_usuario from Usuarios ORDER BY Nome_usuario")
    usuarios = cur.fetchall()
    cur.execute("select ID_livro, Titulo from Livros ORDER BY Titulo")
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
            "insert into emprestimos "
            "(usuario_id, livro_id, data_emprestimo, data_devolucao_prevista, "
            "data_devolucao_real, status_emprestimo) "
            "values (%s, %s, %s, %s, %s, %s)"
        )

        cur = conn.cursor()

        try:
            cur.execute(sql, (usuario_id, livro_id, data_emp, data_prev, data_real, status))
            conn.commit()
            flash("Empréstimo cadastrado com sucesso!", "success")
            return redirect(url_for("emprestimos.listar_emprestimos"))

        except mysql.connector.Error as err:
            print(err)
            print(err.msg)
            print(err.errno)
            conn.rollback()

            if "livro indisponível para empréstimo" in str(err):
                flash("Este livro não possui estoque disponível.", "danger")
            else:
                flash("Erro ao cadastrar empréstimo.", "danger")

            return redirect(url_for("emprestimos.novo_emprestimo"))

        finally:
            cur.close()
            conn.close()

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
            "where ID_emprestimo=%s"
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

    cur.execute("select * from Emprestimos where ID_emprestimo=%s", (id_emprestimo,))
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
    cur.execute("delete from Emprestimos where ID_emprestimo=%s", (id_emprestimo,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Empréstimo excluído com sucesso!", "success")
    return redirect(url_for("emprestimos.listar_emprestimos"))
