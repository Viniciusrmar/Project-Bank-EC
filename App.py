# =============================================
# app.py - Arquivo principal da aplicação
# Sistema Bancário Digital - Projeto Acadêmico
# =============================================
 
from flask import Flask, jsonify
from flask_cors import CORS
 
from routes.usuarios      import usuarios_bp
from routes.contas        import contas_bp
from routes.transacoes    import transacoes_bp
from routes.gastos        import gastos_bp
from routes.investimentos import investimentos_bp
 
# -----------------------------------------------
# Inicialização da aplicação
# -----------------------------------------------
app = Flask(__name__)
 
# CORS liberado para qualquer origem (frontend local)
CORS(app)
 
# -----------------------------------------------
# Registro dos Blueprints (grupos de rotas)
# -----------------------------------------------
app.register_blueprint(usuarios_bp)
app.register_blueprint(contas_bp)
app.register_blueprint(transacoes_bp)
app.register_blueprint(gastos_bp)
app.register_blueprint(investimentos_bp)
 
 
# -----------------------------------------------
# Rota raiz - health check
# -----------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "aplicacao": "Banco Digital API",
        "versao": "1.0.0",
        "rotas_disponiveis": [
            "POST  /usuarios/cadastro",
            "POST  /usuarios/login",
            "GET   /usuarios",
            "GET   /contas/usuario/<usuario_id>",
            "POST  /transacoes",
            "GET   /transacoes/conta/<conta_id>",
            "POST  /gastos",
            "GET   /gastos/usuario/<usuario_id>",
            "POST  /investimentos",
            "GET   /investimentos/usuario/<usuario_id>",
        ]
    }), 200
 
 
# -----------------------------------------------
# Tratamento global de erros
# -----------------------------------------------
@app.errorhandler(404)
def nao_encontrado(e):
    return jsonify({"erro": "Rota não encontrada."}), 404
 
 
@app.errorhandler(405)
def metodo_nao_permitido(e):
    return jsonify({"erro": "Método HTTP não permitido para esta rota."}), 405
 
 
@app.errorhandler(500)
def erro_interno(e):
    return jsonify({"erro": "Erro interno no servidor."}), 500
 
 
# -----------------------------------------------
# Execução
# -----------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("  Banco Digital API rodando!")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)