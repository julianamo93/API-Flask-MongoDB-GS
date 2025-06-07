from flask import Flask, request, jsonify
from flask_pymongo import PyMongo                                                                                                         
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)

# 🔗 Conexão com MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/orbis_db"

mongo = PyMongo(app)
comentarios_collection = mongo.db.alertas_climaticos

# 🎯 Rota de boas-vindas
@app.route('/')
def home():
    return jsonify({
        "mensagem": "API - Alertas Climáticos ORBIS"
    }), 200

# 🔸 Criar um novo comentário (alerta)
@app.route('/alertas', methods=['POST'])
def adicionar_alerta():
    data = request.json
    usuario_id = data.get('usuario_id')
    tipo_evento = data.get('tipo_evento')
    comentario = data.get('comentario')
    localizacao = data.get('localizacao')

    if not usuario_id or not tipo_evento or not comentario:
        return jsonify({
            "erro": "Campos usuario_id, tipo_evento e comentario são obrigatórios."
        }), 400

    if tipo_evento not in ["enchente", "chuva_forte", "vento_forte", "outro"]:
        return jsonify({
            "erro": "tipo_evento deve ser: enchente, chuva_forte, vento_forte ou outro."
        }), 400

    novo_alerta = {
        "usuario_id": usuario_id,
        "tipo_evento": tipo_evento,
        "comentario": comentario,
        "localizacao": localizacao if localizacao else "Não informado",
        "data_comentario": datetime.utcnow()
    }

    result = comentarios_collection.insert_one(novo_alerta)

    return jsonify({
        "mensagem": "Alerta registrado com sucesso.",
        "id": str(result.inserted_id)
    }), 201


# 🔸 Listar todos os alertas
@app.route('/alertas', methods=['GET'])
def listar_alertas():
    alertas = []
    for a in comentarios_collection.find():
        alertas.append({
            "id": str(a["_id"]),
            "usuario_id": a["usuario_id"],
            "tipo_evento": a["tipo_evento"],
            "comentario": a["comentario"],
            "localizacao": a["localizacao"],
            "data_comentario": a["data_comentario"].isoformat()
        })
    return jsonify(alertas), 200


# 🔸 Filtrar alertas por tipo de evento
@app.route('/alertas/evento/<tipo_evento>', methods=['GET'])
def listar_por_evento(tipo_evento):
    if tipo_evento not in ["enchente", "chuva_forte", "vento_forte", "outro"]:
        return jsonify({
            "erro": "tipo_evento deve ser: enchente, chuva_forte, vento_forte ou outro."
        }), 400

    alertas = []
    for a in comentarios_collection.find({"tipo_evento": tipo_evento}):
        alertas.append({
            "id": str(a["_id"]),
            "usuario_id": a["usuario_id"],
            "tipo_evento": a["tipo_evento"],
            "comentario": a["comentario"],
            "localizacao": a["localizacao"],
            "data_comentario": a["data_comentario"].isoformat()
        })
    return jsonify(alertas), 200


# 🔸 Buscar alertas por usuário
@app.route('/alertas/usuario/<usuario_id>', methods=['GET'])
def buscar_por_usuario(usuario_id):
    alertas = []
    for a in comentarios_collection.find({"usuario_id": usuario_id}):
        alertas.append({
            "id": str(a["_id"]),
            "usuario_id": a["usuario_id"],
            "tipo_evento": a["tipo_evento"],
            "comentario": a["comentario"],
            "localizacao": a["localizacao"],
            "data_comentario": a["data_comentario"].isoformat()
        })
    return jsonify(alertas), 200


# 🔸 Deletar um alerta pelo ID
@app.route('/alertas/<id>', methods=['DELETE'])
def deletar_alerta(id):
    result = comentarios_collection.delete_one({'_id': ObjectId(id)})

    if result.deleted_count == 1:
        return jsonify({"mensagem": "Alerta deletado com sucesso."}), 200
    else:
        return jsonify({"erro": "Alerta não encontrado."}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
