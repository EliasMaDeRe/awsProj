import os
import time
import uuid
import secrets
import boto3
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from botocore.exceptions import ClientError

app = Flask(__name__)

AWS_REGION = 'us-east-1'
AWS_ACCESS_KEY = '' 
AWS_SECRET_KEY = ''
AWS_SESSION_TOKEN = '' 

DB_USER = 'admin'
DB_PASS = ''
DB_HOST = '.us-east-1.rds.amazonaws.com'
DB_NAME = 'cloud_foundations'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

S3_BUCKET_NAME = 'bucket'
SNS_TOPIC_ARN = 'topic'
DYNAMO_TABLE_NAME = 'sesiones-alumnos'

db = SQLAlchemy(app)

def get_aws_client(service):
    return boto3.client(
        service,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        aws_session_token=AWS_SESSION_TOKEN
    )

class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), nullable=False)
    promedio = db.Column(db.Float, nullable=False)
    fotoPerfilUrl = db.Column(db.String(300), nullable=True)
    password = db.Column(db.String(100), nullable=True) 

    def to_dict(self):
        return {
            "id": self.id,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "matricula": self.matricula,
            "promedio": self.promedio,
            "fotoPerfilUrl": self.fotoPerfilUrl,
        }

class Profesor(db.Model):
    __tablename__ = 'profesores'
    id = db.Column(db.Integer, primary_key=True)
    numeroEmpleado = db.Column(db.String(50), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    horasClase = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "numeroEmpleado": self.numeroEmpleado,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "horasClase": self.horasClase
        }

with app.app_context():
    db.create_all()

def validate_common(data, fields):
    for field in fields:
        value = data.get(field)
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
    return True

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    alumnos = Alumno.query.all()
    return jsonify([a.to_dict() for a in alumnos]), 200

@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = Alumno.query.get(id)
    if alumno:
        return jsonify(alumno.to_dict()), 200
    return jsonify({"error": "Alumno no encontrado"}), 404

@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()
    required_fields = ["nombres", "apellidos", "matricula", "promedio"]
    
    if not validate_common(data, required_fields):
        return jsonify({"error": "Datos incompletos o inválidos"}), 400
    
    try:
        promedio_val = float(data['promedio'])
    except (ValueError, TypeError):
        return jsonify({"error": "El promedio debe ser un número"}), 400

    nuevo_alumno = Alumno(
        nombres=data['nombres'],
        apellidos=data['apellidos'],
        matricula=data['matricula'],
        promedio=promedio_val,
        password=data.get('password', '123456') 
    )
    db.session.add(nuevo_alumno)
    db.session.commit()
    return jsonify(nuevo_alumno.to_dict()), 201

@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    
    data = request.get_json()
    
    if 'nombres' in data: 
        if data['nombres'] is None or (isinstance(data['nombres'], str) and data['nombres'].strip() == ""):
             return jsonify({"error": "El nombre no puede ser nulo o vacío"}), 400
        alumno.nombres = data['nombres']
        
    if 'apellidos' in data: 
        if data['apellidos'] is None or (isinstance(data['apellidos'], str) and data['apellidos'].strip() == ""):
             return jsonify({"error": "El apellido no puede ser nulo o vacío"}), 400
        alumno.apellidos = data['apellidos']

    if 'matricula' in data: 
        if data['matricula'] is None or (isinstance(data['matricula'], str) and data['matricula'].strip() == ""):
             return jsonify({"error": "La matricula no puede ser nula o vacía"}), 400
        alumno.matricula = data['matricula']

    if 'promedio' in data: 
        try:
            promedio_val = float(data['promedio'])
            alumno.promedio = promedio_val
        except (ValueError, TypeError):
            return jsonify({"error": "El promedio debe ser un número válido"}), 400
    
    db.session.commit()
    return jsonify(alumno.to_dict()), 200

@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404
    
    db.session.delete(alumno)
    db.session.commit()
    return jsonify({"mensaje": "Alumno eliminado"}), 200

@app.route('/alumnos/<int:id>/fotoPerfil', methods=['POST'])
def upload_foto_perfil(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404

    if 'foto' not in request.files:
        return jsonify({"error": "No se envió el archivo 'foto'"}), 400

    file = request.files['foto']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    s3 = get_aws_client('s3')
    filename = f"fotos_perfil/{id}_{file.filename}"

    try:
        s3.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            filename,
            ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type} 
        )

        url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{filename}"
        
        alumno.fotoPerfilUrl = url
        db.session.commit()

        return jsonify({"mensaje": "Foto subida", "url": url, "fotoPerfilUrl": url}), 200
    except Exception as e:
        return jsonify({"error": f"Error al subir a S3: {str(e)}"}), 500

@app.route('/alumnos/<int:id>/email', methods=['POST'])
def send_email_sns(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404

    sns = get_aws_client('sns')
    mensaje = (f"Reporte de Calificaciones UADY\n\n"
               f"Alumno: {alumno.nombres} {alumno.apellidos}\n"
               f"Matrícula: {alumno.matricula}\n"
               f"Promedio General: {alumno.promedio}")

    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=mensaje,
            Subject=f"Calificaciones de {alumno.nombres}"
        )
        return jsonify({"mensaje": "Correo enviado vía SNS", "messageId": response['MessageId']}), 200
    except Exception as e:
        return jsonify({"error": f"Error al enviar SNS: {str(e)}"}), 500

