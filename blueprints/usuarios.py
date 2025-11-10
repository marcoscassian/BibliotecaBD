
from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuarios_bp.route("/")
def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("select * from Usuarios ORDER BY ID_usuario")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("usuarios_list.html", usuarios=usuarios)

@usuarios_bp.route("/novo", methods=["GET", "POST"])
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("Nome_usuario")
        email = request.form.get("Email")
        telefone = request.form.get("Numero_telefone")
        data_inscricao = request.form.get("Data_inscricao") or None
        multa = request.form.get("Multa_atual") or 0

        conn = get_connection()
        cur = conn.cursor()
        sql = (
            "INSERT INTO Usuarios "
            "(Nome_usuario, Email, Numero_telefone, Data_inscricao, Multa_atual) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        cur.execute(sql, (nome, email, telefone, data_inscricao, multa))
        conn.commit()
        cur.close()
        conn.close()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for("usuarios.listar_usuarios"))

    return render_template("usuarios_form.html", usuario=None)

@usuarios_bp.route("/editar/<int:id_usuario>", methods=["GET", "POST"])
def editar_usuario(id_usuario):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        nome = request.form.get("Nome_usuario")
        email = request.form.get("Email")
        telefone = request.form.get("Numero_telefone")
        data_inscricao = request.form.get("Data_inscricao") or None
        multa = request.form.get("Multa_atual") or 0

        sql = (
            "UPDATE Usuarios SET Nome_usuario=%s, Email=%s, Numero_telefone=%s, "
            "Data_inscricao=%s, Multa_atual=%s where ID_usuario=%s"
        )
        cur.execute(sql, (nome, email, telefone, data_inscricao, multa, id_usuario))
        conn.commit()
        cur.close()
        conn.close()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("usuarios.listar_usuarios"))

    cur.execute("select * from Usuarios where ID_usuario=%s", (id_usuario,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("usuarios_form.html", usuario=usuario)

@usuarios_bp.route("/excluir/<int:id_usuario>", methods=["POST"])
def excluir_usuario(id_usuario):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    #verif se tem emrepstimo com o livro
    cur.execute("select COUNT(*) AS total from Emprestimos where Usuario_id = %s",(id_usuario,))
    row = cur.fetchone()
    tem_emprestimo = row["total"] > 0 #ver se tem alguma coisa ligada

    if tem_emprestimo:
        #se tetnar excluir enquanto tem uma foreing key mirando nele, o codigo explode
        cur.close()
        conn.close()
        flash("Não é possível excluir o user porque existem empréstimos relacionados a ele.", "warning")
        return redirect(url_for("usuarios.listar_usuarios"))
    
    #aq so roda se tiver dado false no if de cima
    
    cur.execute("delete from Usuarios where ID_usuario=%s", (id_usuario,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("usuarios.listar_usuarios"))
