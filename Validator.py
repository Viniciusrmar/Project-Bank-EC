# =============================================
# validators.py - Funções de validação
# =============================================

import re
from datetime import date, datetime


def validar_email(email: str) -> bool:
    """Verifica se o email tem formato válido."""
    padrao = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(padrao, email))


def validar_data_nascimento(data_str: str):
    """
    Recebe data no formato YYYY-MM-DD.
    Retorna (True, None) se válida, ou (False, "mensagem") se inválida.
    - Não pode ser futura
    - Usuário deve ter pelo menos 18 anos
    """
    try:
        nascimento = datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        return False, "Data de nascimento inválida. Use o formato YYYY-MM-DD."

    hoje = date.today()

    if nascimento >= hoje:
        return False, "Data de nascimento não pode ser futura."

    idade = hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )

    if idade < 18:
        return False, "Usuário deve ter pelo menos 18 anos."

    return True, None


def validar_usuario(dados: dict):
    """
    Valida todos os campos do usuário.
    Retorna lista de erros (vazia se tudo ok).
    """
    erros = []

    nome = dados.get("nome", "").strip()
    if not nome:
        erros.append("Nome é obrigatório.")
    elif len(nome) < 5:
        erros.append("Nome deve ter no mínimo 5 caracteres.")

    email = dados.get("email", "").strip()
    if not email:
        erros.append("Email é obrigatório.")
    elif not validar_email(email):
        erros.append("Email inválido.")

    senha = dados.get("senha", "").strip()
    if not senha:
        erros.append("Senha é obrigatória.")

    data_nasc = dados.get("data_nascimento", "").strip()
    if not data_nasc:
        erros.append("Data de nascimento é obrigatória.")
    else:
        ok, msg = validar_data_nascimento(data_nasc)
        if not ok:
            erros.append(msg)

    cpf = dados.get("cpf", "").strip()
    if not cpf:
        erros.append("CPF é obrigatório.")

    cep = dados.get("cep", "").strip()
    if not cep:
        erros.append("CEP é obrigatório.")

    return erros