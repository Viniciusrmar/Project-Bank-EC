# =============================================
# routes/investimentos.py
# =============================================

from flask import Blueprint, request, jsonify
from config import get_connection

investimentos_bp = Blueprint("investimentos", __name__)

TIPOS_VALIDOS = {
    "RENDA_FIXA", "RENDA_VARIAVEL", "TESOURO_DIRETO",
    "FUNDO", "CRIPTO", "ACAO", "FII", "CDB", "LCI", "LCA"
}


# --------------------------------------------------
# POST /investimentos
# --------------------------------------------------
@investimentos_bp.route("/investimentos", methods=["POST"])
def criar_investimento():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou vazio."}), 400

    erros = []
    usuario_id        = dados.get("usuario_id")
    tipo_investimento = dados.get("tipo_investimento", "").strip().upper()
    nome_ativo        = dados.get("nome_ativo", "").strip()
    valor_aplicado    = dados.get("valor_aplicado")
    rentabilidade     = dados.get("rentabilidade")   # opcional

    if not usuario_id:
        erros.append("usuario_id é obrigatório.")
    if not tipo_investimento:
        erros.append("tipo_investimento é obrigatório.")
    if not nome_ativo:
        erros.append("nome_ativo é obrigatório.")
    if valor_aplicado is None:
        erros.append("valor_aplicado é obrigatório.")
    elif float(valor_aplicado) <= 0:
        erros.append("valor_aplicado deve ser maior que zero.")

    if erros:
        return jsonify({"erros": erros}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verifica se o usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            return jsonify({"erro": "Usuário não encontrado."}), 404

        rent = float(rentabilidade) if rentabilidade is not None else None

        cursor.execute(
            """
            INSERT INTO investimentos
                (usuario_id, tipo_investimento, nome_ativo, valor_aplicado, rentabilidade)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, tipo_investimento, nome_ativo, float(valor_aplicado), rent)
        )
        investimento_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "mensagem": "Investimento cadastrado com sucesso!",
            "investimento_id": investimento_id
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------
# GET /investimentos/usuario/<usuario_id>
# --------------------------------------------------
@investimentos_bp.route("/investimentos/usuario/<int:usuario_id>", methods=["GET"])
def investimentos_por_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, usuario_id, tipo_investimento, nome_ativo,
                   valor_aplicado, rentabilidade, data_aplicacao
            FROM investimentos
            WHERE usuario_id = %s
            ORDER BY data_aplicacao DESC
            """,
            (usuario_id,)
        )
        investimentos = cursor.fetchall()

        total_aplicado = 0.0
        for inv in investimentos:
            inv["valor_aplicado"] = float(inv["valor_aplicado"])
            inv["rentabilidade"]  = float(inv["rentabilidade"]) if inv["rentabilidade"] else None
            if inv.get("data_aplicacao"):
                inv["data_aplicacao"] = str(inv["data_aplicacao"])
            total_aplicado += inv["valor_aplicado"]

        return jsonify({
            "investimentos": investimentos,
            "total_aplicado": round(total_aplicado, 2)
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()