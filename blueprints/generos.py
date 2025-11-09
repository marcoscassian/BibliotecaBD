
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

generos_bp = Blueprint("generos", __name__, url_prefix="/generos")

@generos_bp.route("/")
def listar_generos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Generos ORDER BY ID_genero")
    generos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("generos_list.html", generos=generos)

@generos_bp.route("/novo", methods=["GET", "POST"])
def novo_genero():
    if request.method == "POST":
        nome = request.form.get("Nome_genero")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Generos (Nome_genero) VALUES (%s)", (nome,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Gênero cadastrado com sucesso!", "success")
        return redirect(url_for("generos.listar_generos"))

    return render_template("generos_form.html", genero=None)

@generos_bp.route("/editar/<int:id_genero>", methods=["GET", "POST"])
def editar_genero(id_genero):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form.get("Nome_genero")
        cur.execute("UPDATE Generos SET Nome_genero=%s WHERE ID_genero=%s", (nome, id_genero))
        conn.commit()
        cur.close()
        conn.close()
        flash("Gênero atualizado com sucesso!", "success")
        return redirect(url_for("generos.listar_generos"))

    cur.execute("SELECT * FROM Generos WHERE ID_genero=%s", (id_genero,))
    genero = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("generos_form.html", genero=genero)

@generos_bp.route("/excluir/<int:id_genero>", methods=["POST"])
def excluir_genero(id_genero):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Generos WHERE ID_genero = %s", (id_genero,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Gênero excluído com sucesso!", "success")
    return redirect(url_for("generos.listar_generos"))
