# Librerías para gestión de tiempos
from time import sleep
from tqdm import tqdm

# Librerías para tratamiento de datos

import pandas as pd
import numpy as np
import re

# Librerías para captura de datos
import requests
from bs4 import BeautifulSoup

# Librería de traducción
from googletrans import Translator

# Librería de geolocalización
from geopy.geocoders import Nominatim

# Librerías para automatización de navegadores web con Selenium
from selenium import webdriver  
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.support.ui import Select 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException 

# Librería para gestión de tiempos
import time

# Librería para trabajar con bases de datos SQL
import psycopg2
from psycopg2 import OperationalError, errorcodes, errors

# Librería para manejar archivos .env, para cargar tokens y claves
import os
import dotenv
dotenv.load_dotenv()

# Librería para ignorar avisos
import warnings
warnings.filterwarnings("ignore") # Ignora TODOS los avisos


# -------------------------------------- #

# Este script permite navegar y extraer información de un sitio web, limpiar y organizar los datos,
# y luego interactuar con una base de datos para almacenar o recuperar información.

# -------------------------------------- #

# Importamos el usuario y contraseña que hemos guardado en el archivo .env, de modo que podamos utilizarlos como inputs de nuestra función.
dbeaver_pw = os.getenv("dbeaver_pw")
dbeaver_user = os.getenv("dbeaver_user")
rapiapi_key = os.getenv("rapiapi_key")


def consulta_airbnbs(destino, checkin, checkout, paginas):
    """
    Consulta anuncios de Airbnb en función del destino y las fechas proporcionadas, y retorna los resultados de las páginas especificadas.

    Parámetros:
    destino (str): El destino de la búsqueda.
    checkin (str): Fecha de entrada en formato 'YYYY-MM-DD'.
    checkout (str): Fecha de salida en formato 'YYYY-MM-DD'.
    paginas (int): Número de páginas de resultados a consultar.

    Devuelve:
    list: Una lista con los resultados de las búsquedas de las páginas especificadas.
    """

    url = "https://airbnb13.p.rapidapi.com/search-location"
    headers = {
        "x-rapidapi-key": "e9d53ce8f2msh50c48f79aa0b1b1p1674b7jsn7a3fd4b9a409",
        "x-rapidapi-host": "airbnb13.p.rapidapi.com"
    }
    
    lista_resultados = []
    
    for pagina in tqdm(range(1, paginas + 1)):
        query = {
            "location": destino,
            "checkin": checkin,
            "checkout": checkout,
            "adults": "2",
            "children": "0",
            "infants": "0",
            "pets": "0",
            "page": str(pagina),
            "currency": "EUR"
        }

        try:
            response = requests.get(url, headers=headers, params=query)
            res = response.json()
            lista_resultados.append(res)
        except requests.exceptions.RequestException as e:
            print(f"Error en la página {pagina}: {e}")
            continue  # Continuar con la siguiente página en caso de error
        
        # Pausa para evitar superar los límites de tasa de la API
        sleep(20)
    
    return lista_resultados


def dataframe_airbnb(resultados_airbnb):
    """
    Convierte los resultados de Airbnb en un DataFrame de pandas con columnas para latitud, longitud, descripción y precio total.

    Parámetros:
    resultados_airbnb (list): Una lista de diccionarios que contiene los resultados de las búsquedas de Airbnb.

    Devuelve:
    DataFrame: Un DataFrame de pandas con las columnas 'Latitud', 'Longitud', 'Descripción' y 'Precio Total'.
    """
    lista_airbnbs = []
    
    for resultado in resultados_airbnb:
        alojamientos = resultado.get("results", [])
        
        for alojamiento in alojamientos:
            lista_airbnbs.append({
                "Latitud": alojamiento["lat"],
                "Longitud": alojamiento["lng"],
                "Descripcion": alojamiento["name"],
                "Precio Total": alojamiento["price"]["total"]
            })
    
    df_airbnb = pd.DataFrame(lista_airbnbs)
    return df_airbnb


def traducir_es(text):
    """
    Traduce un texto al español utilizando la biblioteca Googletrans.

    Parámetros:
    text (str): El texto que se desea traducir.

    Devuelve:
    str: El texto traducido al español, o un mensaje de error si la traducción falla.
    """
    if text is None:
        return "Descripción no encontrada"
    translator = Translator()
    try:
        translated = translator.translate(text, dest='es')  # Traduciendo a español ('es')
        return translated.text
    except Exception as e:
        return f"Error de traducción: {e}"


