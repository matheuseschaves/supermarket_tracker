# app/utils.py
from datetime import datetime

def formatar_moeda(valor):
    """Formata um valor float para string de moeda brasileira"""
    if valor is None:
        return "R$ 0,00"
    try:
        return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"


def parsear_data(data_str):
    """Converte string de data para objeto date"""
    try:
        return datetime.strptime(data_str, "%d/%m/%Y").date()
    except ValueError:
        try:
            return datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            return None


def calcular_preco_unitario(preco, quantidade):
    """Calcula o preço unitário"""
    if quantidade is None or quantidade <= 0:
        return 0
    try:
        return float(preco) / float(quantidade)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


def extrair_nome_produto(produto_text):
    """Extrai apenas o nome do produto, removendo a marca se presente"""
    if not produto_text:
        return ""
    
    if '(' in produto_text and ')' in produto_text:
        nome = produto_text.split('(')[0].strip()
        # Remove possíveis espaços extras
        return nome.strip()
    return produto_text.strip()


def extrair_marca_produto(produto_text):
    """Extrai a marca do texto do produto"""
    if not produto_text:
        return ""
    
    if '(' in produto_text and ')' in produto_text:
        try:
            marca = produto_text.split('(')[1].split(')')[0].strip()
            return marca
        except IndexError:
            return ""
    return ""