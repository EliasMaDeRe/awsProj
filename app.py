import json
from flask import Flask, jsonify, request

app = Flask(__name__)
PORT = 3000

alumnos = [
    {"id": 1, "nombres": "Elias", "apellidos": "Madera De Regil", "matricula": "18000577", "promedio": 100.00},
]
profesores = [
    {"id": 1, "numeroEmpleado": "P1", "nombres": "Eduardo", "apellidos": "Rodríguez", "horasClase": 4},
]

next_alumno_id = 2
next_profesor_id = 2


def validate_alumno(data):
    if not isinstance(data, dict):
        return "Solicitud JSON no válida."
    
    required_text_fields = ["nombres", "apellidos", "matricula"]
    for field in required_text_fields:
        if field not in data or not isinstance(data.get(field), str) or not data[field].strip():
            return f"Campo '{field}' obligatorio o vacío."

    promedio_val = data.get("promedio")
    if promedio_val is None:
        return "Campo 'promedio' obligatorio."
    
    try:
        promedio = float(promedio_val)
        if not (0 <= promedio <= 100):
            return "Promedio fuera de rango (0-100)."
    except (ValueError, TypeError):
        return "Campo 'promedio' debe ser numérico."

    return None

def validate_profesor(data):
    if not isinstance(data, dict):
        return "Solicitud JSON no válida."

    required_text_fields = ["nombres", "apellidos", "numeroEmpleado"]
    for field in required_text_fields:
        if field not in data or not isinstance(data.get(field), str) or not data[field].strip():
            return f"Campo '{field}' obligatorio o vacío."

    horas_clase_val = data.get("horasClase")
    if horas_clase_val is None:
        return "Campo 'horasClase' obligatorio."
    
    try:
        horas_clase = int(horas_clase_val)
        if horas_clase <= 0:
            return "Campo 'horasClase' debe ser positivo."
    except (ValueError, TypeError):
        return "Campo 'horasClase' debe ser entero."

    return None


@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    return jsonify(alumnos), 200

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = next((a for a in alumnos if a["id"] == id), None)
    if alumno:
        return jsonify(alumno), 200
    return jsonify({"error": "Alumno no encontrado."}), 404

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    global next_alumno_id
    try:
        data = request.get_json()
        error = validate_alumno(data)
        
        if error:
            return jsonify({"error": error}), 400

        nuevo_alumno = {
            "id": next_alumno_id,
            "nombres": data["nombres"].strip(),
            "apellidos": data["apellidos"].strip(),
            "matricula": data["matricula"].strip(),
            "promedio": float(data["promedio"]),
        }
        alumnos.append(nuevo_alumno)
        next_alumno_id += 1
        
        return jsonify(nuevo_alumno), 201
    except Exception:
        return jsonify({"error": "Error interno al procesar la solicitud."}), 500

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    try:
        data = request.get_json()
        error = validate_alumno(data)

        if error:
            return jsonify({"error": error}), 400

        index = next((i for i, a in enumerate(alumnos) if a["id"] == id), -1)

        if index == -1:
            return jsonify({"error": "Alumno no encontrado para actualizar."}), 404
        
        alumnos[index] = {
            "id": id,
            "nombres": data["nombres"].strip(),
            "apellidos": data["apellidos"].strip(),
            "matricula": data["matricula"].strip(),
            "promedio": float(data["promedio"]),
        }

        return jsonify(alumnos[index]), 200
    except Exception:
        return jsonify({"error": "Error interno al procesar la solicitud."}), 500

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    global alumnos
    initial_length = len(alumnos)
    alumnos = [a for a in alumnos if a["id"] != id]

    if len(alumnos) < initial_length:
        return jsonify({"message": "Alumno eliminado exitosamente."}), 200
    else:
        return jsonify({"error": "Alumno no encontrado para eliminar."}), 404


@app.route('/profesores', methods=['GET'])
def get_profesores():
    return jsonify(profesores), 200

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = next((p for p in profesores if p["id"] == id), None)
    if profesor:
        return jsonify(profesor), 200
    return jsonify({"error": "Profesor no encontrado."}), 404

@app.route('/profesores', methods=['POST'])
def create_profesor():
    global next_profesor_id
    try:
        data = request.get_json()
        error = validate_profesor(data)

        if error:
            return jsonify({"error": error}), 400

        nuevo_profesor = {
            "id": next_profesor_id,
            "numeroEmpleado": data["numeroEmpleado"].strip(),
            "nombres": data["nombres"].strip(),
            "apellidos": data["apellidos"].strip(),
            "horasClase": int(data["horasClase"]),
        }
        profesores.append(nuevo_profesor)
        next_profesor_id += 1

        return jsonify(nuevo_profesor), 201
    except Exception:
        return jsonify({"error": "Error interno al procesar la solicitud."}), 500

@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    try:
        data = request.get_json()
        error = validate_profesor(data)

        if error:
            return jsonify({"error": error}), 400

        index = next((i for i, p in enumerate(profesores) if p["id"] == id), -1)

        if index == -1:
            return jsonify({"error": "Profesor no encontrado para actualizar."}), 404
        
        profesores[index] = {
            "id": id,
            "numeroEmpleado": data["numeroEmpleado"].strip(),
            "nombres": data["nombres"].strip(),
            "apellidos": data["apellidos"].strip(),
            "horasClase": int(data["horasClase"]),
        }

        return jsonify(profesores[index]), 200
    except Exception:
        return jsonify({"error": "Error interno al procesar la solicitud."}), 500

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    global profesores
    initial_length = len(profesores)
    profesores = [p for p in profesores if p["id"] != id]

    if len(profesores) < initial_length:
        return jsonify({"message": "Profesor eliminado exitosamente."}), 200
    else:
        return jsonify({"error": "Profesor no encontrado para eliminar."}), 404

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Ruta no encontrada."}), 404

if __name__ == '__main__':
    print(f"[OK] Servidor Flask corriendo en http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT)