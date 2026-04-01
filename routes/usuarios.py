# =============================================
# routes/usuarios.py
# =============================================

import random
from flask import Blueprint, request, jsonify
from config import get_connection
from validators import validar_usuario

usuarios_bp = Blueprint("usuarios", __name__)


def gerar_numero_conta():
    """Gera um número de conta aleatório no formato XXXXX-D."""
    numero = random.randint(10000, 99999)
    digito = random.randint(0, 9)
    return f"{numero}-{digito}"


# --------------------------------------------------
# POST /usuarios/cadastro
# --------------------------------------------------
@usuarios_bp.route("/usuarios/cadastro", methods=["POST"])
def cadastrar_usuario():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou vazio."}), 400

    # Validações
    erros = validar_usuario(dados)
    if erros:
        return jsonify({"erros": erros}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verifica duplicidade de email
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (dados["email"],))
        if cursor.fetchone():
            return jsonify({"erro": "Email já cadastrado."}), 409

        # Verifica duplicidade de CPF
        cursor.execute("SELECT id FROM usuarios WHERE cpf = %s", (dados["cpf"],))
        if cursor.fetchone():
            return jsonify({"erro": "CPF já cadastrado."}), 409

        # ATENÇÃO: Em produção real, a senha DEVE ser hasheada com bcrypt ou argon2.
        # Aqui armazenamos em texto puro apenas para simplificar o projeto acadêmico.
        sql_usuario = """
            INSERT INTO usuarios
                (nome, email, senha, data_nascimento, cpf, cep, logradouro, numero, bairro, cidade, estado)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores_usuario = (
            dados["nome"].strip(),
            dados["email"].strip(),
            dados["senha"].strip(),
            dados["data_nascimento"].strip(),
            dados["cpf"].strip(),
            dados["cep"].strip(),
            dados.get("logradouro", ""),
            dados.get("numero", ""),
            dados.get("bairro", ""),
            dados.get("cidade", ""),
            dados.get("estado", ""),
        )
        cursor.execute(sql_usuario, valores_usuario)
        usuario_id = cursor.lastrowid

        # Cria conta automaticamente ao cadastrar usuário
        numero_conta = gerar_numero_conta()
        sql_conta = """
            INSERT INTO contas (usuario_id, numero_conta, agencia, saldo, tipo_conta)
            VALUES (%s, %s, '0001', 0.00, 'CORRENTE')
        """
        cursor.execute(sql_conta, (usuario_id, numero_conta))

        conn.commit()

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso!",
            "usuario_id": usuario_id,
            "conta_criada": {
                "numero_conta": numero_conta,
                "agencia": "0001",
                "saldo_inicial": 0.00
            }
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------
# POST /usuarios/login
# --------------------------------------------------
@usuarios_bp.route("/usuarios/login", methods=["POST"])
def login():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou vazio."}), 400

    email = dados.get("email", "").strip()
    senha = dados.get("senha", "").strip()

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios."}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # ATENÇÃO: Em produção real, compare hash da senha, nunca texto puro.
        cursor.execute(
            "SELECT id, nome, email FROM usuarios WHERE email = %s AND senha = %s",
            (email, senha)
        )
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"erro": "Email ou senha incorretos."}), 401

        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "usuario": usuario
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


# --------------------------------------------------
# GET /usuarios
# --------------------------------------------------
@usuarios_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, nome, email, cpf, cidade, estado, created_at FROM usuarios ORDER BY id"
        )
        usuarios = cursor.fetchall()

        # Converte datas para string (para serialização JSON)
        for u in usuarios:
            if u.get("created_at"):
                u["created_at"] = str(u["created_at"])

        return jsonify({"usuarios": usuarios}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()