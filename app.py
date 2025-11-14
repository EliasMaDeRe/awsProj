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
    alumno = {
        "id": data["id"],
        "nombres": data.get("nombres"),
        "apellidos": data.get("apellidos"),
        "promedio": data.get("promedio")
    }
    alumnos.append(alumno)
    return jsonify(alumno), 201

@app.route('/alumnos/<int:alumno_id>', methods=['PUT'])
def put_alumno(alumno_id):
    data = request.get_json()
    for alumno in alumnos:
        if alumno["id"] == alumno_id:
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
    profesor = {
        "id": data["id"],
        "nombres": data.get("nombres"),
        "apellidos": data.get("apellidos"),
        "numeroEmpleado": data.get("numeroEmpleado"),
        "horasClase": data.get("horasClase")
    }
    profesores.append(profesor)
    return jsonify(profesor), 201

@app.route('/profesores/<int:profesor_id>', methods=['PUT'])
def put_profesor(profesor_id):
    data = request.get_json()
    for profesor in profesores:
        if profesor["id"] == profesor_id:
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
    print(f"[OK] Servidor Flask corriendo en http://0.0.0.0:3000")
    app.run(host='0.0.0.0', port=3000)


