from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

app = Flask(__name__)

# --- CONFIG ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
# Güvenlik uyarısını gidermek için anahtarı 32 karakterden uzun yaptık
app.config['JWT_SECRET_KEY'] = '9c5afe43064f9f260b452aa90e7911fbe1093a299f34810523e9a3fed0c0cdf4'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_JSON_KEY_STRATEGY'] = lambda x: x

db = SQLAlchemy(app)
jwt = JWTManager(app)

CORS(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}}, supports_credentials=True)


@app.route('/debug/db', methods=['GET'])
def debug_db():
    users = User.query.all()
    tasks = Task.query.all()

    return jsonify({
        "users": [{"id": u.id, "username": u.username, "role": u.role} for u in users],
        "tasks": [{"id": t.id, "title": t.title, "status": t.status, "assigned_to": t.assigned_to} for t in tasks]
    })


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = make_response()
        res.headers.add("Access-Control-Allow-Origin", "*")
        res.headers.add("Access-Control-Allow-Methods", "*")
        res.headers.add("Access-Control-Allow-Headers", "*")
        return res, 200

# --- MODELLER ---


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), default='worker')  # 'leader' veya 'worker'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='todo')
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))

# --- AUTH ENDPOINTS ---


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(
        username=data['username'], password=data['password']).first()

    if user:
        additional_claims = {"role": user.role, "username": user.username}

        token = create_access_token(
            identity=str(user.id),  # ID'yi stringe çeviriyoruz
            additional_claims=additional_claims
        )

        return jsonify({
            "token": token,
            "role": user.role,
            "username": user.username,
            "id": user.id
        }), 200

    return jsonify({"msg": "Hatalı giriş"}), 401


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'worker')

    # Check if username exists
    if User.query.filter_by(username=username).first():
        # 409 Conflict
        return jsonify({"msg": "Bu kullanıcı adı zaten alınmış"}), 409

    try:
        new_user = User(
            username=username,
            password=password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "Kayıt başarılı"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Sunucu hatası oluştu"}), 500


# --- WORKER ENDPOINT ---


@app.route('/workers', methods=['GET'])
@jwt_required()
def get_workers():
    claims = get_jwt()
    role = claims.get('role')

    if role != 'leader':
        return jsonify({"msg": "Yetkiniz yok"}), 403

    workers = User.query.filter_by(role='worker').all()
    return jsonify([{"id": w.id, "username": w.username} for w in workers]), 200

# --- TASK ENDPOINTS ---


@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    claims = get_jwt()
    role = claims.get('role')
    user_id = claims.get('id')

    if role == 'leader':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(assigned_to=user_id).all()

    result = []
    for t in tasks:
        worker = User.query.get(t.assigned_to)
        result.append({
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "assigned_to": t.assigned_to,
            "assigned_name": worker.username if worker else "Atanmamış"
        })
    return jsonify(result), 200


@app.route('/tasks/create', methods=['POST'])
@jwt_required()
def create_task():
    claims = get_jwt()
    role = claims.get('role')

    if role != 'leader':
        return jsonify({"msg": "Sadece liderler görev atayabilir"}), 403

    data = request.json
    new_task = Task(
        title=data['title'],
        assigned_to=data['assigned_to'],
        status='todo'
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({"msg": "Görev başarıyla oluşturuldu"}), 201


@app.route('/tasks/update', methods=['POST'])
@jwt_required()
def update_task():
    data = request.json
    task = Task.query.get(data['id'])
    if not task:
        return jsonify({"msg": "Görev bulunamadı"}), 404

    task.status = data['status']
    db.session.commit()
    return jsonify({"msg": "Güncellendi"}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
