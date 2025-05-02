import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrap_one_element():
    url = input("saississez votre url :\n")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    book ={
        "product_page_url": url,
        "universal_product_code(upc)": soup.find("table").find("th", string="UPC").find_next_sibling("td").text, # id "content_inner" => table
        "title": soup.find("h1").text, # h1
        "price_including_tax": soup.find("table").find("th", string="Price (incl. tax)").find_next_sibling("td").text, # id "content_inner" => table
        "price_excluding_tax": soup.find("table").find("th", string="Price (excl. tax)").find_next_sibling("td").text, # id "content_inner" => table
        "number_available": soup.find("table").find("th", string="Availability").find_next_sibling("td").text, # id "content_inner" => table
        "product_description": soup.find("div", id="product_description").find_next_sibling("p").text, # id "product_description" élément suivant p
        "category": soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").text, # ul class "breadcrumb" 3eme li a
        "review_rating": soup.find("p", class_="star-rating")["class"][1], # p class "star-rating" /!\
        "image_url": urljoin("https://books.toscrape.com", soup.find("div", id="product_gallery").find("img")["src"]) # id "product_galery" => img src="" https://books.toscrape.com
    }

    return print(book)


url = "https://books.toscrape.com/catalogue/the-secret-garden_413/index.html"
def interface_user():
    print("======================")
    print("        Scrapping ")
    print("======================")
    print("1 - scrap 1 livre")
    match input("Choississez votre fonction : "):
        case "1": scrap_one_element()
        case _: print("veuillez entrer une valeur valide")

interface_user()