def obtener_coordenadas_distrito(distritos):
    
    """
    Obtiene las coordenadas geográficas (latitud y longitud) de una lista de distritos.

    Parámetros:
    - distritos (list): Lista de nombres de distritos.

    Retorna:
    - dicc_coordenadas (dict): Diccionario con los nombres de los municipios como claves y sus respectivas coordenadas (latitud y longitud) como valores.
    """

    geolocator = Nominatim(user_agent="my_app")
    dicc_coordenadas = {}
    
    for distrito in tqdm(distritos):
        location = geolocator.geocode(distrito)
        dicc_coordenadas[distrito] = ((location.latitude, location.longitude))
        sleep(1)

    return dicc_coordenadas


def obtener_nombre_distrito(latitude, longitude):
    """
    Obtiene el nombre del distrito en función de la latitud y longitud proporcionadas.

    Parámetros:
    latitude (float): La latitud del lugar.
    longitude (float): La longitud del lugar.

    Devuelve:
    str: El nombre del distrito de la ubicación especificada. Si no se encuentra, devuelve una cadena vacía.
    """
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.reverse((latitude, longitude), language='es')
    address = location.raw['address']
    distrito = address.get('city_district', '')
    
    return distrito


import requests

def consulta_idealista(locationId, locationName, paginas=1):
    """
    Realiza consultas a la API de Idealista para obtener anuncios de alquiler de viviendas en función del destino y número de páginas especificadas.

    Parámetros:
    locationId (str): El ID de la ubicación.
    locationName (str): El nombre de la ubicación.
    paginas (int): Número de páginas de resultados a consultar (por defecto es 1).

    Devuelve:
    list: Una lista de diccionarios con los resultados de las búsquedas de las páginas especificadas.
    """

    url = "https://idealista7.p.rapidapi.com/listhomes"
    headers = {
        "x-rapidapi-key": "e9d53ce8f2msh50c48f79aa0b1b1p1674b7jsn7a3fd4b9a409",
        "x-rapidapi-host": "idealista7.p.rapidapi.com"
    }

    lista_resultados = []

    for pagina in tqdm(range(1, paginas + 1)):
        querystring = {
            "order": "relevance",
            "operation": "rent",
            "locationId": locationId,
            "locationName": locationName,
            "numPage": str(pagina),
            "maxItems": "40",
            "location": "es",
            "locale": "es"
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        res = response.json()
        lista_resultados.append(res)
        sleep(5)
    
    return lista_resultados


def dataframe_idealista(lista_resultados):
    """
    Convierte los resultados de Idealista en un DataFrame de pandas con varias columnas de interés.

    Parámetros:
    lista_resultados (list): Una lista de diccionarios que contienen los resultados de las búsquedas de Idealista.

    Devuelve:
    DataFrame: Un DataFrame de pandas con columnas que incluyen 'Latitud', 'Longitud', 'Precio', 'Tipo', 'Planta', 'Tamaño', 'Habitaciones', 'Baños', 'Dirección' y 'Descripción'.
    """
    anuncios = []

    for elemento in lista_resultados:
        for anuncio in elemento.get("elementList", []):
            anuncios.append({
                "Latitud": anuncio.get("latitude"),
                "Longitud": anuncio.get("longitude"),
                "Precio": anuncio.get("price"),
                "Tipo": anuncio.get("propertyType"),
                "Planta": anuncio.get("floor"),
                "Tamanio": anuncio.get("size"),
                "Habitaciones": anuncio.get("rooms"),
                "Banios": anuncio.get("bathrooms"),
                "Direccion": anuncio.get("address"),
                "Descripcion": anuncio.get("description")
            })

    df_idealista = pd.DataFrame(anuncios)

    return df_idealista


def scraping_alquileres_redpiso(paginas=1):
    """
    Realiza el scraping de la página web de Redpiso para obtener anuncios de alquiler de viviendas en Madrid.
    
    Pasos:
    1. Configura el driver de Chrome en modo incógnito y abre la URL inicial.
    2. Acepta las cookies.
    3. Realiza clics necesarios para configurar la búsqueda (tipo, alquiler, buscar).
    4. Itera sobre las primeras páginas de resultados, realizando scroll y obteniendo el código fuente de cada página.
    5. Analiza el código fuente con BeautifulSoup y almacena los resultados.

    Parámetros:
    paginas (int): Número de páginas de resultados a consultar (por defecto es 1).

    Devuelve:
    list: Una lista con los resultados del scraping de las páginas especificadas.
    """

    # Configurar el driver y abrir la URL
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=chrome_options)
    
    url_inicio = "https://www.redpiso.es/"
    driver.get(url_inicio)
    
    # Esperar a que aparezca el banner de cookies y aceptar cookies
    time.sleep(3)
    try:
        driver.find_element("css selector", "#gdpr-cookie-accept").click()
        print("Cookies aceptadas")
    except Exception as e:
        print(f"Error al aceptar cookies: {e}")
    
    # Click en botón tipo
    time.sleep(2)
    driver.find_element("css selector", "#form_guided > div > div:nth-child(3) > div > button > span.filter-option.pull-left").click()
    print("Click en tipo")
    
    # Click en alquiler
    time.sleep(2)
    driver.find_element("css selector", "#form_guided > div > div:nth-child(3) > div > div > ul > li:nth-child(1) > a > span.text").click()
    print("Click en alquilar")
    
    # Click en buscar
    time.sleep(1)
    driver.find_element("css selector", "#form_guided > div > div.row > div.col-lg-4.col-md-4.col-sm-4.text-right > button").click()
    print("Click en buscar")
    
    # Inicializar contenedor de resultados
    lista_sopas = []
    
    # Iterar sobre las páginas
    for pagina in tqdm(range(1, paginas + 1)):
        # Navegar a la página de resultados
        pagina_url = f"https://www.redpiso.es/alquiler-viviendas/madrid/madrid/pagina-{pagina}"
        driver.get(pagina_url)
        print(f"Scraping página {pagina}")

        # Scroll para cargar contenido
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 400);")
        #print("Scroll")

        # Obtener el código fuente de la página y analizarlo con BeautifulSoup
        time.sleep(2)
        source = driver.page_source
        sopa = BeautifulSoup(source, "html.parser")
        print(f"Sopa creada {pagina}")

        # Almacenar resultados de la página
        lista_sopas.append(sopa)
    
    # Cerrar el navegador
    time.sleep(2)
    driver.quit()
    
    # Imprimir confirmación
    print("Scraping finalizado")
    
    return lista_sopas


