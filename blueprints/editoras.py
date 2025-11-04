from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Editora


editoras_bp = Blueprint('editoras', __name__, url_prefix='/editoras')

@editoras_bp.route('/')
def listar_editoras():
    editoras = Editora.query.all()
    return render_template('editoras/listar.html', editoras=editoras)

@editoras_bp.route('/novo', methods=['GET', 'POST'])
def novo_editora():
    if request.method=='POST':
        editora=Editora(
            Nome_editora=request.form['nome'],
            Endereco_editora=request.form['endereco']
        )
        db.session.add(editora)
        db.session.commit()
        return redirect(url_for('editoras.listar_editoras'))
    return render_template('editoras/form.html')

@editoras_bp.route('/excluir/<int:id>')
def deletar_editora():
    editora=Editora.query.get_or_404(id)
    db.session.delete(editora)
    db.session.commit()
    return redirect(url_for('editoras.listar_editoras'))


@editoras_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_editora(id):
    editora = Editora.query.get_or_404(id)
    if request.method == 'POST':
        editora.Nome_editora = request.form['nome']
        editora.Endereco_editora = request.form['endereco']
        db.session.commit()
        return redirect(url_for('editoras.listar_editoras'))
    return render_template('editoras/form.html', editora=editora)