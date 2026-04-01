# =============================================
# routes/transacoes.py
# =============================================

from flask import Blueprint, request, jsonify
from config import get_connection

transacoes_bp = Blueprint("transacoes", __name__)

TIPOS_VALIDOS = {"ENTRADA", "SAIDA"}


# --------------------------------------------------
# POST /transacoes
# --------------------------------------------------
@transacoes_bp.route("/transacoes", methods=["POST"])
def criar_transacao():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou vazio."}), 400

    # Validações básicas
    erros = []
    conta_id = dados.get("conta_id")
    tipo = dados.get("tipo_transacao", "").strip().upper()
    valor = dados.get("valor")
    descricao = dados.get("descricao", "").strip()

    if not conta_id:
        erros.append("conta_id é obrigatório.")
    if not tipo:
        erros.append("tipo_transacao é obrigatório.")
    elif tipo not in TIPOS_VALIDOS:
        erros.append(f"tipo_transacao deve ser ENTRADA ou SAIDA.")
    if valor is None:
        erros.append("valor é obrigatório.")
    elif float(valor) <= 0:
        erros.append("valor deve ser maior que zero.")

    if erros:
        return jsonify({"erros": erros}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verifica se a conta existe
        cursor.execute("SELECT id, saldo FROM contas WHERE id = %s", (conta_id,))
        conta = cursor.fetchone()
        if not conta:
            return jsonify({"erro": "Conta não encontrada."}), 404

        saldo_atual = float(conta["saldo"])
        valor_float = float(valor)

        # Verifica saldo suficiente para saída
        if tipo == "SAIDA" and valor_float > saldo_atual:
            return jsonify({"erro": "Saldo insuficiente para esta transação."}), 422

        # Atualiza saldo da conta
        if tipo == "ENTRADA":
            novo_saldo = saldo_atual + valor_float
        else:
            novo_saldo = saldo_atual - valor_float

        cursor.execute("UPDATE contas SET saldo = %s WHERE id = %s", (novo_saldo, conta_id))

        # Insere a transação
        cursor.execute(
            """
            INSERT INTO transacoes (conta_id, tipo_transacao, descricao, valor)
            VALUES (%s, %s, %s, %s)
            """,
            (conta_id, tipo, descricao, valor_float)
        )
        transacao_id = cursor.lastrowid

        conn.commit()

        return jsonify({
            "mensagem": "Transação realizada com sucesso!",
            "transacao_id": transacao_id,
            "novo_saldo": round(novo_saldo, 2)
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------
# GET /transacoes/conta/<conta_id>
# --------------------------------------------------
@transacoes_bp.route("/transacoes/conta/<int:conta_id>", methods=["GET"])
def transacoes_por_conta(conta_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, conta_id, tipo_transacao, descricao, valor, data_transacao
            FROM transacoes
            WHERE conta_id = %s
            ORDER BY data_transacao DESC
            """,
            (conta_id,)
        )
        transacoes = cursor.fetchall()

        for t in transacoes:
            t["valor"] = float(t["valor"])
            if t.get("data_transacao"):
                t["data_transacao"] = str(t["data_transacao"])

        return jsonify({"transacoes": transacoes}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()