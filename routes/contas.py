# =============================================
# routes/contas.py
# =============================================

from flask import Blueprint, jsonify
from config import get_connection

contas_bp = Blueprint("contas", __name__)


# --------------------------------------------------
# GET /contas/usuario/<usuario_id>
# --------------------------------------------------
@contas_bp.route("/contas/usuario/<int:usuario_id>", methods=["GET"])
def contas_por_usuario(usuario_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, usuario_id, numero_conta, agencia, saldo, tipo_conta
            FROM contas
            WHERE usuario_id = %s
            ORDER BY id
            """,
            (usuario_id,)
        )
        contas = cursor.fetchall()

        if not contas:
            return jsonify({"mensagem": "Nenhuma conta encontrada para este usuário.", "contas": []}), 200

        # Converte Decimal para float para serialização JSON
        for c in contas:
            c["saldo"] = float(c["saldo"])

        return jsonify({"contas": contas}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()