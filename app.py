
from flask import Flask, render_template
from blueprints.autores import autores_bp
from blueprints.generos import generos_bp
from blueprints.editoras import editoras_bp
from blueprints.usuarios import usuarios_bp
from blueprints.livros import livros_bp
from blueprints.emprestimos import emprestimos_bp

def cria_app():
    app = Flask(__name__)
    app.secret_key = "chave_super_secreta"

    app.register_blueprint(autores_bp)
    app.register_blueprint(generos_bp)
    app.register_blueprint(editoras_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(livros_bp)
    app.register_blueprint(emprestimos_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = cria_app()
    app.run(debug=True)
