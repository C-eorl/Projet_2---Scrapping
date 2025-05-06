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
            table = soup.find("table").find_all("tr")
            book ={
                "product_page_url": url,
                "universal_product_code(upc)": table[0].find("td").text, # id "content_inner" => table
                "title": soup.find("h1").text, # h1
                "price_including_tax": table[3].find("td").text, # id "content_inner" => table
                "price_excluding_tax": table[2].find("td").text, # id "content_inner" => table
                "number_available": table[5].find("td").text, # id "content_inner" => table
                "product_description": soup.find("div", id="product_description").find_next_sibling("p").text if soup.find("div", id="product_description") else "Pas de description", # id "product_description" élément suivant p
                "category": soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").text, # ul class "breadcrumb" 3eme li a
                "review_rating": soup.find("p", class_="star-rating")["class"][1], # p class "star-rating" /!\
                "image_url": urljoin("https://books.toscrape.com", soup.find("div", id="product_gallery").find("img")["src"]) # id "product_galery" => img src="" https://books.toscrape.com
            }
            return book
        except Exception as e: # lève une erreur s'il y a un caillou dans la soup
            print("Une erreur est survenue (scrap_one_element): ", e)
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
            list_url = []
            list_book = []
            find_url_page(list_url, response)
            for book_url in list_url:
                list_book.append(scrap_one_element(book_url))

            return list_book
        except Exception as e: # lève une erreur s'il y a un caillou dans la soup
            print("Une erreur est survenue (scrap_all_in_category): ", e)
            continue

def scrap_all_in_all_category(url):
    list_url_categories = list()
    while True:
        response, url= request_url(url)
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            list_category = soup.find("ul", class_="nav-list").find("li").find("ul").find_all("li")
            for a in list_category:
                href = a.find("a")["href"]
                list_url_categories.append(urljoin(url, href))

            for url_category in list_url_categories:
                export_csv(scrap_all_in_category(url_category))
            return print("Toutes les catégories ont été exporter dans le dossier Dossier_CSV")
        except Exception as e:  # lève une erreur s'il y a un caillou dans la soup
            print("Une erreur est survenue (scrap_all_in_all_category): ", e)
            continue

def extraction_img():
    print("========   ATTENTION   ========")
    print("Veuillez éxécutez la fonction 3 'Scrap tous les livres de toutes les catégories'")
    print("pour pouvoir récupèrer les images de tous les livres de chaque catégories")
    print("===============================")
    if input("Tapez 'oui' pour continuer => ").lower() == "oui":
        path_directory_csv = os.path.join(os.path.dirname(__file__), "Dossier_CSV") # chemin de Dossier_CSV
        if not exists("Dossier_img"):
            os.mkdir("Dossier_img")

        for file_csv in os.listdir(path_directory_csv):
            nom_category = file_csv.replace(".csv", "")
            path_file_csv = os.path.join(path_directory_csv, file_csv)
            path_directory_category_img = f"Dossier_img/{nom_category}"
            if not exists(path_directory_category_img):
                os.mkdir(path_directory_category_img)

            list_url_img = {}
            with open(path_file_csv, "r", encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for  ligne in reader:
                    list_url_img[ligne["title"]] = ligne["image_url"]

            for title, url_img in list_url_img.items():
                title_clean = safe_filename(title)
                path_file_img = path_directory_category_img +f"/{title_clean}.jpg"
                # faire vérification si fichier img exist
                if not exists(path_file_img):
                    r = requests.get(url_img)
                    if r.status_code == 200:
                        with open(path_file_img, "wb") as f:
                            f.write(r.content)
                        print(f"Image téléchargée sous le nom : {title_clean} dans le dossier {path_directory_category_img}")
                    else:
                        print("Erreur lors du téléchargement :", r.status_code)
                print(f"l'image {title_clean} dans le dossier {path_directory_category_img} existe déjà.")
        print("Toutes les images ont été enregistrées.")

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
        print("============================================")
        print("||                Scrapping               ||")
        print("============================================")
        print("1 - Scrap un livre")
        print("2 - Scrap tous les livres d'une catégorie")
        print("3 - Scrap tous les livres de toutes les catégories")
        print("4 - Extraction des images")
        print('0 - Quittez')
        print("============================================")
        match input("Choisissez votre fonction : "):
            case "1": export_csv(scrap_one_element(input_url()))
            case "2": export_csv(scrap_all_in_category(input_url()))
            case "3": scrap_all_in_all_category(input_url())
            case "4": extraction_img()
            case "0": break
            case _: print("Veuillez entrer une valeur valide")



if __name__ == "__main__":
    user_interface()
    # soup = BeautifulSoup(requests.get("https://books.toscrape.com/catalogue/the-complete-stories-and-poems-the-works-of-edgar-allan-poe-cameo-edition_238/index.html").text, "html.parser")
    # table = soup.find("article", class_="product_page").find_all("p")
    # print(table)