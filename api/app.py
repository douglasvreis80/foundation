from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///partidas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos do banco de dados
class Partida(db.Model):
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
    partida_id = db.Column(db.Integer, db.ForeignKey('partida.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('nome', 'partida_id', name='uq_jogador_partida'),
    )


@app.after_request
def aplicar_codificacao(response):
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.before_request
def inicializar_banco():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()  # Cria as tabelas no banco de dados
        app.db_initialized = True


# Endpoints da API
@app.route('/partida', methods=['POST'])
def criar_partida_api():
    dados = request.json

    # Criar o novo partida
    nova_partida = Partida(
        data=dados['data'],
        hora=dados['hora'],
        local=dados['local'],
        slots_primarios=dados['slots_primarios'],
        slots_goleiros=dados['slots_goleiros'],
        slots_espera=dados['slots_espera']
    )
    db.session.add(nova_partida)
    db.session.commit()

    # Adicionar jogadores, se fornecidos
    jogadores = dados.get('jogadores', [])
    for jogador_data in jogadores:
        posicao = jogador_data.get('posicao', 'jogador')
        status = 'principais' if posicao == 'jogador' else 'goleiros'

        if status == 'principais' and Jogador.query.filter_by(partida_id=nova_partida.id, status='principais').count() < nova_partida.slots_primarios:
            jogador = Jogador(nome=jogador_data['nome'], posicao=posicao, status='principais', partida_id=nova_partida.id)
        elif status == 'goleiros' and Jogador.query.filter_by(partida_id=nova_partida.id, status='goleiros').count() < nova_partida.slots_goleiros:
            jogador = Jogador(nome=jogador_data['nome'], posicao=posicao, status='goleiros', partida_id=nova_partida.id)
        elif Jogador.query.filter_by(partida_id=nova_partida.id, status='espera').count() < nova_partida.slots_espera:
            jogador = Jogador(nome=jogador_data['nome'], posicao=posicao, status='espera', partida_id=nova_partida.id)
        else:
            return jsonify({"status": "erro", "mensagem": f"Não foi possível adicionar o jogador {jogador_data['nome']} devido à falta de vagas disponíveis."})

        db.session.add(jogador)

    db.session.commit()
    return jsonify({"status": "sucesso", "mensagem": "partida e jogadores criados com sucesso.", "partida_id": nova_partida.id})


@app.route('/partida/<int:partida_id>', methods=['GET'])
def mostrar_partida_api(partida_id):
    partida = Partida.query.get(partida_id)
    if not partida:
        return jsonify({"status": "erro", "mensagem": "partida não encontrada."})

    jogadores = Jogador.query.filter_by(partida_id=partida.id).all()
    jogadores_dict = {
        "principais": [j.nome for j in jogadores if j.status == 'principais'],
        "goleiros": [j.nome for j in jogadores if j.status == 'goleiros'],
        "espera": [j.nome for j in jogadores if j.status == 'espera']
    }

    return jsonify({
        "data": partida.data,
        "hora": partida.hora,
        "local": partida.local,
        "jogadores": jogadores_dict
    })


@app.route('/jogador', methods=['POST'])
def adicionar_jogador_api():
    dados = request.json
    partida_id = dados.get('partida_id')  # Agora esperamos o partida_id no corpo da requisição

    # Buscar a partida pelo ID
    partida = Partida.query.get(partida_id)
    if not partida:
        return jsonify({"status": "erro", "mensagem": "Partida não encontrada."}), 404

    # Verificar se o jogador já está associado a essa partida
    jogador_existente = Jogador.query.filter_by(nome=dados['nome'], partida_id=partida.id).first()
    if jogador_existente:
        return jsonify({"status": "erro", "mensagem": f"O jogador {dados['nome']} já está registrado nesta partida."}), 400

    posicao = dados.get('posicao', 'jogador')
    status = 'principais' if posicao == 'jogador' else 'goleiros'

    # Lógica de slots
    if status == 'principais' and Jogador.query.filter_by(partida_id=partida.id, status='principais').count() < partida.slots_primarios:
        jogador = Jogador(nome=dados['nome'], posicao=posicao, status='principais', partida_id=partida.id)
    elif status == 'goleiros' and Jogador.query.filter_by(partida_id=partida.id, status='goleiros').count() < partida.slots_goleiros:
        jogador = Jogador(nome=dados['nome'], posicao=posicao, status='goleiros', partida_id=partida.id)
    elif Jogador.query.filter_by(partida_id=partida.id, status='espera').count() < partida.slots_espera:
        jogador = Jogador(nome=dados['nome'], posicao=posicao, status='espera', partida_id=partida.id)
    else:
        return jsonify({"status": "erro", "mensagem": "Todas as vagas estão ocupadas."}), 400

    db.session.add(jogador)
    db.session.commit()
    return jsonify({"status": "sucesso", "mensagem": f"{dados['nome']} adicionado como {posicao}."}), 201




@app.route('/jogador', methods=['DELETE'])
def remover_jogador_api():
    dados = request.json
    nome_jogador = dados.get('nome')
    partida_id = dados.get('partida_id')  # Esperando o partida_id na requisição
    
    # Buscar o partida pelo ID
    partida = Partida.query.get(partida_id)
    if not partida:
        return jsonify({"status": "erro", "mensagem": "partida não encontrada."})
    
    # Buscar o jogador pelo nome e partida_id
    jogador = Jogador.query.filter_by(nome=nome_jogador, partida_id=partida.id).first()
    if not jogador:
        return jsonify({"status": "erro", "mensagem": f"{nome_jogador} não encontrado no partida."})

    db.session.delete(jogador)
    db.session.commit()
    return jsonify({"status": "sucesso", "mensagem": f"{nome_jogador} removido do partida."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)