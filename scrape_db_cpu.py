#!/usr/bin/env python3
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import time
from pwn import log
import sys
import argparse

load_dotenv()


parser = argparse.ArgumentParser()
parser.add_argument("--update", "-u", required=False, action='store_true', help="Perform update only.")
parser.add_argument("--brand", "-b", action='store', default='ALL', choices=['AMD', 'INTEL', 'VIA', 'ALL'], help="Pull data for specified Mfgr (Defaults to all)", required=False, nargs='*', type=str.upper)
parser.add_argument("--years", "-y", nargs='+', action='store', default=[1998, time.localtime()[0]+1], help="Years for which the data is to be pulled.")
parser.add_argument("--processor-class", "-pc", default=["all"], choices=["Desktop", "Mobile", "Server Desktop", "Server Mobile","all"], action='store', nargs='*', help="Processor class to pull. Defaults to 'all'.")
parser.add_argument("--skip-igpu", "-skigp", action='store_true', help="Skip processor with iGPU or not.")
args = parser.parse_args()
cpu_brands = []
if "ALL" in args.brand:
    cpu_brands = ["INTEL", "AMD", "VIA"]
else:
    cpu_brands = args.brand
years = []
if args.update:
    years = [time.localtime()[0], time.localtime()[0]+1]
else:
    years = args.years


status = log.progress("Status")
brand_logging = log.progress("Brand")
year_logging = log.progress("Year")

db_connection_url = f"mongodb://root:{os.environ.get('MONGODB_PASSWORD')}@localhost:4040/techpowerup?authSource=admin"
client = MongoClient(db_connection_url)
dbname = client.get_database()
collection_name = dbname["CPU"]

tpu_db_cpu_url = "https://www.techpowerup.com/cpu-specs/"


params = {
    "mfgr":"", 
    "released":2000,
    "mobile":"No",
    "server":"No",
    "sort":"released",
    "igp": "No",
    "multiUnlocked": "No"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.techpowerup.com/cpu-specs/?sort=name",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Gpc": "1",
    "X-Requested-With": "XMLHttpRequest"
    }


def check_for_existing():
    pass


def createDocument(brand, name, link, codename, cores, clock, socket, process, l3cache, tdp, released, igpu, class_of_cpu, multiplier):
    document = {
        "Brand": brand,
        "Name": name,
        "Link": link,
        "Codename": codename,
        "Product Class": class_of_cpu,
        "Cores": cores,
        "Clock": clock,
        "Multiplier": multiplier,
        "iGPU": igpu,
        "Socket": socket,
        "Process": process,
        "L3 Cache": l3cache,
        "TDP": tdp,
        "Released": released
    }
    return document


def scrape_cpu_by_year(params, brand, class_of_cpu: str, year, multiplier):
    year_logging.status(str(year))
    status.status(f"Scraping {class_of_cpu} from {brand} for year {year}, iGPU:{params['igp']}, Multiplier: {multiplier}")
    params["released"] = year
    resp = requests.get(tpu_db_cpu_url, params=params)
    if resp.status_code != 200:
        print(f"Something's not right...\nStatus Code: {resp.status_code}\nResponse: {resp.text}")
        exit()
    else:
        tables = pd.read_html(resp.text, extract_links="all")
        resp.close()
        if "No CPUs found" in resp.text:
            status.status(f"Single table parsed, maybe an empty year. Skipping. Processor Class=>{class_of_cpu}; iGPU={params['igp']}")
            time.sleep(90)
            return
        documents = []
        for index in tables[1].index:
            brand_for_document = ''
            if brand == 'INTEL':
                brand_for_document = 'Intel'
            else:
                brand_for_document = brand
            documents.append(createDocument(brand=brand_for_document,                                                           # Brand
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
                                            class_of_cpu=class_of_cpu.replace(" CPUs", ""),                                     # Class of CPU
                                            igpu=params["igp"],                                                                 # iGPU [Yes/No]
                                            multiplier=multiplier                                                               # Multiplier Unlocked [Yes/No]
                                            ))
        collection_name.insert_many(documents)
    print(f"Scraped {class_of_cpu} from {brand} for year {year}, iGPU:{params['igp']}, Multiplier: {multiplier}")
    status.status(f"Scraped {class_of_cpu} from {brand} for year {year}, iGPU:{params['igp']}, Multiplier: {multiplier}. Sleeping for 90 seconds.")
    time.sleep(90)


