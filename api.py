from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

def obtener_conexion():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='12345',
        db='catalogo',
        cursorclass=pymysql.cursors.DictCursor
    )

#listar todos los lugares
@app.route('/api/catalogo', methods=['GET'])
def listar_lugares():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM lugares") 
            resp = cursor.fetchall()
        return jsonify(resp)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

#buscar el lugar por el id
@app.route('/api/catalogo/<int:id_lugar>', methods=['GET'])
def buscar_lugar(id_lugar):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM `lugares` WHERE id_lugar = %s", (id_lugar,))
            result = cursor.fetchone()
        if result:
            return jsonify(result)
        else:
            return jsonify({'message': 'no se encontró ningún lugar'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()
        
#agregar un lugar
@app.route('/api/catalogo', methods=['POST'])
def agregar_luagr():
    data = request.get_json()
    nom_lugar = data.get('nom_lugar')
    descripcion = data.get('descripcion')
    ubicacion = data.get('ubicacion')
    estatus = data.get('estatus')
#campos no llenados
    if not nom_lugar or not descripcion or not ubicacion or not estatus:
        return jsonify({'mensaje': 'Falgunos campos se encuentra vacios, favor de llenarlos.'}), 400
#si los campos están completos, insetar el lugar
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO lugares (nom_lugar, descripcion, ubicacion, estatus)
        VALUES (%s, %s, NOW(), %s)
    """, (nom_lugar, descripcion, ubicacion, estatus))
    conexion.commit()
    return jsonify({'mensaje': 'el lugar se ha añadido exitosamente'}), 201

#editar los campos del lugar
@app.route('/api/catalogo/<int:id_lugar>', methods=['PUT'])
def editar_lugar(id_lugar):
    try:

        data = request.get_json()
        nom_lugar = data.get('nom_lugar')
        descripcion = data.get('descripcion')
        ubicacion = data.get('ubicacion')
        estatus = data.get('estatus')

#verificar si los siguientes campos no están vacios
        if not nom_lugar or not descripcion or not ubicacion or not estatus:
            return jsonify({'mensaje': 'algunos campos se encuentra vacios, favor de llenarlos.'}), 400

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE lugares SET id_lugar = %s, descripcion = %s, ubicacion = %s, estatus = %s WHERE id_lugar = %s
               """, (nom_lugar, descripcion, ubicacion, estatus, id_lugar))
            conexion.commit()
        return jsonify({'mensaje': 'el lugar se ha añadido exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conexion' in locals():  
            conexion.close()    

#ELIMINAR UN LUGAR

@app.route('/api/catalogo/<int:id_lugar>', methods=['DELETE'])
def eliminar_lugar(id_lugar):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute('DELETE FROM `lugares` WHERE id_lugar = %s', (id_lugar,))
            conexion.commit()

 # Verifica si existe el elemento para eliminarlo

            # indica el número de filas que se vieron afectadas por la última consulta SQL ejecutada
            if cursor.rowcount == 0:
                return jsonify({'error': 'Lugar no encontrado.'}), 404

        # devuelve un mensaje de confirmación
        return jsonify({'mensaje': 'Lugar eliminado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conexion.close()

if __name__=='__main__':
    app.run(debug=True)