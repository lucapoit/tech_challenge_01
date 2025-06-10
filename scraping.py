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
from io import StringIO  

url = 'https://books.toscrape.com/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

#listas vazias para criação do dataframe
ids=[]
categories = []
avaiability = []
image_links = []
titles = []
prices = []
ratings = []

#encontra os links das sessões da página inicial
links = soup.find_all('a', href=True)

for link in links:

    #confere se o link leva para uma página de catálogo
    if ('catalogue/category/books/' in link['href']):

        category_page = requests.get('https://books.toscrape.com/'+ link['href'])
        category_soup = BeautifulSoup(category_page.content, 'html.parser')
        books = category_soup.find_all(class_ = "product_pod" )        

        #progress-tracking para quando rodar o programa
        #print('https://books.toscrape.com/'+ link['href'])

        next_page_link = category_soup.find('li', class_ = "next" )

        if next_page_link:

            next_page = next_page_link.find('a', href=True)

            if next_page:
                new_link = 'catalogue/category/books/'+ link['href'].split('/')[-2] + '/' + next_page['href']
                next_page['href'] = new_link
                links.append(next_page)

                #progress-tracking para quando rodar o programa
                #print(f'adicionando a pagina {next_page['href']}')

        #extrai infos de cada livro disponibilizado na página
        for book in books:

            #categoria
            category = link['href'].split('/')[-2].split('_')[0]

            #id
            id_div = book.find('div', class_='image_container')
            id_link = id_div.find('a', href=True)
            id_page = requests.get('https://books.toscrape.com/catalogue/'+ id_link['href'].split('/')[3] + '/index.html')
            id_soup = BeautifulSoup(id_page.content, 'html.parser')
            id_table = id_soup.find('table',class_='table table-striped')

            first_row = id_table.find('tr')
            second_column = first_row.find('td')
            product_id = second_column.text.strip()

            #titulo
            title_class = id_soup.find('div', class_='col-sm-6 product_main')
            title = title_class.find('h1').text.strip()

            #rating
            tag = id_soup.find('p', class_='star-rating')
            classes = tag.get('class')
            rating = classes[1]


            rating_map = {
            'One': 1,
            'Two': 2,
            'Three': 3,
            'Four': 4,
            'Five': 5
            }
            numeric_rating = rating_map[rating]

            #preco
            price_class = id_soup.find(class_ = 'col-sm-6 product_main')
            price_tag = price_class.find('p', class_ = 'price_color')
            price = price_tag.text.strip().replace('£', '')

            stock_class = id_soup.find(class_ = 'col-sm-6 product_main')
            stock_tag = stock_class.find('p', class_ = 'instock availability').text.strip()

            match = re.search(r'\((\d+)\s+available\)', stock_tag)
            if match:
                stock_number = int(match.group(1))
            else:
                stock_numer = 0     

            #link da imagem
            image_tag = id_soup.find('img')  
            image_src = image_tag['src']
            image_url = 'https://books.toscrape.com/' + image_src.replace('../../', '')

            #adiciona os elementos as suas respectivas listas
            ids.append(product_id)
            categories.append(category)
            avaiability.append(stock_number)
            image_links.append(image_url)
            titles.append(title)
            prices.append(price)
            ratings.append(numeric_rating)

#cria um dicionário com as listas para gerar o dataframe
books_dict = {'id':ids,'title':titles,'category':categories,'price':prices,'rating':ratings, 'availability':avaiability,'image_links':image_links}

#gera o dataframe
books_df = pd.DataFrame(books_dict)

#exporta o csv
books_df.to_csv('books.csv')



            

