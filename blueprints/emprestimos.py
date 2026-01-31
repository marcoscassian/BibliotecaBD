from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection
import mysql.connector

emprestimos_bp = Blueprint("emprestimos", __name__, url_prefix="/emprestimos")

@emprestimos_bp.route("/")
def listar_emprestimos():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    sql = (
        "SELECT E.ID_emprestimo, U.Nome_usuario, U.Status as Usuario_status, L.Titulo, "
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
    # Carregar apenas usuários ativos para empréstimos
    cur.execute("SELECT ID_usuario, Nome_usuario, Status FROM Usuarios ORDER BY Nome_usuario")
    usuarios = cur.fetchall()
    cur.execute("SELECT ID_livro, Titulo, Quantidade_disponivel FROM Livros ORDER BY Titulo")
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
        data_emp = request.form.get("Data_emprestimo")
        if data_emp == '':
            data_emp = None
        data_prev = request.form.get("Data_devolucao_prevista") or None
        data_real = request.form.get("Data_devolucao_real") or None
        status = request.form.get("Status_emprestimo") or 'pendente'

        sql = (
            "INSERT INTO Emprestimos "
            "(Usuario_id, Livro_id, Data_emprestimo, Data_devolucao_prevista, "
            "Data_devolucao_real, Status_emprestimo) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )

        cur = conn.cursor()

        try:
            cur.execute(sql, (usuario_id, livro_id, data_emp, data_prev, data_real, status))
            conn.commit()
            flash("Empréstimo cadastrado com sucesso!", "success")
            return redirect(url_for("emprestimos.listar_emprestimos"))

        except mysql.connector.Error as err:
            conn.rollback()
            error_msg = str(err.msg).lower() if hasattr(err, 'msg') else str(err).lower()
            print(f"Erro capturado: {err}")

            # Tratamento dos erros dos triggers
            if "inativo" in error_msg or "usuário inativo" in error_msg:
                flash("Este usuário está inativo e não pode realizar empréstimos.", "danger")
            elif "indisponível" in error_msg or "sem estoque" in error_msg:
                flash("Este livro não possui estoque disponível para empréstimo.", "danger")
            elif "duplicado" in error_msg or "empréstimo ativo" in error_msg:
                flash("Este usuário já possui um empréstimo pendente para este livro.", "danger")
            else:
                flash(f"Erro ao cadastrar empréstimo: {err}", "danger")
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
        # Carregar status atual do empréstimo para usar como fallback caso não seja selecionado outro
        cur.execute("SELECT Status_emprestimo FROM Emprestimos WHERE ID_emprestimo=%s", (id_emprestimo,))
        row = cur.fetchone()
        current_status = row['Status_emprestimo'] if row and 'Status_emprestimo' in row else 'pendente'
        status = request.form.get("Status_emprestimo") or current_status

        sql = (
            "UPDATE Emprestimos SET Usuario_id=%s, Livro_id=%s, "
            "Data_emprestimo=%s, Data_devolucao_prevista=%s, "
            "Data_devolucao_real=%s, Status_emprestimo=%s "
            "WHERE ID_emprestimo=%s"
        )

        try:
            cur2 = conn.cursor()
            cur2.execute(
                sql,
                (usuario_id, livro_id, data_emp, data_prev, data_real, status, id_emprestimo),
            )
            conn.commit()
            cur2.close()
            flash("Empréstimo atualizado com sucesso!", "success")
            return redirect(url_for("emprestimos.listar_emprestimos"))

        except mysql.connector.Error as err:
            conn.rollback()
            error_msg = str(err.msg).lower() if hasattr(err, 'msg') else str(err).lower()

            # Tratamento dos erros dos triggers
            if "data de devolução" in error_msg or "anterior" in error_msg:
                flash("A data de devolução não pode ser anterior à data do empréstimo.", "danger")
            else:
                flash(f"Erro ao atualizar empréstimo: {err}", "danger")
            return redirect(url_for("emprestimos.editar_emprestimo", id_emprestimo=id_emprestimo))

        finally:
            cur.close()
            conn.close()

    cur.execute("SELECT * FROM Emprestimos WHERE ID_emprestimo=%s", (id_emprestimo,))
    emprestimo = cur.fetchone()

    for campo in ['Data_emprestimo', 'Data_devolucao_prevista', 'Data_devolucao_real']:
        if campo in emprestimo:
            if emprestimo[campo]:
                emprestimo[campo] = emprestimo[campo].strftime('%Y-%m-%d')
            else:
                emprestimo[campo] = ''

    cur.close()
    conn.close()

    return render_template(
        "emprestimos_form.html",
        emprestimo=emprestimo,
        usuarios=usuarios,
        livros=livros,
    )

@emprestimos_bp.route("/devolver/<int:id_emprestimo>", methods=["POST"])
def devolver_emprestimo(id_emprestimo):
    """Registra a devolução de um empréstimo"""
    conn = get_connection()
    cur = conn.cursor()

    try:
        # O trigger trg_gerar_status_emprestimo vai atualizar o status automaticamente
        # O trigger trg_retorna_estoque_livro vai devolver o livro ao estoque
        # O trigger trg_gerar_multa_atraso vai calcular multa se houver atraso
        cur.execute(
            "UPDATE Emprestimos SET Data_devolucao_real = CURDATE() WHERE ID_emprestimo = %s",
            (id_emprestimo,)
        )
        conn.commit()
        flash("Devolução registrada com sucesso!", "success")

    except mysql.connector.Error as err:
        conn.rollback()
        error_msg = str(err.msg).lower() if hasattr(err, 'msg') else str(err).lower()

        if "data de devolução" in error_msg:
            flash("Erro na data de devolução.", "danger")
        else:
            flash(f"Erro ao registrar devolução: {err}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("emprestimos.listar_emprestimos"))

@emprestimos_bp.route("/excluir/<int:id_emprestimo>", methods=["POST"])
def excluir_emprestimo(id_emprestimo):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # O trigger trg_inativa_usuario pode inativar o usuário se não tiver mais empréstimos
        cur.execute("DELETE FROM Emprestimos WHERE ID_emprestimo=%s", (id_emprestimo,))
        conn.commit()
        flash("Empréstimo excluído com sucesso!", "success")

    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao excluir empréstimo: {err}", "danger")

    finally:
        cur.close()
        conn.close()

    return redirect(url_for("emprestimos.listar_emprestimos"))
