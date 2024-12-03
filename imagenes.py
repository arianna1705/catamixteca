from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  
        database='catalogo'
    )

# Obtener todas las imágenes activas
@app.route('/api/imagenes', methods=['GET'])
def get_imagenes():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imagenes WHERE estatus = 1")
    imagenes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(imagenes)

# Obtener una imagen por ID
@app.route('/api/imagenes/<int:id>', methods=['GET'])
def get_imagen(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM imagenes WHERE id_imagen = %s", (id,))
    imagen = cursor.fetchone()
    cursor.close()
    conn.close()

    if imagen is None or imagen['estatus'] == 0:
        return jsonify({'error': 'Imagen no encontrada o está inactiva'}), 404
    return jsonify(imagen)

# Crear una nueva imagen
@app.route('/api/imagenes', methods=['POST'])
def create_imagen():
    data = request.json
    required_fields = ['ruta_imagen', 'titulo_img', 'usu_mod', 'id_lugar']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)
    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO imagenes (ruta_imagen, titulo_img, estatus, usu_mod, ult_mod, fecha_mov, id_lugar) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['ruta_imagen'], data['titulo_img'], estatus, data['usu_mod'], action, now, data['id_lugar'])
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'message': 'Imagen creada con éxito', 'id_imagen': new_id}), 201

# Actualizar una imagen existente
@app.route('/api/imagenes/<int:id>', methods=['PUT'])
def update_imagen(id):
    data = request.json
    required_fields = ['ruta_imagen', 'titulo_img', 'estatus', 'usu_mod', 'id_lugar']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    if data['estatus'] not in [0, 1]:
        return jsonify({'error': 'El campo estatus debe ser 0 o 1'}), 400

    now = datetime.now().date()
    action = "Actualización"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imagenes SET ruta_imagen = %s, titulo_img = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s, id_lugar = %s WHERE id_imagen = %s",
        (data['ruta_imagen'], data['titulo_img'], data['estatus'], data['usu_mod'], action, now, data['id_lugar'], id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Imagen no encontrada'}), 404

    return jsonify({'message': f'Imagen con ID {id} actualizada con éxito'})

# Baja lógica de una imagen
@app.route('/api/imagenes/<int:id>', methods=['DELETE'])
def delete_imagen(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE imagenes SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_imagen = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Imagen no encontrada o ya está inactiva'}), 404

    return jsonify({'message': f'Imagen con ID {id} marcada como inactiva'})

if __name__ == '__main__':
    app.run(debug=True)
