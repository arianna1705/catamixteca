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

# Obtener todos los lugares activos
@app.route('/api/lugares', methods=['GET'])
def get_lugares():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lugares WHERE estatus = 1")
    lugares = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(lugares)

# Obtener un lugar por ID 
@app.route('/api/lugares/<int:id>', methods=['GET'])
def get_lugar(id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lugares WHERE id_lugar = %s", (id,))
    lugar = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if lugar is None or lugar['estatus'] == 0:
        return jsonify({'error': 'Lugar no encontrado o está inactivo'}), 404
    return jsonify(lugar)

# Crear un nuevo lugar
@app.route('/api/lugares', methods=['POST'])
def create_lugar():
    data = request.json
    required_fields = ['nom_lugar', 'descripcion', 'ubicacion', 'usu_mod']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'El campo {field} es obligatorio'}), 400

    estatus = data.get('estatus', 1)

    now = datetime.now().date()
    action = "Creación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lugares (nom_lugar, descripcion, ubicacion, estatus, usu_mod, ult_mod, fecha_mov) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['nom_lugar'], data['descripcion'], data['ubicacion'], estatus, data['usu_mod'], action, now)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    return jsonify({'message': f'Lugar creado con éxito', 'id_lugar': new_id}), 201

# Actualizar un lugar existente
@app.route('/api/lugares/<int:id>', methods=['PUT'])
def update_lugar(id):
    data = request.json
    required_fields = ['nom_lugar', 'descripcion', 'ubicacion', 'estatus', 'usu_mod']
    
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
        "UPDATE lugares SET nom_lugar = %s, descripcion = %s, ubicacion = %s, estatus = %s, usu_mod = %s, ult_mod = %s, fecha_mov = %s WHERE id_lugar = %s",
        (data['nom_lugar'], data['descripcion'], data['ubicacion'], data['estatus'], data['usu_mod'], action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Lugar no encontrado'}), 404

    return jsonify({'message': f'Lugar con ID {id} actualizado con éxito'})

# Baja lógica de un lugar 
@app.route('/api/lugares/<int:id>', methods=['DELETE'])
def delete_lugar(id):
    now = datetime.now().date()
    action = "Eliminación"

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE lugares SET estatus = 0, ult_mod = %s, fecha_mov = %s WHERE id_lugar = %s AND estatus = 1",
        (action, now, id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    cursor.close()
    conn.close()

    if rows_affected == 0:
        return jsonify({'error': 'Lugar no encontrado o ya está inactivo'}), 404

    return jsonify({'message': f'Lugar con ID {id} marcado como inactivo'})

if __name__ == '__main__':
    app.run(debug=True)
