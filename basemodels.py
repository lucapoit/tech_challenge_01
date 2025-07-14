from pydantic import BaseModel, Field
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from db_utils import log_event 

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response: Response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Handles unexpected exceptions or HTTPException in your routes
            status_code = 500
            raise e  # Still raise the exception to return correct error
        finally:
            # Log regardless of outcome
            endpoint = request.url.path
            log_event(endpoint, status_code)

        return response


class Book(BaseModel):
    id : str
    title : str = Field(None, description='Título do livro')
    category : str = Field(None, description='Categoria do livro')
    price : float = Field(None, description='Preço do livro')
    rating : int = Field(None, description='Avaliação do livro (0-5)')
    availability : int = Field(None, description='Disponibilidade do livro')
    image_links : str = Field(None, description='URL da imagem do livro')


class PredictionInput(BaseModel):
    feature1: float
    feature2: float