def dataframe_redpiso(lista_sopas):
    """
    Extrae información de precios y descripciones de una lista de objetos BeautifulSoup y crea un DataFrame de pandas.

    Parámetros:
    lista_sopas (list): Una lista de objetos BeautifulSoup que contienen el HTML de las páginas de resultados.

    Devuelve:
    DataFrame: Un DataFrame de pandas con columnas 'Descripción' y 'Precio' que contiene la información extraída.
    """
    precios = []
    descripciones = []
    #oficinas = []
    
    for pagina in lista_sopas:
        pisos = pagina.find_all('div', class_='property-list')
        for piso in pisos:
            # Precio
            precio = piso.find('h3').text.strip()
            precios.append(precio)
            
            # Descripción    
            descripcion = piso.find('h5').text.strip()
            if descripcion:
                descripciones.append(descripcion)
            else:
                descripcion = "Sin descripción"
            
            # Oficina
            #oficina = piso.find('div', class_='property-list-contact-office').text.strip()
            #oficinas.append(oficina)
    
    df_redpiso = pd.DataFrame({
        #'Oficina': oficinas,
        'Descripcion': descripciones,
        'Precio': precios
    })
    
    return df_redpiso


def extraer_distrito(texto):
    """
    Extrae el nombre del distrito de un texto que sigue un formato específico.

    Parámetros:
    texto (str): La cadena de texto que contiene la dirección.

    Devuelve:
    str: El nombre del distrito si se encuentra en el texto; de lo contrario, devuelve "Distrito no identificado".
    """
    patron = r', ([^,]+), Madrid, Madrid$'
    coincidencia = re.search(patron, texto)
    if coincidencia:
        return coincidencia.group(1)
    else:
        return "Distrito no identificado"


