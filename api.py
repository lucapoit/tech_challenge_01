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
    description='Projeto criado para o tech challenge 01 do curso de pós-graduação em Engenharia de Machine Learning na FIAP.'
)

app.add_middleware(LoggingMiddleware)

router = APIRouter(
    prefix="/api/v1"
)


@app.get('/', tags=['HOMEPAGE'])
async def home():
    return 'hello world'


# POST /login to get JWT token
@router.post("/auth/login", tags=['LOGIN'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


# GET /protected that requires JWT token
@router.get("/scraping/trigger", tags=['ADMIN'])
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Olá, {current_user}. Você tem permissão para iniciar o Scraping."}



@router.get('/books', tags=['BOOKS'])
async def get_items():
    return books.to_dict(orient='records')


@router.get('/books/search', tags=['BOOKS'])
async def get_book_by_name(title:str, category:str):

    filtered_books = books[
        (books['title'].str.strip().str.lower() == title.strip().lower()) &
        (books['category'].str.strip().str.lower() == category.strip().lower())
    ]

    if filtered_books.empty:
        raise HTTPException(status_code=404, detail='item nao encontrado')
    return filtered_books.to_dict(orient='records')[0]


@router.get('/categories', tags=['BOOKS'])
async def get_categories():

    try:
        return books['category'].dropna().unique().tolist()
    
    except Exception as e:
        raise HTTPException(status_code=404, detail='coleção nao encontrada')


@router.get('/books/top-rated', tags=['INSIGHTS'])
async def get_top_rated_books():
    try:
        return  books.sort_values(by=['rating','price','availability'], ascending=False).head(30).to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"nenhum livro encontrado: {str(e)}")
    

@router.get('/books/price-range', tags=['INSIGHTS'])
async def get_book_by_price(min:float, max:float):
    try:
        return books[(books['price']>=min) & (books['price']<=max)].to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Nenhum livro encontrado nesse intervalo de preço: {str(e)}")


@router.get('/books/{id}', tags=['BOOKS'])
async def get_book(id:str):
    book = books[books['id'] == id]
    if book.empty:
        raise HTTPException(status_code=404, detail='item nao encontrado')
    return book.to_dict(orient='records')[0]


@router.get('/health', tags=['HEALTH'])
async def health_check():
    try:

        total_books = len(books)
        return {
            "status": "ok",
            "mensagem": "API está funcionando corretamente",
            "total de livros": total_books
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check falhou: {str(e)}")


@router.get('/stats/overview', tags=['INSIGHTS'])
async def stats_overview():
    try:

        return {
            "total de livros": len(books),
            "preço médio": books['price'].mean(),
            "ratings": books['rating'].value_counts().to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"coleção nao encontrada: {str(e)}")

@router.get('/ml/features', tags=['ML READY'])
async def get_features():
    try: 
        features = pd.DataFrame()
        features[['x1_availability','x2_rating']] = books[['availability','rating']]
        return features.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=404, detail='coleção não encontradas')
    
@router.get('/ml/training-data', tags=['ML READY'])
async def get_training_data():
    try: 
        training_data = pd.DataFrame()
        training_data[['x1_availability','x2_rating','y_labels_price']] = books[['availability','rating','price']].sample(frac=0.8)
        return training_data.to_dict(orient='records')
    
    except Exception as e:
        raise HTTPException(status_code=404, detail='coleção não encontradas')


@router.post('/ml/predictions', tags=['ML READY'])
async def receive_predictions(input: PredictionInput):
    try: 
        return fake_model(input)
    except Exception as e:
        raise HTTPException(status_code=404, detail='features inválidas')

app.include_router(router)