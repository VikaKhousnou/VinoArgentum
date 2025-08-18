from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# 1. Configurar la aplicación Flask
app = Flask(__name__)
# Configura la conexión a tu base de datos (cambia la contraseña y el nombre de la DB si es necesario)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres/vinos_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. Definir el modelo de la tabla 'vinos'
class Vino(db.Model):
    __tablename__ = 'vinos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    cepa = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    foto_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<Vino {self.nombre}>'

# 3. Crear las rutas (lo que pasa cuando el usuario visita una URL)
@app.route('/')
def home():
    vinos = Vino.query.all() # Obtiene todos los vinos de la base de datos
    return render_template('index.html', vinos=vinos)

# 4. Iniciar la aplicación
if __name__ == '__main__':
    # Crea las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True)