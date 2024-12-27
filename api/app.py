from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///evento_futebol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos do banco de dados
class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    local = db.Column(db.String(100), nullable=False)
    slots_primarios = db.Column(db.Integer, nullable=False)
    slots_goleiros = db.Column(db.Integer, nullable=False)
    slots_espera = db.Column(db.Integer, nullable=False)

class Jogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    posicao = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'principais', 'goleiros', 'espera'
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)



@app.after_request
def aplicar_codificacao(response):
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


# Substituir o decorador @app.before_first_request
@app.before_request
def inicializar_banco():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()  # Cria as tabelas no banco de dados
        app.db_initialized = True


# Endpoints da API
@app.route('/evento', methods=['POST'])
def criar_evento_api():
    dados = request.json

    # Criar o novo evento
    novo_evento = Evento(
        data=dados['data'],
        hora=dados['hora'],
        local=dados['local'],
        slots_primarios=dados['slots_primarios'],
        slots_goleiros=dados['slots_goleiros'],
        slots_espera=dados['slots_espera']
    )
    db.session.add(novo_evento)
    db.session.commit()

    # Adicionar jogadores, se fornecidos
    jogadores = dados.get('jogadores', [])
    for jogador_data in jogadores:
        posicao = jogador_data.get('posicao', 'jogador')
        status = 'principais' if posicao == 'jogador' else 'goleiros'

        if status == 'principais' and Jogador.query.filter_by(evento_id=novo_evento.id, status='principais').count() < novo_evento.slots_primarios:
            jogador = Jogador(nome=jogador_data['nome'], posicao=posicao, status='principais', evento_id=novo_evento.id)
        elif status == 'goleiros' and Jogador.query.filter_by(evento_id=novo_evento.id, status='goleiros').count() < novo_evento.slots_goleiros:
            jogador = Jogador(nome=jogador_data['nome'], posicao=posicao, status='goleiros', evento_id=novo_evento.id)
        elif Jogador.query.filter_by(evento_id=novo_evento.id, status='espera').count() < novo_evento.slots_espera:
            jogador = Jogador(nome=jogador_data['nome'], posicao=posicao, status='espera', evento_id=novo_evento.id)
        else:
            return jsonify({"status": "erro", "mensagem": f"Não foi possível adicionar o jogador {jogador_data['nome']} devido à falta de slots disponíveis."})

        db.session.add(jogador)

    db.session.commit()
    return jsonify({"status": "sucesso", "mensagem": "Evento e jogadores criados com sucesso.", "evento_id": novo_evento.id})


@app.route('/evento/<int:evento_id>', methods=['GET'])
def mostrar_evento_api(evento_id):
    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"status": "erro", "mensagem": "Evento não encontrado."})

    jogadores = Jogador.query.filter_by(evento_id=evento.id).all()
    jogadores_dict = {
        "principais": [j.nome for j in jogadores if j.status == 'principais'],
        "goleiros": [j.nome for j in jogadores if j.status == 'goleiros'],
        "espera": [j.nome for j in jogadores if j.status == 'espera']
    }

    return jsonify({
        "data": evento.data,
        "hora": evento.hora,
        "local": evento.local,
        "jogadores": jogadores_dict
    })


@app.route('/jogador', methods=['POST'])
def adicionar_jogador_api():
    dados = request.json
    evento_id = dados.get('evento_id')  # Agora esperamos o evento_id no corpo da requisição
    
    # Buscar o evento pelo ID
    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"status": "erro", "mensagem": "Evento não encontrado."})

    posicao = dados.get('posicao', 'jogador')
    status = 'principais' if posicao == 'jogador' else 'goleiros'

    if status == 'principais' and Jogador.query.filter_by(evento_id=evento.id, status='principais').count() < evento.slots_primarios:
        jogador = Jogador(nome=dados['nome'], posicao=posicao, status='principais', evento_id=evento.id)
    elif status == 'goleiros' and Jogador.query.filter_by(evento_id=evento.id, status='goleiros').count() < evento.slots_goleiros:
        jogador = Jogador(nome=dados['nome'], posicao=posicao, status='goleiros', evento_id=evento.id)
    elif Jogador.query.filter_by(evento_id=evento.id, status='espera').count() < evento.slots_espera:
        jogador = Jogador(nome=dados['nome'], posicao=posicao, status='espera', evento_id=evento.id)
    else:
        return jsonify({"status": "erro", "mensagem": "Todos os slots estão cheios."})

    db.session.add(jogador)
    db.session.commit()
    return jsonify({"status": "sucesso", "mensagem": f"{dados['nome']} adicionado como {posicao}"})


@app.route('/jogador', methods=['DELETE'])
def remover_jogador_api():
    dados = request.json
    nome_jogador = dados.get('nome')
    evento_id = dados.get('evento_id')  # Esperando o evento_id na requisição
    
    # Buscar o evento pelo ID
    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"status": "erro", "mensagem": "Evento não encontrado."})
    
    # Buscar o jogador pelo nome e evento_id
    jogador = Jogador.query.filter_by(nome=nome_jogador, evento_id=evento.id).first()
    if not jogador:
        return jsonify({"status": "erro", "mensagem": f"{nome_jogador} não encontrado no evento."})

    db.session.delete(jogador)
    db.session.commit()
    return jsonify({"status": "sucesso", "mensagem": f"{nome_jogador} removido do evento."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