def scraping_ayuntamiento():
    """
    Configura el navegador Chrome, abre la página especificada y realiza una serie de clics y desplazamientos
    para descargar datos en formato CSV.

    Parámetros:
    No hay parámetros de entrada.

    Devuelve:
    No hay valores de retorno. La función descarga un archivo CSV en la ruta especificada.
    """

    chrome_options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": "/Users/davidfranco/Library/CloudStorage/OneDrive-Personal/Hackio/Jupyter/Proyecto5-ProyectoLibre-PreciosAlquileresMadrid/datos/origen",  # ruta de descarga
        "download.prompt_for_download": False,   # desactiva el diálogo que Chrome normalmente muestra para pedir confirmación del usuario antes de descargar un archivo
        "directory_upgrade": True,    # hace que Chrome actualice el directorio de descarga predeterminado a la nueva ubicación especificada por download.default_directory si esta ha cambiado.
    }

    url = "https://servpub.madrid.es/CSEBD_WBINTER/seleccionSerie.html?numSerie=0307010000022"

    # Pasamos diccionario de preferencias a Chrome
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    driver.maximize_window()
    sleep(2)

    # Aceptamos cookies
    driver.find_element("css selector", "#iam-cookie-control-modal-action-primary").click()
    print("Cookies aceptadas")
    sleep(2)

    # Scroll a opciones
    element1 = driver.find_element("css selector", "#filtroSeries > div > div.bg-fluid0 > div > div.container > div > div > table:nth-child(2) > tbody > tr:nth-child(2) > td:nth-child(1)")
    driver.execute_script("arguments[0].scrollIntoView();", element1)
    sleep(1)

    # Click todos distritos
    driver.find_element("css selector", "#check186").click()
    print("Click en todos los distritos")
    sleep(2)

    # Click en totales barrios
    driver.find_element("css selector", "#checkTotales650").click()
    print("Click en totales barrios")
    sleep(2)

    # Click en todos periodos
    driver.find_element("css selector", "#check435").click()
    print("Click en todos los períodos")
    sleep(2)

    # Click en tipo medida todo
    driver.find_element("css selector", "#check360").click()
    print("Click en todas las medidas")
    sleep(2)

    # Scroll a botones
    element2 = driver.find_element("css selector", "#filtroSeries > div > div.content > div > div > div")
    driver.execute_script("arguments[0].scrollIntoView();", element2)
    sleep(2)

    # Click en nacionalidad todo
    driver.find_element("css selector", "#check382").click()
    print("Click en todas las nacionalidades")
    sleep(2)

    # Click en generar CSV
    driver.find_element("css selector", "#botonCsv").click()
    print("Click en generar CSV")
    sleep(5)

    driver.quit()


def scraping_ine():
    """
    Configura el navegador Chrome, abre la página del INE y realiza una serie de clics y desplazamientos
    para descargar datos en formato CSV.

    Parámetros:
    No hay parámetros de entrada.

    Devuelve:
    No hay valores de retorno. La función descarga un archivo CSV en la ruta especificada.
    """
    chrome_options = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": "/Users/davidfranco/Library/CloudStorage/OneDrive-Personal/Hackio/Jupyter/Proyecto5-ProyectoLibre-PreciosAlquileresMadrid/datos/origen", #ruta de descarga
        "download.prompt_for_download": False,   # desactiva el diálogo que Chrome normalmente muestra para pedir confirmación del usuario antes de descargar un archivo
        "directory_upgrade": True,    # hace que Chrome actualice el directorio de descarga predeterminado a la nueva ubicación especificada por download.default_directory si esta ha cambiado.
    }

    url = "https://www.ine.es/jaxiT3/Tabla.htm?t=31097&L=0"

    # Pasamos diccionario de preferencias a Chrome
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    driver.maximize_window()
    sleep(2)

    # Aceptamos cookies
    driver.find_element("css selector", "#aceptarCookie").click()
    print("Cookies aceptadas")
    sleep(2)

    # Clicks quitar municipios, distritos, secciones
    driver.find_element("css selector", "#selCri_0").click()
    sleep(1)
    driver.find_element("css selector", "#selCri_1").click()
    sleep(1)
    driver.find_element("css selector", "#selCri_2").click()
    sleep(1)
    print("Quitadas opciones por defecto")

    # Click todos años
    driver.find_element("css selector", "#caja_periodo > div > fieldset > div.capaSelecTodosNinguno > button.opcionesvarDer").click()
    print("Click en todos los años")
    sleep(1)

    # Click abrir Madrid
    driver.find_element("css selector", "#nt_1374330").click()
    print("Desplegable Madrid abierto")

    # Click en distritos
    driver.find_element("css selector", "#selchld_1374330").click()
    print("Click en distritos")
    sleep(1)

    # Click en botón descarga 
    driver.find_element("css selector", "#btnDescarga > i").click()
    print("Click en descarga")
    sleep(2)

    # Entrar en iframe
    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located(("xpath", '//*[@id="thickBoxINEfrm"]')))
    driver.switch_to.frame(iframe)
    sleep(2)

    # Click en CSV
    driver.find_element("css selector", "body > ul > li:nth-child(4) > a").click()
    print("Click en CSV")
    sleep(5)

    driver.quit()


