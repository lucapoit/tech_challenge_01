'''
Esse módulo define os endpoints da API:

• GET /api/v1/books: Lista todos os livros disponíveis na base de dados. 
• GET /api/v1/books/{id}: Retorna detalhes completos de um livro 
específico pelo ID. 
• GET /api/v1/books/search?title={title}&category={category}: Busca 
livros por título e/ou categoria. 
• GET /api/v1/categories: Lista todas as categorias de livros disponíveis. 
• GET /api/v1/health: Verifica status da API e conectividade com os 
dados. 
• GET /api/v1/stats/overview: Estatísticas gerais da coleção (total de 
livros, preço médio, distribuição de ratings). 
• GET /api/v1/stats/categories: Estatísticas detalhadas por categoria 
(quantidade de livros, preços por categoria). 
• GET /api/v1/books/top-rated: Lista os livros com melhor avaliação 
(rating mais alto). 
• GET /api/v1/books/price-range?min={min}&max={max}: Filtra livros 
dentro de uma faixa de preço específica.

• GET /api/v1/ml/features - Dados formatados para features. 
• GET /api/v1/ml/training-data - Dataset para treinamento. 
• POST /api/v1/ml/predictions - Endpoint para receber predições.

• POST /api/v1/auth/login - Gera um token usado para acessar rotas protegidas. 
• GET /api/v1/ml/scraping/trigger - endpoint protegido que simula um ativador do scraping. 

OBS: a fins de teste, o usuário autorizado tem credenciais

username: luca 
senha: secret

autores: Luca Poit, Gabriel Jordan, Marcio Lima, Luciana Ferreira

a database com logs é um banco postgresSQL instanciada com o NEON
o deploy da API foi feito usando Heroku
o deploy do dashboard com logs foi feito usando streamlit

'''
from dotenv import load_dotenv
load_dotenv()  # Esta função carrega as variáveis do arquivo .env

from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from basemodels import Book, PredictionInput
import pandas as pd
from ml_model import fake_model 
from auth_utils import get_current_user, authenticate_user, verify_password, create_access_token
from basemodels import LoggingMiddleware

books = pd.read_csv('books.csv')

app = FastAPI(
    title = 'API para consulta de livros',
    version='1.0.0',
    description=(
        "Uma API para extrair e consultar dados de livros do site 'books.toscrape.com'. \n"
        "Esta API permite buscar livros, ver estatísticas e obter dados para modelos de Machine Learning."
    )
)

app.add_middleware(LoggingMiddleware)

router = APIRouter(
    prefix="/api/v1"
)


@app.get('/', tags=['HOMEPAGE'], summary='Página Inicial da API.')
async def home():
    """
    Retorna uma mensagem de boas-vindas para indicar que a API está
    funcionando corretamente.
    """
    return {"message": "Bem-vindo à API de Livros! Acesse /docs para ver a documentação interativa."}


# POST /login to get JWT token
@router.post("/auth/login", tags=['LOGIN'], summary='Autentica um usuário e retorna um token JWT.')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Recebe credenciais de usuário (username e password) via formulário OAuth2.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# GET /protected that requires JWT token
@router.get("/scraping/trigger", tags=['ADMIN'], summary='Inicia o processo de scraping (requer autenticação).')
async def protected_route(current_user: str = Depends(get_current_user)):
    """
    Este é um endpoint protegido que inicia o processo de web scraping
    do site 'books.toscrape.com' para atualizar a base de dados.
    """
    return {"message": f"Olá, {current_user}. Você tem permissão para iniciar o Scraping."}



@router.get('/books', tags=['BOOKS'], summary='Lista todos os livros disponíveis.')
async def get_items():
    """

    Retorna uma lista completa de todos os livros que foram capturados pelo scraping.
    """
    return books.to_dict(orient='records')


@router.get('/books/search', tags=['BOOKS'], summary='Busca um livro específico por título e categoria.')
async def get_book_by_name(title:str, category:str):
    """
    A busca não é sensível a maiúsculas/minúsculas nem a espaços
    em branco no início/fim dos parâmetros.
    """

    filtered_books = books[
        (books['title'].str.strip().str.lower() == title.strip().lower()) &
        (books['category'].str.strip().str.lower() == category.strip().lower())
    ]

    if filtered_books.empty:
        raise HTTPException(status_code=404, detail='item nao encontrado')
    return filtered_books.to_dict(orient='records')[0]


