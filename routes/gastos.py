# =============================================
# routes/gastos.py
# =============================================

from flask import Blueprint, request, jsonify
from config import get_connection

gastos_bp = Blueprint("gastos", __name__)


# --------------------------------------------------
# POST /gastos
# --------------------------------------------------
@gastos_bp.route("/gastos", methods=["POST"])
def criar_gasto():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou vazio."}), 400

    erros = []
    usuario_id = dados.get("usuario_id")
    categoria  = dados.get("categoria", "").strip()
    valor      = dados.get("valor")
    descricao  = dados.get("descricao", "").strip()

    if not usuario_id:
        erros.append("usuario_id é obrigatório.")
    if not categoria:
        erros.append("categoria é obrigatória.")
    if valor is None:
        erros.append("valor é obrigatório.")
    elif float(valor) <= 0:
        erros.append("valor deve ser maior que zero.")

    if erros:
        return jsonify({"erros": erros}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verifica se o usuário existe
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
        if not cursor.fetchone():
            return jsonify({"erro": "Usuário não encontrado."}), 404

        cursor.execute(
            """
            INSERT INTO gastos (usuario_id, categoria, descricao, valor)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario_id, categoria, descricao, float(valor))
        )
        gasto_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "mensagem": "Gasto cadastrado com sucesso!",
            "gasto_id": gasto_id
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------
# GET /gastos/usuario/<usuario_id>
# --------------------------------------------------
@gastos_bp.route("/gastos/usuario/<int:usuario_id>", methods=["GET"])
def gastos_por_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, usuario_id, categoria, descricao, valor, data_gasto
            FROM gastos
            WHERE usuario_id = %s
            ORDER BY data_gasto DESC
            """,
            (usuario_id,)
        )
        gastos = cursor.fetchall()

        for g in gastos:
            g["valor"] = float(g["valor"])
            if g.get("data_gasto"):
                g["data_gasto"] = str(g["data_gasto"])

        # Total de gastos por categoria
        total_por_categoria = {}
        for g in gastos:
            cat = g["categoria"]
            total_por_categoria[cat] = round(
                total_por_categoria.get(cat, 0) + g["valor"], 2
            )

        return jsonify({
            "gastos": gastos,
            "resumo_por_categoria": total_por_categoria,
            "total_geral": round(sum(g["valor"] for g in gastos), 2)
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()