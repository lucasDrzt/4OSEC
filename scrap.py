import requests
from bs4 import BeautifulSoup
import sqlite3  # Utilise sqlite3 pour SQLite ; utilise psycopg2 pour PostgreSQL si nécessaire

# Connexion à la base de données SQLite
conn = sqlite3.connect("data.db")
cur = conn.cursor()

# Création de la table pour stocker les données si elle n'existe pas
cur.execute("""
CREATE TABLE IF NOT EXISTS scraped_data (
    url TEXT PRIMARY KEY,
    title TEXT,
    description TEXT
)
""")
conn.commit()

# Récupération du sitemap
sitemap_url = "https://readi.fi/sitemap.xml"
sitemap_content = requests.get(sitemap_url).text

# Parse le sitemap pour obtenir les URLs
soup = BeautifulSoup(sitemap_content, "xml")
urls = [loc.text for loc in soup.find_all("loc") if loc.text.startswith("https://readi.fi/asset")]

print(f"Nombre d'URLs spécifiques trouvées: {len(set(urls))}")

# Scraping de chaque URL
for url in urls:
    response = requests.get(url)
    page_soup = BeautifulSoup(response.text, "html.parser")
    
    title = page_soup.title.string if page_soup.title else "N/A"
    description = ""
    
    # Recherche de la balise meta description
    meta_desc = page_soup.find("meta", {"name": "description"})
    if meta_desc:
        description = meta_desc.get("content", "")
    
    # Insertion des données dans la base
    cur.execute("""
    INSERT OR REPLACE INTO scraped_data (url, title, description)
    VALUES (?, ?, ?)
    """, (url, title, description))
    conn.commit()

conn.close()
print("Scraping et insertion en base de données terminés.")
