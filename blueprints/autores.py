
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

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
        sql = (
            "INSERT INTO Autores (Nome_autor, Nacionalidade, Data_nascimento, Biografia) "
            "VALUES (%s, %s, %s, %s)"
        )
        cur.execute(sql, (nome, nacionalidade, data_nasc, biografia))
        conn.commit()
        cur.close()
        conn.close()
        flash("Autor cadastrado com sucesso!", "success")
        return redirect(url_for("autores.listar_autores"))

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

        sql = (
            "UPDATE Autores "
            "SET Nome_autor=%s, Nacionalidade=%s, Data_nascimento=%s, Biografia=%s "
            "WHERE ID_autor=%s"
        )
        cur.execute(sql, (nome, nacionalidade, data_nasc, biografia, id_autor))
        conn.commit()
        cur.close()
        conn.close()
        flash("Autor atualizado com sucesso!", "success")
        return redirect(url_for("autores.listar_autores"))

    cur.execute("SELECT * FROM Autores WHERE ID_autor = %s", (id_autor,))
    autor = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("autores_form.html", autor=autor)

@autores_bp.route("/excluir/<int:id_autor>", methods=["POST"])
def excluir_autor(id_autor):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Autores WHERE ID_autor = %s", (id_autor,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Autor excluído com sucesso!", "success")
    return redirect(url_for("autores.listar_autores"))
