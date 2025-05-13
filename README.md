# Projet de Web Scraping de Livres

Ce projet de scraping récupère des données de livres à partir d’un site web ([Book](https://books.toscrape.com/index.html)), les enregistre dans des fichiers CSV, et télécharge les images des couvertures en les classant automatiquement par catégorie.

---

## Installation

### Prérequis
*python 3.12*
- installation: 
```bash
winget install "Python 3.12"
```
- soit:
https://www.python.org/downloads/release/python-3120/

### 1. Cloner ce dépôt
```bash
git clone git@github.com:C-eorl/Projet_2---Scrapping.git
cd scraping-livres
```
### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # sous Windows : venv\Scripts\activate
```
### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```
### 4. Lancer le script
Attention à bien être dans le dossier scrapping.
```bash
cd scrapping
```
```bash
python main.py
```


---

## Fonctionnalité

En lançant le fichier main.py, le terminal s'ouvrira laissant le choix à 4 fonctions et le choix de quitter le script :
 - 1 - Scrap un livre
 - 2 - Scrap tous les livres d'une catégorie
 - 3 - Scrap tous les livres de toutes les catégories
 - 4 - Extraction des images

### Fonction 1 - Scrap un livre

La fonction se sert de beautifulsoup pour récupérer le code HTML de l'url d'un livre donné par l'utilisateur au début de la fonction.
Pour chaque exigence à récupérer, on recherche la balise associée à l'information recherchée. 
Ensuite, on envoie toutes les informations sous forme de dictionnaire à une fonction qui va les enregistrer sous un format .csv au nom du titre du livre.

### Fonction 2 - Scrap tous les livres d'une catégorie

La fonction se sert de beautifulsoup pour récupérer le code HTML de l'url d'une catégorie donné par l'utilisateur au début de la fonction.
Elle va rechercher toutes les urls de chaque livre présent dans cette catégorie en recherchant la balise h3 et en vérifiant la présence de plusieurs pages pour les enregistrer dans une liste.
Ensuite, Elle va, pour chaque url de livre dans la liste, appeler la fonction 1 - scrap un livre et enregistrer le dictionnaire dans une autre liste.
Cette dernière sera traitée par une fonction qui génèrera un fichier .csv au nom de la catégorie choisie avec toutes les exigences de tous les livres.

### Fonction 3 - Scrap tous les livres de toutes les catégories

La fonction se sert de beautifulsoup pour récupérer le code HTML de l'url du site https://books.toscrape.com/index.html donné par l'utilisateur au début de la fonction.
Elle va rechercher toutes les urls des catégories pour les mettre dans une liste.
Ensuite, elle va faire appelle, pour chaque url de la liste, à la fonction 2 - Scrap tous les livres d'une catégorie.

### Fonction 4 - Extraction des images

La fonction va vérifier si le dossier contenant les fichiers .csv est présent, sinon, arrête la fonction.
La fonction va, ensuite, vérifier si le dossier prévu pour enregistrer les image et le dossier des categories existent, sinon, les créer.
Elle va mettre dans une liste toutes les urls des images récupérées dans les fichiers .csv.
Puis, elle télécharge chaque image associée aux urls en les classant par catégorie et en les renommant avec le titre du livre correspondant.