@app.route('/alumnos/<int:id>/session/login', methods=['POST'])
def login(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        return jsonify({"error": "Alumno no encontrado"}), 404

    data = request.get_json()
    password_input = data.get('password')

    if not alumno.password or alumno.password != password_input:
        return jsonify({"error": "Contraseña incorrecta"}), 400

    dynamo = get_aws_client('dynamodb')
    
    session_id = str(uuid.uuid4())
    fecha = int(time.time())
    session_string = secrets.token_hex(64) 

    item = {
        'id': {'S': session_id}, 
        'fecha': {'N': str(fecha)},
        'alumnoId': {'N': str(id)},
        'active': {'BOOL': True},
        'sessionString': {'S': session_string}
    }

    try:
        dynamo.put_item(TableName=DYNAMO_TABLE_NAME, Item=item)
        return jsonify({
            "mensaje": "Login exitoso",
            "sessionString": session_string
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error en login DynamoDB: {str(e)}"}), 500

@app.route('/alumnos/<int:id>/session/verify', methods=['POST'])
def verify_session(id):
    data = request.get_json()
    session_string = data.get('sessionString')

    if not session_string:
        return jsonify({"error": "Falta sessionString"}), 400

    dynamo = get_aws_client('dynamodb')

    try:
        response = dynamo.scan(
            TableName=DYNAMO_TABLE_NAME,
            FilterExpression='sessionString = :s AND alumnoId = :a',
            ExpressionAttributeValues={
                ':s': {'S': session_string},
                ':a': {'N': str(id)}
            }
        )

        items = response.get('Items', [])
        
        if not items:
            return jsonify({"error": "Sesión inválida"}), 400

        session = items[0]
        is_active = session.get('active', {}).get('BOOL', False)

        if is_active:
            return jsonify({"mensaje": "Sesión válida", "active": True}), 200
        else:
            return jsonify({"error": "Sesión inactiva"}), 400 

    except Exception as e:
        return jsonify({"error": f"Error al verificar sesión DynamoDB: {str(e)}"}), 500

@app.route('/alumnos/<int:id>/session/logout', methods=['POST'])
def logout(id):
    data = request.get_json()
    session_string = data.get('sessionString')

    if not session_string:
        return jsonify({"error": "Falta sessionString"}), 400

    dynamo = get_aws_client('dynamodb')

    try:
        response = dynamo.scan(
            TableName=DYNAMO_TABLE_NAME,
            FilterExpression='sessionString = :s AND alumnoId = :a',
            ExpressionAttributeValues={
                ':s': {'S': session_string},
                ':a': {'N': str(id)}
            }
        )
        items = response.get('Items', [])
        if not items:
            return jsonify({"error": "Sesión no encontrada"}), 400

        session_uuid = items[0]['id']['S']

        dynamo.update_item(
            TableName=DYNAMO_TABLE_NAME,
            Key={'id': {'S': session_uuid}},
            UpdateExpression='SET active = :val',
            ExpressionAttributeValues={':val': {'BOOL': False}}
        )
        
        return jsonify({"mensaje": "Logout exitoso"}), 200

    except Exception as e:
        return jsonify({"error": f"Error en logout DynamoDB: {str(e)}"}), 500

@app.route('/profesores', methods=['GET'])
def get_profesores():
    profesores = Profesor.query.all()
    return jsonify([p.to_dict() for p in profesores]), 200

@app.route('/profesores/<int:id>', methods=['GET'])
def get_profesor(id):
    profesor = Profesor.query.get(id)
    if profesor: return jsonify(profesor.to_dict()), 200
    return jsonify({"error": "Profesor no encontrado"}), 404

@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()
    required_fields = ["numeroEmpleado", "nombres", "apellidos", "horasClase"]

    if not validate_common(data, required_fields):
        return jsonify({"error": "Datos incompletos o inválidos"}), 400
    
    try:
        horasClase_val = int(data['horasClase'])
        if isinstance(data['horasClase'], float) and data['horasClase'] % 1 != 0:
            return jsonify({"error": "Las horas clase deben ser un número entero"}), 400

    except (ValueError, TypeError):
        return jsonify({"error": "Las horas clase deben ser un número entero"}), 400
    
    nuevo_profesor = Profesor(
        numeroEmpleado=data['numeroEmpleado'],
        nombres=data['nombres'],
        apellidos=data['apellidos'],
        horasClase=horasClase_val
    )
    db.session.add(nuevo_profesor)
    db.session.commit()
    return jsonify(nuevo_profesor.to_dict()), 201

@app.route('/profesores/<int:id>', methods=['PUT'])
def update_profesor(id):
    profesor = Profesor.query.get(id)
    if not profesor: return jsonify({"error": "Profesor no encontrado"}), 404
    
    data = request.get_json()
    
    for field in ['nombres', 'apellidos', 'numeroEmpleado']:
        if field in data:
            if data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                return jsonify({"error": f"El campo {field} no puede ser nulo o vacío"}), 400
            setattr(profesor, field, data[field])
    
    if 'horasClase' in data: 
        try:
            horasClase_val = int(data['horasClase'])
            if isinstance(data['horasClase'], float) and data['horasClase'] % 1 != 0:
                return jsonify({"error": "Las horas clase deben ser un número entero válido"}), 400
            
            profesor.horasClase = horasClase_val

        except (ValueError, TypeError):
            return jsonify({"error": "Las horas clase deben ser un número entero válido"}), 400
    
    db.session.commit()
    return jsonify(profesor.to_dict()), 200

@app.route('/profesores/<int:id>', methods=['DELETE'])
def delete_profesor(id):
    profesor = Profesor.query.get(id)
    if not profesor: return jsonify({"error": "Profesor no encontrado"}), 404
    db.session.delete(profesor)
    db.session.commit()
    return jsonify({"mensaje": "Profesor eliminado"}), 200

if __name__ == '__main__':
    print("[OK] Servidor Flask corriendo con BD, S3, SNS y DynamoDB")
    app.run(host='0.0.0.0', port=3000)
