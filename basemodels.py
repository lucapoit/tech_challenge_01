from pydantic import BaseModel

class Book(BaseModel):
    id : str
    title : str = None
    category : str = None
    price : float = None
    rating : int = None
    availability : int = None
    image_links : str = None


class PredictionInput(BaseModel):
    feature1: float
    feature2: float
