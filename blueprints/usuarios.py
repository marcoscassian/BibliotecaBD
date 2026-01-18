from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection
import mysql.connector

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuarios_bp.route("/")
def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Usuarios ORDER BY ID_usuario")
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
        status = request.form.get("Status") or 'ativo'
        multa = request.form.get("Multa_atual") or 0

        conn = get_connection()
        cur = conn.cursor()

        try:
            # Verificar se email já existe (validação no código)
            cur.execute("SELECT COUNT(*) FROM Usuarios WHERE Email = %s", (email,))
            if cur.fetchone()[0] > 0:
                flash("Este email já está cadastrado no sistema.", "danger")
                return redirect(url_for("usuarios.novo_usuario"))

            sql = (
                "INSERT INTO Usuarios "
                "(Nome_usuario, Email, Numero_telefone, Data_inscricao, Status, Multa_atual) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cur.execute(sql, (nome, email, telefone, data_inscricao, status, multa))
            conn.commit()
            flash("Usuário cadastrado com sucesso!", "success")
            return redirect(url_for("usuarios.listar_usuarios"))

        except mysql.connector.Error as err:
            conn.rollback()
            error_msg = str(err.msg).lower() if hasattr(err, 'msg') else str(err).lower()

            if "duplicate" in error_msg or "email" in error_msg:
                flash("Este email já está cadastrado no sistema.", "danger")
            else:
                flash(f"Erro ao cadastrar usuário: {err}", "danger")
            return redirect(url_for("usuarios.novo_usuario"))

        finally:
            cur.close()
            conn.close()

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
        status = request.form.get("Status") or 'ativo'
        multa = request.form.get("Multa_atual") or 0

        try:
            # Verificar se email já existe para outro usuário
            cur.execute(
                "SELECT COUNT(*) as total FROM Usuarios WHERE Email = %s AND ID_usuario != %s",
                (email, id_usuario)
            )
            if cur.fetchone()["total"] > 0:
                flash("Este email já está cadastrado para outro usuário.", "danger")
                return redirect(url_for("usuarios.editar_usuario", id_usuario=id_usuario))

            sql = (
                "UPDATE Usuarios SET Nome_usuario=%s, Email=%s, Numero_telefone=%s, "
                "Data_inscricao=%s, Status=%s, Multa_atual=%s WHERE ID_usuario=%s"
            )
            cur.execute(sql, (nome, email, telefone, data_inscricao, status, multa, id_usuario))
            conn.commit()
            flash("Usuário atualizado com sucesso!", "success")
            return redirect(url_for("usuarios.listar_usuarios"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao atualizar usuário: {err}", "danger")
            return redirect(url_for("usuarios.editar_usuario", id_usuario=id_usuario))

        finally:
            cur.close()
            conn.close()

    cur.execute("SELECT * FROM Usuarios WHERE ID_usuario=%s", (id_usuario,))
    usuario = cur.fetchone()
    if usuario and 'Data_inscricao' in usuario and usuario['Data_inscricao']:
        usuario['Data_inscricao'] = usuario['Data_inscricao'].strftime('%Y-%m-%d')
    cur.close()
    conn.close()
    return render_template("usuarios_form.html", usuario=usuario)

@usuarios_bp.route("/excluir/<int:id_usuario>", methods=["POST"])
def excluir_usuario(id_usuario):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Verificar se tem empréstimo com o usuário
    cur.execute("SELECT COUNT(*) AS total FROM Emprestimos WHERE Usuario_id = %s", (id_usuario,))
    row = cur.fetchone()
    tem_emprestimo = row["total"] > 0

    if tem_emprestimo:
        cur.close()
        conn.close()
        flash("Não é possível excluir o usuário porque existem empréstimos relacionados a ele.", "warning")
        return redirect(url_for("usuarios.listar_usuarios"))

    try:
        cur.execute("DELETE FROM Usuarios WHERE ID_usuario=%s", (id_usuario,))
        conn.commit()
        flash("Usuário excluído com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao excluir usuário: {err}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("usuarios.listar_usuarios"))

@usuarios_bp.route("/ativar/<int:id_usuario>", methods=["POST"])
def ativar_usuario(id_usuario):
    """Ativa um usuário inativo"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE Usuarios SET Status = 'ativo' WHERE ID_usuario = %s", (id_usuario,))
        conn.commit()
        flash("Usuário ativado com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao ativar usuário: {err}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("usuarios.listar_usuarios"))

@usuarios_bp.route("/inativar/<int:id_usuario>", methods=["POST"])
def inativar_usuario(id_usuario):
    """Inativa um usuário ativo"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("UPDATE Usuarios SET Status = 'inativo' WHERE ID_usuario = %s", (id_usuario,))
        conn.commit()
        flash("Usuário inativado com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao inativar usuário: {err}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("usuarios.listar_usuarios"))
