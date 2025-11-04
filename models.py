from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Autor(db.Model):
    __tablename__ = 'Autores'
    ID_autor = db.Column(db.Integer, primary_key=True)
    Nome_autor = db.Column(db.String(255), nullable=False)
    Nacionalidade = db.Column(db.String(255))
    Data_nascimento = db.Column(db.Date)
    Biografia = db.Column(db.Text)
    livros = db.relationship('Livro', backref='autor', lazy=True)

class Genero(db.Model):
    __tablename__ = 'Generos'
    ID_genero = db.Column(db.Integer, primary_key=True)
    Nome_genero = db.Column(db.String(255), nullable=False)
    livros = db.relationship('Livro', backref='genero', lazy=True)

class Editora(db.Model):
    __tablename__ = 'Editoras'
    ID_editora = db.Column(db.Integer, primary_key=True)
    Nome_editora = db.Column(db.String(255), nullable=False)
    Endereco_editora = db.Column(db.Text)
    livros = db.relationship('Livro', backref='editora', lazy=True)

class Livro(db.Model):
    __tablename__ = 'Livros'
    ID_livro = db.Column(db.Integer, primary_key=True)
    Titulo = db.Column(db.String(255), nullable=False)
    Autor_id = db.Column(db.Integer, db.ForeignKey('Autores.ID_autor'))
    ISBN = db.Column(db.String(13), nullable=False)
    Ano_publicacao = db.Column(db.Integer)
    Genero_id = db.Column(db.Integer, db.ForeignKey('Generos.ID_genero'))
    Editora_id = db.Column(db.Integer, db.ForeignKey('Editoras.ID_editora'))
    Quantidade_disponivel = db.Column(db.Integer)
    Resumo = db.Column(db.Text)
    emprestimos = db.relationship('Emprestimo', backref='livro', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    ID_usuario = db.Column(db.Integer, primary_key=True)
    Nome_usuario = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255))
    Numero_telefone = db.Column(db.String(15))
    Data_inscricao = db.Column(db.Date)
    Multa_atual = db.Column(db.Numeric(10, 2))
    emprestimos = db.relationship('Emprestimo', backref='usuario', lazy=True)

class Emprestimo(db.Model):
    __tablename__ = 'Emprestimos'
    ID_emprestimo = db.Column(db.Integer, primary_key=True)
    Usuario_id = db.Column(db.Integer, db.ForeignKey('Usuarios.ID_usuario'))
    Livro_id = db.Column(db.Integer, db.ForeignKey('Livros.ID_livro'))
    Data_emprestimo = db.Column(db.Date)
    Data_devolucao_prevista = db.Column(db.Date)
    Data_devolucao_real = db.Column(db.Date)
    Status_emprestimo = db.Column(db.Enum('pendente', 'devolvido', 'atrasado'))