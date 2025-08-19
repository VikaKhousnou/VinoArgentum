from flask import Flask, render_template
import psycopg2
import os

app = Flask(__name__)

# Configuración de la conexión a la base de datos
# Es buena práctica usar variables de entorno para datos sensibles como contraseñas
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'vinos_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

def get_db_connection():
    """
    Función para establecer y devolver una conexión a la base de datos PostgreSQL.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

def get_cepas():
    """
    Obtiene la lista de todas las cepas únicas de la base de datos para el menú de navegación.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT cepa FROM vinos ORDER BY cepa;")
    cepas = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cepas

@app.route('/')
def index():
    """
    Ruta para la página principal del blog. Muestra todos los vinos.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vinos;")
    vinos_db = cursor.fetchall()
    conn.close()

    # Obtener los nombres de las columnas para crear diccionarios
    column_names = [desc[0] for desc in cursor.description]
    # Convertir la lista de tuplas de la base de datos a una lista de diccionarios
    # Esto hace más fácil acceder a los datos en la plantilla (ej: vino['nombre'])
    vinos = [dict(zip(column_names, row)) for row in vinos_db]
    
    # Renderiza la plantilla index.html y le pasa los datos de los vinos y las cepas
    return render_template('index.html', vinos=vinos, cepas=get_cepas())

@app.route('/cepa/<cepa_elegida>')
def mostrar_cepa(cepa_elegida):
    """
    Ruta para ver los vinos de una cepa específica.
    El <cepa_elegida> en la URL se pasa como argumento a la función.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    # Usamos un marcador de posición (%s) para evitar inyecciones SQL
    cursor.execute("SELECT * FROM vinos WHERE cepa = %s;", (cepa_elegida,))
    vinos_db = cursor.fetchall()
    conn.close()

    column_names = [desc[0] for desc in cursor.description]
    vinos = [dict(zip(column_names, row)) for row in vinos_db]

    # Renderiza la plantilla cepa.html, pasando los vinos filtrados y la cepa actual
    return render_template('cepa.html', vinos=vinos, cepa_actual=cepa_elegida, cepas=get_cepas())

if __name__ == '__main__':
    # Para iniciar el servidor de desarrollo, se ejecuta este bloque
    app.run(debug=True)