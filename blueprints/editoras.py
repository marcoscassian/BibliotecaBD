
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

editoras_bp = Blueprint("editoras", __name__, url_prefix="/editoras")

@editoras_bp.route("/")
def listar_editoras():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Editoras ORDER BY ID_editora")
    editoras = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("editoras_list.html", editoras=editoras)

@editoras_bp.route("/novo", methods=["GET", "POST"])
def nova_editora():
    if request.method == "POST":
        nome = request.form.get("Nome_editora")
        endereco = request.form.get("Endereco_editora")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO Editoras (Nome_editora, Endereco_editora) VALUES (%s, %s)",
            (nome, endereco),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Editora cadastrada com sucesso!", "success")
        return redirect(url_for("editoras.listar_editoras"))

    return render_template("editoras_form.html", editora=None)

@editoras_bp.route("/editar/<int:id_editora>", methods=["GET", "POST"])
def editar_editora(id_editora):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form.get("Nome_editora")
        endereco = request.form.get("Endereco_editora")
        cur.execute(
            "UPDATE Editoras SET Nome_editora=%s, Endereco_editora=%s WHERE ID_editora=%s",
            (nome, endereco, id_editora),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Editora atualizada com sucesso!", "success")
        return redirect(url_for("editoras.listar_editoras"))

    cur.execute("SELECT * FROM Editoras WHERE ID_editora=%s", (id_editora,))
    editora = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("editoras_form.html", editora=editora)

@editoras_bp.route("/excluir/<int:id_editora>", methods=["POST"])
def excluir_editora(id_editora):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Editoras WHERE ID_editora=%s", (id_editora,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Editora excluída com sucesso!", "success")
    return redirect(url_for("editoras.listar_editoras"))
