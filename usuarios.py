from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Cambia la contraseña si aplica
        database='catalogo'
    )

# Obtener todos los usuarios activos
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE estatus = 1")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(usuarios)

# Obtener un usuario por ID
@app.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario is None or usuario['estatus'] == 0:
        return jsonify({'error': 'Usuario no encontrado o está inactivo'}), 404
    return jsonify(usuario)

# Crear un nuevo usuario
@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    data = request.json
    required_fields = ['nom_usuario', 'correo', 'contrasena', 'usu_mod']

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)
    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nom_usuario, correo, contrasena, estatus, usu_mod, ult_mod, fecha_mov) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['nom_usuario'], data['correo'], data['contrasena'], estatus, data['usu_mod'], action, now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'message': 'Usuario creado con éxito', 'id_usuario': new_id}), 201

# Actualizar un usuario existente
@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    required_fields = ['nom_usuario', 'correo', 'contrasena', 'estatus', 'usu_mod']

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
        "UPDATE usuarios SET nom_usuario = %s, correo = %s, contrasena = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s WHERE id_usuario = %s",
        (data['nom_usuario'], data['correo'], data['contrasena'], data['estatus'], data['usu_mod'], action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({'message': f'Usuario con ID {id} actualizado con éxito'})

# Baja lógica de un usuario
@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_usuario = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Usuario no encontrado o ya está inactivo'}), 404

    return jsonify({'message': f'Usuario con ID {id} marcado como inactivo'})

if __name__ == '__main__':
    app.run(debug=True)
