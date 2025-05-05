import os
import re
from os.path import exists
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def input_url():
    return input("Saississez votre url :\n")

def request_url(url):
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status() # lève erreur (ex: 404 etc..)
            return response, url
        except requests.exceptions.RequestException as e: #lève erreur si url non valide
            print("L'URL n'est pas valide :", e)
            print("Veuillez entrez une URL valide")
            continue

def scrap_one_element(url):
    while True:
        response, url = request_url(url)
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            book ={
                "product_page_url": url,
                "universal_product_code(upc)": soup.find("table").find("th", string="UPC").find_next_sibling("td").text , # id "content_inner" => table
                "title": soup.find("h1").text, # h1
                "price_including_tax": soup.find("table").find("th", string="Price (incl. tax)").find_next_sibling("td").text, # id "content_inner" => table
                "price_excluding_tax": soup.find("table").find("th", string="Price (excl. tax)").find_next_sibling("td").text, # id "content_inner" => table
                "number_available": soup.find("table").find("th", string="Availability").find_next_sibling("td").text, # id "content_inner" => table
                "product_description": soup.find("div", id="product_description").find_next_sibling("p").text, # id "product_description" élément suivant p
                "category": soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").text, # ul class "breadcrumb" 3eme li a
                "review_rating": soup.find("p", class_="star-rating")["class"][1], # p class "star-rating" /!\
                "image_url": urljoin("https://books.toscrape.com", soup.find("div", id="product_gallery").find("img")["src"]) # id "product_galery" => img src="" https://books.toscrape.com
            }
            return book
        except Exception as e: # lève une erreur s'il y a un caillou dans la soup
            print("Une erreur est survenue : ", e)
            continue

def scrap_all_in_category(url):
    def find_url_page(list_url, response):
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("h3"):
            list_url.append(urljoin(url, a.find("a")["href"]))

        next_page = soup.find("li", class_="next")
        if next_page:
            res = requests.get(urljoin(url,next_page.find("a")["href"]))
            find_url_page(list_url, res)
        else:
            return list_url

    while True:
        response, url= request_url(url)
        try:
            list_url =[]
            list_book = []
            find_url_page(list_url, response)
            for book_url in list_url:
                list_book.append(scrap_one_element(book_url))

            return list_book
        except Exception as e: # lève une erreur s'il y a un caillou dans la soup
            print("Une erreur est survenue : ", e)
            continue

def scrap_all_in_all_category(url):
    pass

def safe_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title) # remplace tous les caractères de la liste par "_"

def export_csv(results):
    if not exists("Dossier_CSV"):
        os.mkdir("Dossier_CSV")
    if type(results) == list:

        filename = f"Dossier_CSV/{safe_filename(results[0]['category'])}.csv"

        with open(filename, "w", newline="", encoding="utf-8") as fichier:
            fieldnames = list(results[0].keys())
            writer = csv.DictWriter(fichier, fieldnames=fieldnames)
            writer.writeheader()
            for book in results:
                writer.writerow(book)

            print(f"La catégorie {results[0]['category']} a été exporté dans le fichier {filename}")

    if type(results) == dict :
        filename= f"Dossier_CSV/{safe_filename(results['title'])}.csv"
        with open(filename,"w" ,newline="", encoding="utf-8") as fichier:
            fieldnames = list(results.keys())
            writer = csv.DictWriter(fichier, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(results)
            print(f"Le livre {results["title"]} a été exporté dans le fichier {filename}")

def user_interface():
    while True:
        print("======================")
        print("||     Scrapping    ||")
        print("======================")
        print("1 - Scrap un livre")
        print("2 - Scrap tous les livres d'une catégorie")
        print('0 - Quittez')
        match input("Choississez votre fonction : "):
            case "1": export_csv(scrap_one_element(input_url()))
            case "2": export_csv(scrap_all_in_category(input_url()))
            case "0": break
            case _: print("Veuillez entrer une valeur valide")



if __name__ == "__main__":
    user_interface()