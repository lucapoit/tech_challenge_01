'''
Esse módulo faz o scraping de todo o conteúdo relevante da pagina 'https://books.toscrape.com/'
Para cada livro na página é extraído seu respectivo:
    -id
    -titulo
    -categoria
    -disponibilidade em estoque
    -rating
    -link da capa
    -preço

autores: Luca Poit, Gabriel Jordan, Marcio Lima, Luciana Ferreira, Felipe Guerreiro
'''

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor

BASE_URL = 'https://books.toscrape.com/'
session = requests.Session()

# Inicializa listas para os dados
ids, categories, avaiability, image_links, titles, prices, ratings = [], [], [], [], [], [], []

# Função para extrair links de todas as páginas de categoria e suas páginas seguintes
def get_all_category_pages():
    response = session.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    category_pages = []

    for link in links:
        if 'catalogue/category/books/' in link['href']:
            href = link['href']
            if href.startswith('../'):
                continue  # ignora links duplicados e relativos acima da raiz
            full_link = BASE_URL + href
            # pula se já foi adicionado
            if full_link in category_pages:
                continue

            # agora percorre todas as páginas dessa categoria
            while True:
                category_pages.append(full_link)
                category_soup = BeautifulSoup(session.get(full_link).content, 'html.parser')
                next_page_link = category_soup.find('li', class_="next")
                if next_page_link:
                    next_href = next_page_link.find('a')['href']
                    base = '/'.join(full_link.split('/')[:-1])  # remove a parte do arquivo
                    full_link = base + '/' + next_href
                    #print(full_link)
                else:
                    break  # fim da paginação da categoria

    return list(set(category_pages))  # remove duplicatas


# Função que extrai as URLs de detalhe dos livros em uma página
def get_books_urls_from_category_page(url):
    soup = BeautifulSoup(session.get(url).content, 'html.parser')
    books = soup.find_all(class_="product_pod")
    urls = []
    for book in books:
        id_link = book.find('h3').find('a')['href']
        id_link = id_link.replace('../../../', '')
        full_url = BASE_URL + 'catalogue/' + id_link
        urls.append((full_url, url))  # inclui a URL da categoria para extrair depois
    return urls

# Função que extrai as informações de um único livro
def get_book_info(args):
    url, category_page = args
    try:
        id_soup = BeautifulSoup(session.get(url).content, 'html.parser')

        # ID
        id_table = id_soup.find('table', class_='table table-striped')
        product_id = id_table.find('tr').find('td').text.strip()

        # Título
        title = id_soup.find('div', class_='col-sm-6 product_main').find('h1').text.strip()

        # Rating
        tag = id_soup.find('p', class_='star-rating')
        rating_class = tag.get('class')[1]
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        numeric_rating = rating_map.get(rating_class, 0)

        # Preço
        price_tag = id_soup.find('p', class_='price_color').text.strip()
        price = price_tag.replace('£', '')

        # Estoque
        stock_text = id_soup.find('p', class_='instock availability').text.strip()
        match = re.search(r'\((\d+)\s+available\)', stock_text)
        stock_number = int(match.group(1)) if match else 0

        # Imagem
        image_tag = id_soup.find('img')['src']
        image_url = BASE_URL + image_tag.replace('../../', '')

        # Categoria
        category = category_page.split('/')[-2].split('_')[0]

        return (product_id, title, category, price, numeric_rating, stock_number, image_url)

    except Exception as e:
        print(f"Erro ao processar {url}: {e}")
        return None

# Coleta todas as páginas de categoria
category_pages = get_all_category_pages()

# Coleta todas as URLs de livros
all_book_urls = []
for category_page in category_pages:
    all_book_urls += get_books_urls_from_category_page(category_page)

# Usa paralelismo para coletar dados de cada livro
with ThreadPoolExecutor(max_workers=16) as executor:
    results = list(executor.map(get_book_info, all_book_urls))

# Filtra resultados válidos
for result in results:
    if result:
        product_id, title, category, price, numeric_rating, stock_number, image_url = result
        ids.append(product_id)
        titles.append(title)
        categories.append(category)
        prices.append(price)
        ratings.append(numeric_rating)
        avaiability.append(stock_number)
        image_links.append(image_url)

# Gera o DataFrame
books_df = pd.DataFrame({
    'id': ids,
    'title': titles,
    'category': categories,
    'price': prices,
    'rating': ratings,
    'availability': avaiability,
    'image_links': image_links
})

# Exporta CSV
books_df.to_csv('books.csv', index=False)



            

