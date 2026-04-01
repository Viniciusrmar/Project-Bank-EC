# =============================================
# config.py - Configuração do banco de dados
# =============================================
# Ajuste usuario, senha e host conforme seu ambiente local

import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5500,
    "user": "root",
    "password": "L0r3n4@1708",       # <- altere para sua senha
    "database": "bancodigital",
    "charset": "utf8mb4"
}


def get_connection():
    """Retorna uma nova conexão com o banco de dados MySQL."""
    return mysql.connector.connect(**DB_CONFIG)