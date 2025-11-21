from flask import Flask, request, jsonify

app = Flask(__name__)

alumnos = []
profesores = []

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    return jsonify(alumnos), 200

@app.route('/alumnos/<int:alumno_id>', methods=['GET'])
def get_alumno(alumno_id):
    for alumno in alumnos:
        if alumno["id"] == alumno_id:
            return jsonify(alumno), 200
    return jsonify({"error": "Alumno no encontrado"}), 404

@app.route('/alumnos', methods=['POST'])
def post_alumno():
    data = request.get_json()
    if (
        "id" not in data
        or "nombres" not in data
        or "apellidos" not in data
        or "matricula" not in data
        or "promedio" not in data
        or not isinstance(data["id"], int)
        or not isinstance(data["nombres"], str) or data["nombres"].strip() == ""
        or not isinstance(data["apellidos"], str)
        or not isinstance(data["matricula"], str)
        or not isinstance(data["promedio"], (float, int)) or data["promedio"] < 0
    ):
        return jsonify({"error": "Datos inválidos"}), 400
    alumnos.append(data)
    return jsonify(data), 201

@app.route('/alumnos/<int:alumno_id>', methods=['PUT'])
def put_alumno(alumno_id):
    data = request.get_json()
    for alumno in alumnos:
        if alumno["id"] == alumno_id:
            if (
                "nombres" not in data
                or "matricula" not in data
                or not isinstance(data["nombres"], str) or data["nombres"].strip() == ""
                or not isinstance(data["matricula"], str)
            ):
                return jsonify({"error": "Datos inválidos"}), 400
            alumno.update(data)
            return jsonify(alumno), 200
    return jsonify({"error": "Alumno no encontrado"}), 404

@app.route('/alumnos/<int:alumno_id>', methods=['DELETE'])
def delete_alumno(alumno_id):
    global alumnos
    for alumno in alumnos:
        if alumno["id"] == alumno_id:
            alumnos = [a for a in alumnos if a["id"] != alumno_id]
            return jsonify({"mensaje": "Alumno eliminado"}), 200
    return jsonify({"error": "Alumno no encontrado"}), 404

@app.route('/profesores', methods=['GET'])
def get_profesores():
    return jsonify(profesores), 200

@app.route('/profesores/<int:profesor_id>', methods=['GET'])
def get_profesor(profesor_id):
    for profesor in profesores:
        if profesor["id"] == profesor_id:
            return jsonify(profesor), 200
    return jsonify({"error": "Profesor no encontrado"}), 404

@app.route('/profesores', methods=['POST'])
def post_profesor():
    data = request.get_json()
    if (
        "id" not in data
        or "nombres" not in data
        or "apellidos" not in data
        or "numeroEmpleado" not in data
        or "horasClase" not in data
        or not isinstance(data["id"], int)
        or not isinstance(data["nombres"], str) or data["nombres"].strip() == ""
        or not isinstance(data["apellidos"], str)
        or not isinstance(data["numeroEmpleado"], int) or data["numeroEmpleado"] < 0
        or not isinstance(data["horasClase"], (float, int)) or data["horasClase"] < 0
    ):
        return jsonify({"error": "Datos inválidos"}), 400
    profesores.append(data)
    return jsonify(data), 201

@app.route('/profesores/<int:profesor_id>', methods=['PUT'])
def put_profesor(profesor_id):
    data = request.get_json()
    for profesor in profesores:
        if profesor["id"] == profesor_id:
            if (
                "nombres" not in data
                or "horasClase" not in data
                or not isinstance(data["nombres"], str) or data["nombres"].strip() == ""
                or not isinstance(data["horasClase"], (float, int)) or data["horasClase"] < 0
            ):
                return jsonify({"error": "Datos inválidos"}), 400
            profesor.update(data)
            return jsonify(profesor), 200
    return jsonify({"error": "Profesor no encontrado"}), 404

@app.route('/profesores/<int:profesor_id>', methods=['DELETE'])
def delete_profesor(profesor_id):
    global profesores
    for profesor in profesores:
        if profesor["id"] == profesor_id:
            profesores = [p for p in profesores if p["id"] != profesor_id]
            return jsonify({"mensaje": "Profesor eliminado"}), 200
    return jsonify({"error": "Profesor no encontrado"}), 404

if __name__ == '__main__':
    print("[OK] Servidor Flask corriendo en http://0.0.0.0:3000")
    app.run(host='0.0.0.0', port=3000)