@router.get('/categories', tags=['BOOKS'], summary='Lista todas as categorias de livros existentes.')
async def get_categories():
    """
    Retorna uma lista de strings, onde cada string é uma categoria única
    """

    try:
        return books['category'].dropna().unique().tolist()
    
    except Exception as e:
        raise HTTPException(status_code=404, detail='coleção nao encontrada')


@router.get('/books/top-rated', tags=['INSIGHTS'], summary='Retorna os 30 livros mais bem avaliados.')
async def get_top_rated_books():
    """
    A lista é ordenada por 'rating' (avaliação), 'price' (preço) e 'availability' (disponibilidade)
    """
    try:
        return  books.sort_values(by=['rating','price','availability'], ascending=False).head(30).to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"nenhum livro encontrado: {str(e)}")
    

@router.get('/books/price-range', tags=['INSIGHTS'], summary='Filtra livros por um intervalo de preço.')
async def get_book_by_price(min:float, max:float):
    """
    Retorna todos os livros cujo preço esteja entre o valor `min_price` e `max_price`,
    incluindo os limites.
    """
    try:
        return books[(books['price']>=min) & (books['price']<=max)].to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Nenhum livro encontrado nesse intervalo de preço: {str(e)}")


@router.get('/books/{id}', tags=['BOOKS'], summary='Busca um único livro pelo seu ID.')
async def get_book(id:str):

    book = books[books['id'] == id]
    if book.empty:
        raise HTTPException(status_code=404, detail='item nao encontrado')
    return book.to_dict(orient='records')[0]


@router.get('/health', tags=['HEALTH'], summary='Verifica a saúde e o estado da API.')
async def health_check():
    """
    Retorna o status da aplicação e a quantidade total de livros
    atualmente carregados na memória, servindo como um monitoramento básico.
    """
    try:

        total_books = len(books)
        return {
            "status": "ok",
            "mensagem": "API está funcionando corretamente",
            "total de livros": total_books
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check falhou: {str(e)}")


@router.get('/stats/overview', tags=['INSIGHTS'], summary='Fornece um resumo estatístico da coleção de livros.')
async def stats_overview():
    """
    Calcula e retorna o número total de livros, o preço médio de todos os livros,
    e a contagem de livros para cada nota de avaliação (de 1 a 5 estrelas).
    """
    try:

        return {
            "total de livros": len(books),
            "preço médio": books['price'].mean(),
            "ratings": books['rating'].value_counts().to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"coleção nao encontrada: {str(e)}")

@router.get('/ml/features', tags=['ML READY'], summary='Extrai features prontas para modelos de Machine Learning.')
async def get_features():
    """
    Retorna um conjunto de dados simplificado contendo apenas as features
    `availability` e `rating`, que podem ser usadas para treinar um modelo de ML.
    """
    try: 
        features = pd.DataFrame()
        features[['x1_availability','x2_rating']] = books[['availability','rating']]
        return features.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=404, detail='coleção não encontradas')
    
@router.get('/ml/training-data', tags=['ML READY'], summary='Fornece um conjunto de dados de treinamento (features + label).')
async def get_training_data():
    """
    Retorna uma amostra de 80% dos dados, contendo as features (`availability`, `rating`)
    e o label (`price`), pronto para ser usado no treinamento de um modelo
    de regressão para prever o preço.
    """
    try: 
        training_data = pd.DataFrame()
        training_data[['x1_availability','x2_rating','y_labels_price']] = books[['availability','rating','price']].sample(frac=0.8)
        return training_data.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=404, detail='coleção não encontradas')


@router.post('/ml/predictions', tags=['ML READY'], summary='Prevê o preço de um livro com base em suas features.')
async def receive_predictions(input: PredictionInput):
    """
    Recebe a disponibilidade (`availability`) e a avaliação (`rating`) de um livro
    e utiliza um modelo de Machine Learning (simulado) para prever seu preço.
    """
    try: 
        return fake_model(input)
    except Exception as e:
        raise HTTPException(status_code=404, detail='features inválidas')

app.include_router(router)
