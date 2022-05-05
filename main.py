from bs4 import BeautifulSoup
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd

# Amazon Product Scraper

BASE_URL = 'https://www.amazon.ca/s?k='

def open_browser(url):
    # options = webdriver.ChromeOptions()
    # options.headless = True
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    options = webdriver.FirefoxOptions()
    options.headless = True
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    driver.get(url)
    return driver.page_source

def search_url(keywords):
    return f'{BASE_URL}{keywords.replace(" ", "+")}'

def fetch_page(keyword):
    url = search_url(keyword)
    page_source = open_browser(url)
    return BeautifulSoup(page_source, 'html.parser')

def get_product_detail_page(element):
    return f"https://www.amazon.ca{element.find('a')['href']}"

def get_product_image_src(element):
    return element.find('img')['src']

def get_product_name(element):
    return element.find('h2').get_text()

def get_product_rating(element):
    return element.select('span.a-icon-alt')[0].get_text() if element.select('span.a-icon-alt') else "N/A"

def get_product_price(element) -> str:
    return element.select('span.a-price>span')[0].get_text() if element.select('span.a-price') else "N/A"

def get_original_price(element) -> str:
    return element.select('span.a-price.a-text-price>span')[0].get_text() if element.select('span.a-price.a-text-price') else "N/A"

def get_sale_percent(prd) -> str:
    original = get_original_price(prd)
    current = get_product_price(prd)

    org = float(original.replace("$", "")) if original != "N/A" else None
    curr = float(current.replace("$", "")) if current != "N/A" else None

    if curr != None and org != None:
        diff = org - curr
        return f"{int((diff/org)*100)}%"

    return "N/A"

def get_products(soup):
    products = soup.select('div.sg-col-4-of-12.s-result-item.s-asin.sg-col-4-of-16.sg-col.s-widget-spacing-small.sg-col-4-of-20')
    products_data = [
        {'prod_url': get_product_detail_page(prd), 
        'prod_img': get_product_image_src(prd), 
        'prod_name': get_product_name(prd), 
        'prod_rating': get_product_rating(prd),
        'prod_price': get_product_price(prd),
        'prod_org_price': get_original_price(prd),
        'prod_sale': get_sale_percent(prd)
        } for prd in products]

    return products_data



soup = fetch_page('monitor cleaning kit')
print("==================================")
data = get_products(soup)

df = pd.DataFrame(data)
df.to_excel("monitor_cleaning_kit.xlsx")