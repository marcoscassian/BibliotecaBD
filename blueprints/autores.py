from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Autor
from datetime import datetime

autores_bp = Blueprint('autores', __name__, url_prefix='/autores')

@autores_bp.route('/')
def listar_autores():
    autores= Autor.query.all()
    return render_template('autores/listar.html',autores=autores)

@autores_bp.route('/novo', methods=['GET', 'POST'])
def novo_autor():
    if request.method=='POST':
        autor=Autor(
            Nome_autor=request.form['nome'],
            Naciolaidade=request.form['nacionalidade'],
            Data_nascimento=datetime.strptime(request.form['data_nascimento'], '%Y-%m-%d'),#ano,mes,dia
            Biografia=request.form['biografia']
        )
        db.session.add(autor)
        db.session.commit()
        return redirect(url_for('autores.listar_autores'))
    return render_template('autores/form.html')

@autores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_autor(id):
    autor = Autor.query.get_or_404(id)
    if request.method == 'POST':
        autor.Nome_autor = request.form['nome']
        autor.Nacionalidade = request.form['nacionalidade']
        autor.Data_nascimento = datetime.strptime(request.form['data_nascimento'], '%Y-%m-%d')
        autor.Biografia = request.form['biografia']
        db.session.commit()
        return redirect(url_for('autores.listar_autores'))
    return render_template('autores/form.html', autor=autor)


@autores_bp.route('/excluir/<int:id>')
def deletar_autor():
    autor=Autor.query.get_or_404(id) #se n achar id da erro 404
    db.session.delete(autor)
    db.session.commit()
    return redirect(url_for('autores.listar_autores'))