def scrape_desktop_cpu(brand, years:list):
    params["mfgr"] = brand
    params["mobile"] = "No"
    params["server"] = "No"
    for year in years:
        # Desktop, no iGPU, locked
        params["igp"] = "No"
        params["multiUnlocked"] = "No"
        scrape_cpu_by_year(params,brand,"Desktop CPUs", year, "Locked")
        # Desktop, no iGPU, Unlocked
        params["igp"] = "No"
        params["multiUnlocked"] = "Yes"
        scrape_cpu_by_year(params,brand,"Desktop CPUs", year, "Unlocked")
        if not args.skip_igpu:
            # Desktop, iGPU, locked
            params["igp"] = "Yes"
            params["multiUnlocked"] = "No"
            scrape_cpu_by_year(params,brand,"Desktop CPUs", year, "Locked")
            # Desktop, iGPU, Unlocked
            params["igp"] = "Yes"
            params["multiUnlocked"] = "Yes"
            scrape_cpu_by_year(params,brand,"Desktop CPUs", year, "Unlocked")


def scrape_server_cpu(brand, years: list):
    params["mfgr"] = brand
    params["mobile"] = "No"
    params["server"] = "Yes"
    for year in years:
        # Server, no iGPU, locked
        params["igp"] = "No"
        params["multiUnlocked"] = "No"
        scrape_cpu_by_year(params,brand,"Server Desktop CPUs", year, "Locked")
        # Server, no iGPU, Unlocked
        params["igp"] = "No"
        params["multiUnlocked"] = "Yes"
        scrape_cpu_by_year(params,brand,"Server Desktop CPUs", year, "Unlocked")
        if not args.skip_igpu:
            # Server, iGPU, locked
            params["igp"] = "Yes"
            params["multiUnlocked"] = "No"
            scrape_cpu_by_year(params,brand,"Server Desktop CPUs", year, "Locked")
            # Server, iGPU, Unlocked
            params["igp"] = "Yes"
            params["multiUnlocked"] = "Yes"
            scrape_cpu_by_year(params,brand,"Server Desktop CPUs", year, "Unlocked")


def scrape_mobile_cpu(brand, years: list):
    params["mfgr"] = brand
    params["mobile"] = "Yes"
    params["server"] = "No"
    for year in years:
        # Mobile, no iGPU, locked
        params["igp"] = "No"
        params["multiUnlocked"] = "No"
        scrape_cpu_by_year(params,brand,"Mobile CPUs", year, "Locked")
        # Mobile, no iGPU, Unlocked
        params["igp"] = "No"
        params["multiUnlocked"] = "Yes"
        scrape_cpu_by_year(params,brand,"Mobile CPUs", year, "Unlocked")
        if not args.skip_igpu:
            # Mobile, iGPU, locked
            params["igp"] = "Yes"
            params["multiUnlocked"] = "No"
            scrape_cpu_by_year(params,brand,"Mobile CPUs", year, "Locked")
            # Mobile, iGPU, Unlocked
            params["igp"] = "Yes"
            params["multiUnlocked"] = "Yes"
            scrape_cpu_by_year(params,brand,"Mobile CPUs", year, "Unlocked")


def scrape_server_mobile_cpu(brand, years: list):
    if brand == "AMD" or brand == "VIA":
        return
    params["mfgr"] = brand
    params["mobile"] = "Yes"
    params["server"] = "Yes"
    params["igp"] = "Yes"
    params["multiUnlocked"] = "No"
    for year in years:
        scrape_cpu_by_year(params, brand,"Mobile Server CPUs",year, "Locked")

print(f"""These arguments will scrape for:\nBrands: {cpu_brands}\nYears: {years}\nProcessor Class: {args.processor_class}\niGPU: {not args.skip_igpu}
      """)

for brand in cpu_brands:
    status.status(f"Starting scraping Techpowerup CPU DB for {brand}")
    brand_logging.status(brand)
    if "all" in args.processor_class:
        scrape_desktop_cpu(brand, years)
        scrape_server_cpu(brand, years)
        scrape_mobile_cpu(brand, years)
        scrape_server_mobile_cpu(brand, years)
        exit()
    if "Desktop" in args.processor_class:
        scrape_desktop_cpu(brand, years)
    if "Mobile" in args.processor_class:
        scrape_mobile_cpu(brand, years)
    if "Server Desktop" in args.processor_class:
        scrape_server_cpu(brand, years)
    if "Server Mobile" in args.processor_class:
        scrape_server_mobile_cpu(brand, years)

