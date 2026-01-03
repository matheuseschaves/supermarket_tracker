# 🛒 Supermarket Price Tracker

Aplicativo desktop desenvolvido em Python para acompanhamento, comparação e análise histórica de preços de supermercado.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)

## ✨ Funcionalidades

- **📝 Registro de Compras**: Registre compras com preço, quantidade, data, promoção e quem pagou
- **🔍 Consulta Inteligente**: Compare preços entre supermercados e períodos com filtros avançados
- **📊 Gráficos e Estatísticas**: Visualize a evolução de preços e gere relatórios por produto
- **📦 Gerenciamento Completo**: Cadastre, edite e exclua produtos, supermercados e categorias
- **💾 Backup Automático**: Sistema automático de backup do banco de dados SQLite
- **✅ Validação Robusta**: Validação em tempo real de dados e prevenção de erros

## 🚀 Começando

### Pré-requisitos

- Python 3.8 ou superior
- Gerenciador de pacotes pip

### Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/matheuseschaves/supermarket_tracker.git
   cd supermarket_tracker

2. (Recomendado) Crie um ambiente virtual

bash
# No Windows
python -m venv venv
venv\Scripts\activate

# No Linux/Mac
python3 -m venv venv
source venv/bin/activate

3.Instale as dependências
pip install -r requirements.txt

4.Execute a aplicação
python main.py

🏗️ Estrutura do Projeto
supermarket_tracker/
├── app/                 # Lógica principal do aplicativo
├── gui/                # Interface gráfica
├── reports/            # Geração de relatórios e gráficos
├── backups/            # Backups automáticos do banco de dados
├── main.py            # Ponto de entrada da aplicação
├── requirements.txt   # Dependências do projeto
└── README.md         # Esta documentação

🛠️ Tecnologias Utilizadas
Python - Linguagem principal

Tkinter - Framework para interface gráfica

SQLite - Banco de dados embutido

Matplotlib - Geração de gráficos e visualizações

Git - Controle de versão

📋 Roadmap de Funcionalidades
Sistema básico de registro e consulta

Gráficos de evolução de preços

Campo "Quem pagou" nas compras

Sistema de listas de compra

Dashboard com resumo financeiro

Exportação para Excel/CSV

🤝 Como Contribuir
Contribuições são bem-vindas! Siga estes passos:

Faça um Fork do projeto

Crie uma Branch para sua Feature (git checkout -b feature/NovaFuncionalidade)

Commit suas mudanças (git commit -m 'Adiciona nova funcionalidade')

Push para a Branch (git push origin feature/NovaFuncionalidade)

Abra um Pull Request

📄 Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.

✉️ Contato
Matheus Eschaves - GitHub

Link do Projeto: https://github.com/matheuseschaves/supermarket_tracker
