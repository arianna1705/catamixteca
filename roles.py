from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Cambiar si tu contraseña no está vacía
        database='catalogo'
    )

# Obtener todos los roles activos
@app.route('/api/roles', methods=['GET'])
def get_roles():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles WHERE estatus = 1")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(roles)

# Obtener un rol por ID
@app.route('/api/roles/<int:id>', methods=['GET'])
def get_rol(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM roles WHERE id_rol = %s", (id,))
    rol = cursor.fetchone()
    cursor.close()
    conn.close()

    if rol is None or rol['estatus'] == 0:
        return jsonify({'error': 'Rol no encontrado o está inactivo'}), 404
    return jsonify(rol)

# Crear un nuevo rol
@app.route('/api/roles', methods=['POST'])
def create_rol():
    data = request.json
    required_fields = ['nom_rol', 'usu_mod']

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)
    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO roles (nom_rol, estatus, usu_mod, ult_mod, fecha_mov) VALUES (%s, %s, %s, %s, %s)",
        (data['nom_rol'], estatus, data['usu_mod'], action, now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'message': 'Rol creado con éxito', 'id_rol': new_id}), 201

# Actualizar un rol existente
@app.route('/api/roles/<int:id>', methods=['PUT'])
def update_rol(id):
    data = request.json
    required_fields = ['nom_rol', 'estatus', 'usu_mod']

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
        "UPDATE roles SET nom_rol = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s WHERE id_rol = %s",
        (data['nom_rol'], data['estatus'], data['usu_mod'], action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Rol no encontrado'}), 404

    return jsonify({'message': f'Rol con ID {id} actualizado con éxito'})

# Baja lógica de un rol
@app.route('/api/roles/<int:id>', methods=['DELETE'])
def delete_rol(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE roles SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_rol = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Rol no encontrado o ya está inactivo'}), 404

    return jsonify({'message': f'Rol con ID {id} marcado como inactivo'})

if __name__ == '__main__':
    app.run(debug=True)
