from flask import Blueprint, render_template
from db import get_connection

auditoria_bp = Blueprint("auditoria", __name__, url_prefix="/auditoria")

@auditoria_bp.route("/")
def listar_logs():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        select 
            l.id_log,
            l.tabela_afetada,
            l.operacao,
            l.data_operacao,
            u.nome_usuario,
            l.descricao
        from logs_auditoria l
        left join usuarios u on l.usuario_afetado = u.id_usuario
        order by l.data_operacao desc
    """)


    logs = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("auditoria_list.html", logs=logs)
