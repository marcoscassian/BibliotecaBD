from flask import Flask, render_template
from database.config import Config
from database.models import db
from routes.autores import autores_bp
from routes.editoras import editoras_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(autores_bp)
app.register_blueprint(editoras_bp)

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas (ou já existiam).")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
