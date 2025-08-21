from flask import Flask, render_template, url_for, request, redirect

import psycopg2
import os

app = Flask(__name__)

# Configuración de la conexión a la base de datos
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
    Obtiene la lista de todas las cepas únicas para el menú de navegación.
    """
    cepas = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cepa FROM vinos ORDER BY cepa;")
        cepas = [row[0] for row in cursor.fetchall()]
    except (Exception, psycopg2.Error) as error:
        print("Error al obtener las cepas:", error)
    finally:
        if conn:
            conn.close()
    return cepas

def get_cepa_descripcion(cepa_nombre):
    """
    Obtiene la descripción de una cepa desde la tabla 'cepas_info'.
    """
    descripcion = "No hay descripción disponible para esta cepa."
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT descripcion FROM cepas_info WHERE cepa_nombre = %s;", (cepa_nombre,))
        result = cursor.fetchone()
        if result:
            descripcion = result[0]
    except (Exception, psycopg2.Error) as error:
        print("Error al obtener la descripción de la cepa:", error)
    finally:
        if conn:
            conn.close()
    return descripcion

@app.route('/')
def index():
    """
    Ruta para la página principal. Muestra todos los vinos.
    """
    vinos = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vinos;")
        vinos_db = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        vinos = [dict(zip(column_names, row)) for row in vinos_db]
    except (Exception, psycopg2.Error) as error:
        print("Error al obtener los vinos:", error)
    finally:
        if conn:
            conn.close()
    
    return render_template('index.html', vinos=vinos, cepas=get_cepas())

@app.route('/cepa/<cepa_elegida>')
def mostrar_cepa(cepa_elegida):
    """
    Ruta para ver los vinos de una cepa específica.
    """
    vinos = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Usamos un marcador de posición (%s) para evitar inyecciones SQL
        cursor.execute("SELECT * FROM vinos WHERE cepa = %s;", (cepa_elegida,))
        vinos_db = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        vinos = [dict(zip(column_names, row)) for row in vinos_db]
    except (Exception, psycopg2.Error) as error:
        print("Error al obtener los vinos de la cepa:", error)
    finally:
        if conn:
            conn.close()

    # Obtener la descripción de la cepa
    descripcion = get_cepa_descripcion(cepa_elegida)
    
    return render_template('cepa.html', vinos=vinos, cepa_actual=cepa_elegida, descripcion_cepa=descripcion, cepas=get_cepas())

@app.route('/vino/<int:vino_id>')
def ver_detalles_vino(vino_id):
    vino = None
    comentarios = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Obtener los detalles del vino
        cursor.execute("SELECT * FROM vinos WHERE id = %s;", (vino_id,))
        vino_db = cursor.fetchone()
        
        if vino_db:
            column_names = [desc[0] for desc in cursor.description]
            vino = dict(zip(column_names, vino_db))
            
            # 2. Obtener los comentarios para este vino
            cursor.execute("SELECT autor, comentario, fecha FROM comentarios WHERE vino_id = %s ORDER BY fecha DESC;", (vino_id,))
            comentarios_db = cursor.fetchall()
            comentarios = [dict(zip(['autor', 'comentario', 'fecha'], row)) for row in comentarios_db]
            
    except (Exception, psycopg2.Error) as error:
        print("Error al obtener los detalles y comentarios del vino:", error)
    finally:
        if conn:
            conn.close()

    if vino:
        return render_template('vino.html', vino=vino, comentarios=comentarios, cepas=get_cepas())
    else:
        return "Vino no encontrado", 404

# --- Sección para manejar los comentarios ---

@app.route('/agregar_comentario/<int:vino_id>', methods=['POST'])
def agregar_comentario(vino_id):
    if request.method == 'POST':
        autor = request.form['autor']
        comentario = request.form['comentario']
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO comentarios (vino_id, autor, comentario) VALUES (%s, %s, %s);",
                (vino_id, autor, comentario)
            )
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            print("Error al insertar el comentario:", error)
            conn.rollback()  # Revierte la transacción si hay un error
        finally:
            if conn:
                conn.close()
    
    return redirect(url_for('ver_detalles_vino', vino_id=vino_id))


if __name__ == '__main__':
    # Para iniciar el servidor de desarrollo, se ejecuta este bloque
    app.run(debug=True)