def dbeaver_crear_db(database_name):
    """
    Crea una base de datos de PostgreSQL si aún no existe.

    Parámetros:
    -----------
    database_name : str
        El nombre de la base de datos a crear.

    Esta función se conecta al servidor PostgreSQL usando credenciales de usuario, verifica si una base 
    de datos con el nombre dado existe y la crea si no existe. Si ocurre un error de conexión, la función 
    imprimirá el tipo específico de error, como una contraseña incorrecta o un problema de conexión.

    Dependencias:
    -------------
    Requiere el paquete psycopg2 y las siguientes variables globales:
    - dbeaver_user: str - El nombre de usuario para conectarse a PostgreSQL.
    - dbeaver_pw: str - La contraseña asociada con el nombre de usuario.

    Retorna:
    --------
    None
    """

    try:
        conexion = psycopg2.connect(
            user=dbeaver_user,
            password=dbeaver_pw,
            host="localhost",
            port="5432"
        )

        # Crear un cursor con la nueva conexión
        cursor = conexion.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
        
        # Almacenar el resultado de fetchone; si existe, tendrá una fila, de lo contrario None
        bbdd_existe = cursor.fetchone()
        
        # Si bbdd_existe es None, crear la base de datos
        if not bbdd_existe:
            cursor.execute(f"CREATE DATABASE {database_name};")
            print(f"Base de datos {database_name} creada con éxito")
        else:
            print("La base de datos ya existe")
            
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

    except OperationalError as e:
        if e.pgcode == errorcodes.INVALID_PASSWORD:
            print("Contraseña es errónea")
        elif e.pgcode == errorcodes.CONNECTION_EXCEPTION:
            print("Error de conexión")
        else:
            print(f"Ocurrió el error {e}")


def dbeaver_conexion(database):
    """
    Establece una conexión a una base de datos DBeaver.

    Args:
        database (str): El nombre de la base de datos.

    Returns:
        connection: Un objeto de conexión a la base de datos.
    """
    try:
        conexion = psycopg2.connect(
            database=database,
            user=dbeaver_user,
            password=dbeaver_pw,
            host="localhost",
            port="5432"
        )
    except OperationalError as e:
        if e.pgcode == errorcodes.INVALID_PASSWORD:
            print("Contraseña es errónea")
        elif e.pgcode == errorcodes.CONNECTION_EXCEPTION:
            print("Error de conexión")
        else:
            print(f"Ocurrió el error {e}")

    return conexion


def dbeaver_fetch(conexion, query):
    """
    Ejecuta una consulta y obtiene los resultados en un dataframe.

    Args:
        conexion (connection): Un objeto de conexión a la base de datos.
        query (str): La consulta SQL a ejecutar.

    Returns:
        list: Los resultados de la consulta en un dataframe.
    """
    cursor = conexion.cursor()
    cursor.execute(query)
    # resultado_query = cursor.fetchall()
    # Si quisiéramos que el resultado fuera en forma de lista podríamos utilizar esta línea de código.
    # En este caso, sin embargo, nos interesa obtener directamente DFs.
    
    df = pd.DataFrame(cursor.fetchall())
    df.columns = [col[0] for col in cursor.description]

    cursor.close()
    conexion.close()

    return df


def dbeaver_commit(conexion, query, *values):
    """
    Ejecuta una consulta y realiza un commit de los cambios.

    Args:
        conexion (connection): Un objeto de conexión a la base de datos.
        query (str): La consulta SQL a ejecutar.
        *values: Los valores a incluir en la consulta.

    Returns:
        str: Un mensaje de confirmación después del commit.
    """
    cursor = conexion.cursor()
    cursor.execute(query, *values)
    conexion.commit()
    cursor.close()
    conexion.close()
    return print("Commit realizado")


def dbeaver_commitmany(conexion, query, *values):
    """
    Ejecuta múltiples consultas y realiza un commit de los cambios.

    Args:
        conexion (connection): Un objeto de conexión a la base de datos.
        query (str): La consulta SQL a ejecutar.
        *values: Los valores a incluir en la consulta.

    Returns:
        str: Un mensaje de confirmación después del commit.
    """
    cursor = conexion.cursor()
    cursor.executemany(query, *values)
    conexion.commit()
    cursor.close()
    conexion.close()
    return print("Commit realizado")

