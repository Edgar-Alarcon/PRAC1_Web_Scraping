from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# Devuelve el driver de chrome
def getDriverChrome():

    options = Options()
    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    return driver


# Guarda el csv
def saveToCsv(path_file , text):
    f = open(path_file, "w")
    f.write(text)
    f.close()


# Devuelve todos los datos en formato csv para una categoria
def getCsvFromCategory(driver, category, products_already_stored):

    text_csv = ""

    text_category = category.find_element(by=By.CLASS_NAME, value="subhead1-r").text

    subcategories = category.find_elements(by=By.CLASS_NAME, value="category-item__link")

    print(text_category)

    #Itera las subcategorias, clicandolas y parseando lo que aho dentro de ellas
    for subcategory in subcategories:
        subcategory.click()
        time.sleep(3)

        # Obtiene el body para empezar el parseo
        body = driver.execute_script("return document.body")
        source = body.get_attribute('innerHTML')
        soup = BeautifulSoup(source, "html.parser")
        text_subcategory = soup.find("h1", "category-detail__title title1-b").get_text()
        print(text_category, text_subcategory)

        # Itera las secciones que hay dentro de cada subcategoria
        for section in soup.find_all("section", "section"):
            text_section = section.find("h2", "section__header headline1-b").get_text()

            #Itera los productos que hay en cada sección
            for product in section.find_all("div", "product-cell__info"):
                text_name_product = product.find("h4", "subhead1-r product-cell__description-name").get_text()
                text_price_product = product.find("div", "product-price").find("p",
                                                                               "product-price__unit-price subhead1-b").get_text()
                text_price_product = text_price_product.replace(" €", "").replace(",", ".")
                text_details = ""

                # Obtiene los detalles de ese producto
                for description in product.find("div", "product-format product-format__size--cell").find_all("span",
                                                                                                             "footnote1-r"):
                    text_details += description.get_text()

                #Para evitar repeticiones de productos, construye una hash unica
                unique_hash_product = text_name_product + "_" + text_details

                if unique_hash_product not in products_already_stored:

                    # Se añade el producto a una fila del csv
                    text_csv += '"' + text_category + '", "'
                    text_csv += text_subcategory + '", "'
                    text_csv += text_section + '", "'
                    text_csv += text_name_product + '", "'
                    text_csv += text_details + '", '
                    text_csv += text_price_product + "\n"
                    products_already_stored.append(unique_hash_product)

    return text_csv

# Inicializa la pagina y la prepara para el scrapeo
def prepareAndCleanWebsite(driver):

    driver.get("https://tienda.mercadona.es/categories/")
    time.sleep(5)
    inputElement = driver.find_element(by=By.NAME, value="postalCode")
    inputElement.send_keys('08902')
    time.sleep(2)

    button = driver.find_element(by=By.CSS_SELECTOR,
                                 value='#root > div.ui-focus-trap > div > div:nth-child(2) > div > form > button')
    button.click()

    time.sleep(2)

    button_cookies = driver.find_element(by=By.CSS_SELECTOR,
                               value='#root > div.cookie-banner > div > div > button.ui-button.ui-button--small.ui-button--primary.ui-button--positive')
    button_cookies.click()

    time.sleep(2)



# Funcion principal del scraper

def scrapWebsite(driver, is_a_test = True):

    try:
        prepareAndCleanWebsite(driver)

        products_already_stored = list()

        global_csv = "Categoría, Subcategoría, Sección, Producto, Detalle, Precio\n"

        first_passed = False

        categories = driver.find_elements(by=By.CLASS_NAME, value="category-menu__item")

        for num_category,category in enumerate(categories):

            try:
                if first_passed:
                    category.click()
                    time.sleep(3)
                else:
                    first_passed = True

                global_csv += getCsvFromCategory(driver, category,products_already_stored)
                
                # Hace un break al bucle para terminar el test
                if is_a_test and num_category >= 5:
                    break

            except Exception as e:
                print(str(e))


    except Exception as e:
        print(str(e))

    return global_csv

driver = getDriverChrome()
global_csv = scrapWebsite(driver)
saveToCsv("precios_mercadona.csv", global_csv)
