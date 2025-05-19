import os
import re
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from os.path import exists
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

session = requests.Session()

def input_url():
    """ Renvoie l'input de l'utilisateur (url)"""
    return input("Saississez votre url :\n")

def request_url(url: str) :
    """
    Envoie une requête HTTP GET à l'URL fournie et retourne la réponse.
    :param url:
    :return: Tuple (soup, url) si la requête réussit.
    """
    try:
        response = session.get(url)
        response.raise_for_status() # lève erreur (ex : 404, etc..)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup, url
    except requests.exceptions.RequestException as e: # lève erreur si url non valide
        print("L'URL n'est pas valide :", e)
        print("Veuillez entrez une URL valide")

def transform_ressource_book(book:dict):
    """
    Transforme les valeurs de la variable book pour les prendre utilisables.
    :param book: Dictionnaire comprenant toutes les informations du livre
    :return: book avec les valeurs "nettoyer"
    """
    text_to_number = {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
    }
    available = book["number_available"]
    book["number_available"] = int(re.search(r"\((\d+)", available).group(1))
    rating = book["review_rating"]
    book["review_rating"] = text_to_number[rating.lower()]
    image_url = book["image_url"]
    book["image_url"] = urljoin("https://books.toscrape.com", image_url)
    book["path_img"] = f"Dossier_img/{book["category"]}/{safe_filename(book["title"])}.jpg"
    return book

def scrap_one_element(url: str):
    """
   Extrait les informations détaillées d'un livre à partir de sa page produit.

   :param url: L'URL de la page du livre.
   :return: Dict : dictionnaire des informations du livre.
   """

    soup, url = request_url(url)
    try:
        table = soup.find("table").find_all("tr")
        book ={
            "product_page_url": url,
            "universal_product_code(upc)": table[0].find("td").text,
            "title": soup.find("h1").text,
            "price_including_tax": table[3].find("td").text,
            "price_excluding_tax": table[2].find("td").text,
            "number_available": table[5].find("td").text,
            "product_description": soup.find("div", id="product_description").find_next_sibling("p").text if soup.find("div", id="product_description") else "Pas de description",
            "category": soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").text,
            "review_rating": soup.find("p", class_="star-rating")["class"][1],
            "image_url":soup.find("div", id="product_gallery").find("img")["src"]
        }
        return transform_ressource_book(book)
    except AttributeError as e: # lève une erreur s'il y a un caillou dans la soup
        print("Une erreur est survenue (scrap_one_element): ", e)

def scrap_all_in_category(url: str):
    """
    Récupère les données de tous les livres d'une catégorie donnée.

    :param url : L'URL de la page d'accueil de la catégorie à scraper.
    :return list(dict): Une liste de dictionnaires contenant les données de chaque livre.
    """
    def find_url_page(list_url: list[str], soup: BeautifulSoup):
        """

        :param list_url: liste
        :param soup: objet bs4 permettant de rechercher les éléments
        :return: list_url : liste de toutes les urls des livres trouvées dans la catégorie
        """

        for a in soup.find_all("h3"):
            list_url.append(urljoin(url, a.find("a")["href"]))

        next_page = soup.find("li", class_="next")
        if next_page:
            soupe = request_url(urljoin(url,next_page.find("a")["href"]))
            find_url_page(list_url, soupe[0])
        else:
            return list_url

    soup, url= request_url(url)
    list_url = []
    list_book = []
    find_url_page(list_url, soup)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrap_one_element, book_url) for book_url in list_url]
        for future in as_completed(futures):
            book_data = future.result()
            list_book.append(book_data)
    return list_book

def scrap_all_in_all_category(url: str):
    """
    Récupère et exporte en .csv les données de toutes les catégories de livres du site.

    :param url : L'URL de la page d'accueil du site à scraper.

    :return None: Affiche un message une fois l'export terminé.
    """
    list_url_categories = list()
    soup, url= request_url(url)
    list_category = soup.find("ul", class_="nav-list").find("li").find("ul").find_all("li")
    for a in list_category:
        href = a.find("a")["href"]
        list_url_categories.append(urljoin(url, href))

    for url_category in list_url_categories:
        export_csv(scrap_all_in_category(url_category))
    return print("Toutes les catégories ont été exportées dans le dossier Dossier_CSV")

def extraction_img():
    """
    Récupère-les urls des images dans chaque fichier .csv
    Crée dossier → Dossier_img/[categories]/image.jpg si n'existe pas
    puis télécharge l'image
    :return: None
    """

    print("========   ATTENTION   ========")
    print("Veuillez exécuter la fonction 3 'Scrap tous les livres de toutes les catégories'")
    print("pour pouvoir récupérer les images de tous les livres de chaque catégories")
    print("===============================")
    if not exists(os.path.join(os.path.dirname(__file__), "Dossier_CSV")):
        return print("Aucun dossier contenant des fichier .csv n'a été trouvé\n"
                     "Veuillez utiliser la fonction 3 avant.")

    if input("Tapez 'oui' pour continuer => ").lower() == "oui":
        path_directory_csv = os.path.join(os.path.dirname(__file__), "Dossier_CSV") # chemin de Dossier_CSV
        if not exists("Dossier_img"):
            os.mkdir("Dossier_img")
        with ThreadPoolExecutor(max_workers=30) as executor:
            for file_csv in os.listdir(path_directory_csv):
                nom_category = file_csv.replace(".csv", "")
                path_file_csv = os.path.join(path_directory_csv, file_csv)
                path_directory_category_img = f"Dossier_img/{nom_category}"
                if not exists(path_directory_category_img):
                    os.mkdir(path_directory_category_img)


                with open(path_file_csv, "r", encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for  ligne in reader:
                        title = ligne["title"]
                        url_img = ligne["image_url"]
                        title_clean = safe_filename(title)
                        path_file_img = ligne["path_img"]

                        executor.submit(download_image, title_clean, url_img, path_file_img, nom_category)
        return print("Le téléchargement des images est terminé.")

def download_image(title: str, url_img: str, path_file_img:str, category:str):
    """
    Télécharge une image depuis une URL si elle n'existe pas déjà localement.

    :param title: Titre du livre, utilisé pour les logs.
    :param url_img: URL de l'image à télécharger.
    :param path_file_img: Chemin de destination du fichier image local.
    :param category: Nom de la catégorie du livre
    :return: None
    """

    if not exists(path_file_img):
        r = requests.get(url_img)
        if r.status_code == 200:
            with open(path_file_img, "wb") as f:
                f.write(r.content)
            print(f"[{category}] Image téléchargée : {title}")
        else:
            print(f"[{category}] Erreur {r.status_code} pour {title}")
    else:
        print(f"[{category}] Image déjà présente : {title}")

def safe_filename(title:str):
    return re.sub(r'[\\/*?:"<>|]', "_", title) # remplace tous les caractères de la liste par "_"

def export_csv(results):
    """
    Exporte les données d'une liste de livres dans un fichier CSV.
    :param results: Liste de dictionnaires ou dictionnaire contenant les données des livres.
                    Chaque dictionnaire représente un livre.
    :return: None
    """

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
        directory = "Dossier_CSV_one_book"
        if not exists(directory):
            os.mkdir(directory)
        filename= f"{directory}/{safe_filename(results['title'])}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as fichier:
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