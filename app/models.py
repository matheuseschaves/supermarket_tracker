# app/models.py
class Produto:
    def __init__(self, nome, categoria_id=None, marca='', unidade_medida='un', qnt_medida=''):
        self.nome = nome
        self.categoria_id = categoria_id
        self.marca = marca
        self.unidade_medida = unidade_medida
        self.qnt_medida = qnt_medida

    def __repr__(self):
        return f"Produto(nome='{self.nome}', marca='{self.marca}')"


class Compra:
    def __init__(self, produto_id, supermercado_id, preco, data_compra,
                 quantidade=1, promocao=False, observacoes=''):
        self.produto_id = produto_id
        self.supermercado_id = supermercado_id
        self.preco = preco
        self.quantidade = quantidade
        self.data_compra = data_compra
        self.promocao = promocao
        self.observacoes = observacoes

    def preco_unitario(self):
        return self.preco / self.quantidade if self.quantidade > 0 else 0


class Supermercado:
    def __init__(self, nome, endereco=''):
        self.nome = nome
        self.endereco = endereco