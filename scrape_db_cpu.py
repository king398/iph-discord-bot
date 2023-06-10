import requests
import pandas as pd
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import time
from pwn import log

load_dotenv()

status = log.progress("Status")
brand_logging = log.progress("Brand")
year_logging = log.progress("Year")

db_connection_url = f"mongodb://root:{os.environ.get('MONGODB_PASSWORD')}@localhost:4040/techpowerup?authSource=admin"
client = MongoClient(db_connection_url)
dbname = client.get_database()
collection_name = dbname["CPU"]

tpu_db_cpu_url = "https://www.techpowerup.com/cpu-specs/"
#cpu_brands = ["Intel", "AMD"]
cpu_brands = ["VIA"]

params = {
    "mfgr":"", 
    "released":2000,
    "mobile":"No",
    "server":"No",
    "sort":"released"
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

def createDocument(brand, name, link, codename, cores, clock, socket, process, l3cache, tdp, released):
    document = {
        "Brand": brand,
        "Name": name,
        "Link": link,
        "Codename": codename,
        "Cores": cores,
        "Clock": clock,
        "Socket": socket,
        "Process": process,
        "L3 Cache": l3cache,
        "TDP": tdp,
        "Released": released
    }
    return document


def scrape_cpu_by_year(params, brand, class_of_cpu, year):
    year_logging.status(str(year))
    params["released"] = year
    resp = requests.get(tpu_db_cpu_url, params=params)
    if resp.status_code != 200:
        print(f"Something's not right...\nStatus Code: {resp.status_code}\nResponse: {resp.text}")
        exit()
    else:
        tables = pd.read_html(resp.text, extract_links="all")
        if "No CPUs found" in resp.text:
            status.status("Single table parsed, maybe an empty year. Skipping.")
            time.sleep(90)
            return
        documents = []
        for index in tables[1].index:
            documents.append(createDocument(brand=brand,                                                                        # Brand
                                            name=tables[1][tables[1].columns[0]][index][0],                                     # Name
                                            link=tables[1][tables[1].columns[0]][index][1],                                     # Link
                                            codename=tables[1][tables[1].columns[1]][index][0],                                 # Codename
                                            cores=tables[1][tables[1].columns[2]][index][0],                                    # Cores
                                            clock=tables[1][tables[1].columns[3]][index][0],                                    # Clock
                                            socket=tables[1][tables[1].columns[4]][index][0],                                   # Socket
                                            process=tables[1][tables[1].columns[5]][index][0],                                  # Process
                                            l3cache=str(tables[1][tables[1].columns[6]][index][0]),                             # L3 Cache
                                            tdp=tables[1][tables[1].columns[7]][index][0],                                      # TDP
                                            released=tables[1][tables[1].columns[8]][index][0],                                 # Released
                                            ))
        collection_name.insert_many(documents)
    status.status(f"Scraped {class_of_cpu} from {brand} for year {year}")
    time.sleep(90)


def scrape_desktop_cpu(brand, years:list):
    params["mfgr"] = brand
    params["mobile"] = "No"
    params["server"] = "No"
    for year in years:
        scrape_cpu_by_year(params,brand,"Desktop CPUs", year)


def scrape_server_cpu(brand, years: list):
    params["mfgr"] = brand
    params["mobile"] = "No"
    params["server"] = "Yes"
    for year in years:
        scrape_cpu_by_year(params,brand,"Desktop Server CPUs", year)

def scrape_mobile_cpu(brand, years: list):
    params["mfgr"] = brand
    params["mobile"] = "Yes"
    params["server"] = "No"
    for year in years:
        scrape_cpu_by_year(params,brand,"Mobile CPUs", year)


def scrape_server_mobile_cpu(brand, years: list):
    if brand == "AMD":
        return
    params["mfgr"] = brand
    params["mobile"] = "Yes"
    params["server"] = "Yes"
    for year in years:
        scrape_cpu_by_year(params, brand,"Mobile Server CPUs",year)


for brand in cpu_brands:
    status.status(f"Starting scraping Techpowerup CPU DB for {brand}")
    brand_logging.status(brand)
    years = []
    if brand == "VIA":
        years = [2008, 2011, 2015, 2020]
    else:
        start_year = int(input("Enter starting year"))
        years = range(start_year, time.localtime()[0])
    scrape_desktop_cpu(brand, years)
    scrape_server_cpu(brand, years)
    scrape_mobile_cpu(brand, years)
    scrape_server_mobile_cpu(brand, years)

