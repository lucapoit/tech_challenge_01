# 📚 Books API — Web Scraping + API REST + ML

## 📝 Descrição do Projeto

Este projeto consiste em uma solução completa para coleta, exposição e análise de dados de livros via Web Scraping, API RESTful e integração com modelos de Machine Learning.

Os dados são extraídos do site [Books to Scrape](https://books.toscrape.com/), processados e disponibilizados por meio de uma API desenvolvida com FastAPI.

---

## 🔧 Estrutura do Projeto

.
<pre>
├── books.csv                   Arquivo CSV com os livros extraídos

├── users.json                  Arquivo json com o usuário teste com permissões

├── ml_model.py                 Simula o modelo de ML

├── basemodels.py               Classes usadas em outras partes do projeto

├── auht_utils.py               Funções auxiliares de autenticação

├── db_utils.py                 Funções auxiliares de interação com o banco de dados

├── api.py                      Inicialização da aplicação FastAPI

├── streamlit_dashboard.py      Gera o dashboard sobre o funcionamento da API

├── requirements.txt            Dependências

├── Procfile                    Para deploy com Heroku

├── .python-version             Para deploy com Heroku

└── README.md
</pre>
---

## 🚀 Como Executar Localmente

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/books-api.git
cd books-api
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o Web Scraping:
Chame o endpoint api/v1/scraping/trigger (requer autenticação)
```bash
python python scraping.py 
```

5. Inicie a API:
```bash
uvicorn api:app --reload
```

---

## 📚 Endpoints da API

### Endpoints principais

- `GET /api/v1/books`: Lista todos os livros
- `GET /api/v1/books/{id}`: Retorna detalhes de um livro
- `GET /api/v1/books/search?title=...&category=...`: Busca por título e/ou categoria
- `GET /api/v1/categories`: Lista todas as categorias
- `GET /api/v1/health`: Verifica status da API

### Endpoints de estatísticas (opcional)

- `GET /api/v1/stats/overview`: Estatísticas gerais (preço médio, total de livros, etc.)
- `GET /api/v1/stats/categories`: Estatísticas por categoria
- `GET /api/v1/books/top-rated`: Lista os livros com melhor avaliação
- `GET /api/v1/books/price-range?min=...&max=...`: Livros por faixa de preço

### Endpoints para ML (opcional)

- `GET /api/v1/ml/features`: Dados formatados para features
- `GET /api/v1/ml/training-data`: Dados completos para treinamento
- `POST /api/v1/ml/predictions`: Recebe dados e retorna uma predição (fake)

### Endpoints protegidos (opcional)

- `POST /api/v1/auth/login`: Gera token JWT
- `POST /api/v1/scraping/trigger`: Executa novo scraping (rota protegida)

---

## ✅ Exemplo de Requisição

```http
GET /api/v1/books/search?title=python
```

**Resposta:**
```json
[
  {
    "id": "a8f4577a48023344",
    "title": "Learning Python",
    "category": "Programming",
    "price": 45.90,
    "rating": 5,
    "availability": 20
  }
]
```

---

## 🖥️ Deploy Público

O deploy em produção foi feito mas posteriormente removido para evitar gastos.
O uso em produção foi exemplificado no vídeo demonstrativo.

---

## 🧠 Plano Arquitetural

- **Ingestão de dados**: Web scraping automatizado (`scraper.py`)
- **Processamento**: Dados armazenados em CSV
- **API REST**: Disponibiliza os dados via FastAPI
- **ML Ready**: Endpoints simulando predições e extração de features
- **Escalável**: Estrutura modular, fácil de manter e expandir
- **Monitoramento**: Dashboard de monitoramento disponível em [https://tech-challenge-001.streamlit.app/](https://tech-challenge-001.streamlit.app/)

<img width="1920" height="1080" alt="architecture" src="https://github.com/user-attachments/assets/71a5d0df-546b-461e-bf6e-13847ab94304" />


---

## 📹 Apresentação

Vídeo explicativo com execução de chamadas reais e explicação da arquitetura disponível [aqui](#).

---

## 👨‍🔧 Autor

Este projeto foi desenvolvido como parte de um Tech Challenge.
