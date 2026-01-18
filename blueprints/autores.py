from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection
import mysql.connector

autores_bp = Blueprint("autores", __name__, url_prefix="/autores")

@autores_bp.route("/")
def listar_autores():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Autores ORDER BY ID_autor")
    autores = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("autores_list.html", autores=autores)

@autores_bp.route("/novo", methods=["GET", "POST"])
def novo_autor():
    if request.method == "POST":
        nome = request.form.get("Nome_autor")
        nacionalidade = request.form.get("Nacionalidade")
        data_nasc = request.form.get("Data_nascimento") or None
        biografia = request.form.get("Biografia")

        conn = get_connection()
        cur = conn.cursor()

        try:
            sql = (
                "INSERT INTO Autores (Nome_autor, Nacionalidade, Data_nascimento, Biografia) "
                "VALUES (%s, %s, %s, %s)"
            )
            cur.execute(sql, (nome, nacionalidade, data_nasc, biografia))
            conn.commit()
            flash("Autor cadastrado com sucesso!", "success")
            return redirect(url_for("autores.listar_autores"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao cadastrar autor: {err}", "danger")
            return redirect(url_for("autores.novo_autor"))

        finally:
            cur.close()
            conn.close()

    return render_template("autores_form.html", autor=None)

@autores_bp.route("/editar/<int:id_autor>", methods=["GET", "POST"])
def editar_autor(id_autor):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form.get("Nome_autor")
        nacionalidade = request.form.get("Nacionalidade")
        data_nasc = request.form.get("Data_nascimento") or None
        biografia = request.form.get("Biografia")

        try:
            sql = (
                "UPDATE Autores "
                "SET Nome_autor=%s, Nacionalidade=%s, Data_nascimento=%s, Biografia=%s "
                "WHERE ID_autor=%s"
            )
            cur.execute(sql, (nome, nacionalidade, data_nasc, biografia, id_autor))
            conn.commit()
            flash("Autor atualizado com sucesso!", "success")
            return redirect(url_for("autores.listar_autores"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao atualizar autor: {err}", "danger")
            return redirect(url_for("autores.editar_autor", id_autor=id_autor))

        finally:
            cur.close()
            conn.close()

    cur.execute("SELECT * FROM Autores WHERE ID_autor = %s", (id_autor,))
    autor = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("autores_form.html", autor=autor)

@autores_bp.route("/excluir/<int:id_autor>", methods=["POST"])
def excluir_autor(id_autor):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # O trigger trg_bloqueia_exclusao_autor vai impedir a exclusão
        # se houver livros cadastrados para este autor
        cur.execute("DELETE FROM Autores WHERE ID_autor = %s", (id_autor,))
        conn.commit()
        flash("Autor excluído com sucesso!", "success")

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err.msg).lower() if hasattr(err, 'msg') else str(err).lower()

        # Tratamento do erro do trigger
        if "livros cadastrados" in error_msg or "não é possível excluir" in error_msg:
            flash("Não é possível excluir este autor porque existem livros cadastrados para ele.", "warning")
        elif "foreign key" in error_msg or "constraint" in error_msg:
            flash("Não é possível excluir este autor porque existem livros associados a ele.", "warning")
        else:
            flash(f"Erro ao excluir autor: {err}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("autores.listar_autores"))
