# Proyecto 5: Análisis de los precios del alquiler en los distritos de Madrid, demografía y la cantidad de alojamientos turísticos

![imagen](images/header.jpg)


## Planteamiento del problema: **El mercado de la vivienda de alquiler en la capital de España**

- El mercado de alquiler de viviendas en Madrid ha experimentado un crecimiento sostenido en la última década, impulsado tanto por la demanda de los residentes locales como por el interés de extranjeros en vivir en la capital española. Esta demanda ha provocado un aumento considerable en los precios de alquiler, dificultando el acceso a la vivienda, especialmente para los jóvenes y aquellos con ingresos moderados. Además, la escasez de oferta y el dinamismo de Madrid como centro económico y cultural han contribuido a que el mercado de alquiler se mantenga altamente competitivo y sometido a la presión de varios factores económicos y sociales.

- Uno de los factores que ha intensificado esta situación es el crecimiento de los alojamientos turísticos, especialmente aquellos que se gestionan a través de plataformas como Airbnb. Estos alojamientos, situados generalmente en áreas céntricas, han reducido el número de viviendas disponibles para alquiler residencial, impactando aún más en la oferta y elevando los precios. Esto ha llevado a algunos barrios a experimentar cambios en su tejido social y a que las autoridades busquen equilibrar la actividad turística con el acceso a la vivienda, implementando regulaciones para frenar la proliferación de estos alojamientos en zonas residenciales.

- En este proyecto analizaremos los precios del alquiler en los 21 distritos de Madrid, la cantidad de alojamientos turísticos y cómo varían los ingresos por hogar y la cantidad de extranjeros que reside en cada uno de ellos. Utilizaremos datos de viviendas en plataformas como Idealista, Redpiso, AirBnB y datos estadísticos del Instituto Nacional de Estadística (INE) y el Ayuntamiento de Madrid, capturados haciendo uso de herramientas tecnológicas.


## Objetivos del Proyecto

1. **Integración de Múltiples Fuentes**: Combinar APIs y datos de scraping para obtener una vista enriquecida de del tema elegido.

2. **Base de Datos**: Diseñar y estructurar los datos en una base de datos adecuada a los requisitos del análisis.

3. **Análisis Visual**: Utilizar visualizaciones en Python para comunicar hallazgos clave y responder preguntas de interés sobre el tema seleccionado.


## Estructura del repositorio

El proyecto está construido de la siguiente manera:

- **datos/**: Carpeta que contiene archivos `.csv`, `.json` o `.pkl` generados durante la captura y tratamiento de los datos.

- **images/**: Carpeta que contiene archivos de imagen generados durante la ejecución del código o de fuentes externas.

- **notebooks/**: Carpeta que contiene los archivos `.ipynb` utilizados en la captura y tratamiento de los datos. Están numerados para su ejecución secuencial.
  - `1_ExtracciónTransformación`
  - `2_CargaDDBB`
  - `3_QueriesVisualizaciónAnálisis`

- **src/**: Carpeta que contiene los archivos `.py`, con las funciones y variables utilizadas en los distintos notebooks.
  - `soporte_funciones.py`
  - `soporte_variables.py`

- `.gitignore`: Archivo que contiene los archivos y extensiones que no se subirán a nuestro repositorio, como los archivos .env, que contienen contraseñas.


## Lenguaje, librerías y temporalidad
- El proyecto fué elaborado con Python 3.9 y múltiples librerías de soporte:

    - *Librerías para el tratamiento de datos*
- [Pandas](https://pandas.pydata.org/docs/)
- [Numpy](https://numpy.org/doc/)

    - *Librerías para captura de datos*
- [Selenium](https://selenium-python.readthedocs.io)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests](https://pypi.org/project/requests/)

    - *Librerías para gestión de tiempos*
- [Time](https://docs.python.org/3/library/time.html)
- [tqdm](https://numpy.org/doc/)

    - *Librerías para graficar*
- [Plotly](https://plotly.com/python/)
- [Seaborn](https://seaborn.pydata.org)
- [Matplotlib](https://matplotlib.org/stable/index.html)

    - *Librería para gestionar tokens y contraseñas*
- [DotEnv](https://pypi.org/project/python-dotenv/)

    - *Librería para controlar parámetros del sistema*
- [Sys](https://docs.python.org/3/library/sys.html)

    - *Librería para controlar ficheros*
- [os](https://docs.python.org/3/library/os.html)

    - *Librería para conexión a bases de datos SQL*
- [psycopg2](https://www.psycopg.org/docs/)

    - *Librería para la gestión de avisos*
- [warnings](https://docs.python.org/3/library/warnings.html)


- Este proyecto es funcional a fecha 2 de noviembre de 2024, sin embargo, dependendiendo de terceros para la captura de datos (scraping de sitios web y APIs), los mismos podrían no estar disponibles o requerir de modificaciones para su tratamiento y captura en el futuro.


## Instalación

1. Descarga DBeaver. Puedes consultar la documentación de DBeaver [aquí](https://dbeaver.com/docs/dbeaver/).

2. Crea una cuenta gratuita en [Rapidapi](https://rapidapi.com). Suscríbete a las APIs:
   - [AirBnB](https://rapidapi.com/3b-data-3b-data-default/api/airbnb13/)
   - [Idealista](https://rapidapi.com/scraperium/api/idealista7)
   - Ten en cuenta que estas APIs, a pesar de ser gratuitas, cuentan con limitaciones en su modo gratis. Consulta la documentación en los enlaces.
   - Copia la key en cualquiera de las dos APIs, la utilizarás en el paso 5.

3. Clona el repositorio
   ```sh
   git clone https://github.com/davfranco1/Proyecto5-ProyectoLibre-PreciosAlquileresMadrid.git
   ```
4. Instala las librerías que aparecen en el apartado anterior. Utiliza en tu notebook de Jupyter:
   ```sh
   pip install nombre_librería
   ```
5. Genera un archivo para almacenar tus tokens y contraseñas, en este caso para la base de datos de DBeaver:
   Entra en la carpeta `src` y crea `.env`, que contenga el siguiente script, sin olvidar las comillas:
   ```js
   dbeaver_pw = 'contraseña_de_tu_base_de_datos'
   dbeaver_user = 'usuario_de_tu_base_de_datos'
   rapiapi_key = 'tu_key_de_rapiadpi'
   ```

6. Cambia la URL del repositorio remoto para evitar cambios al original.
   ```sh
   git remote set-url origin usuario_github/nombre_repositorio
   git remote -v # Confirma los cambios
   ```

7. Ejecuta el código en los notebooks, modificándolo si es necesario.


## Estructura de la base de datos

<img src="images/Diagrama_ER.png" width="400">

- Este gráfico muestra el diseño de una base de datos relacional en forma de estrella con seis tablas: en el centro, "distritos", rodeada por:
   - Tabla de alojamientos turísticos: "airbnb".
   - Tablas de viviendas en alquiler: "redpiso" e "idealista".
   - Tablas demográficas: "ingresos_hogar" y "población".

- El diseño destaca por varias razones:

1. **Normalización:** Las tablas están normalizadas, lo que reduce la redundancia y mejora la integridad de los datos. Cada tabla tiene una clave primaria única (PK) que identifica de manera única cada registro. Cuando se tienen "formas normales", los datos se dividen en tablas relacionadas que garantizan que cada dato se almacene solo una vez.

2. **Relaciones claras:** Las relaciones entre las tablas están claramente definidas mediante claves foráneas, o foreign keys (FK). Esto facilita la consulta y el mantenimiento de la base de datos.

3. **Escalabilidad:** Este diseño permite agregar nuevas fuentes de información, por ejemplo, otros datos demográficos, información climática, de servicios o de transportes.

4. **Consultas eficientes:** La estructura facilita la realización de consultas complejas. Por ejemplo, se puede obtener información de precios por distritos específicos, utilizando las relaciones definidas.

- Un diseño es eficiente y bien estructurado cuando es escalable y facilita la gestión y consulta de los datos almacenados.


## Conclusiones y Próximos Pasos

- Te invito a descargar el [PDF Resultados](Resumen.pdf), que resume de manera gráfica el análisis preparado.

- Además, el notebook [3_QueriesVisualizaciónAnálisis](https://github.com/davfranco1/Proyecto5-ProyectoLibre-PreciosAlquileresMadrid/blob/main/notebooks/3_QueriesVisualizaciónAnálisis.ipynb), contiene explicaciones de los datos y las visualizaciones generadas durante el proyecto.


## Autor

David Franco - [LinkedIn](https://linkedin.com/in/franco-david)

Enlace del proyecto: [https://github.com/davfranco1/Proyecto5-ProyectoLibre-PreciosAlquileresMadrid](https://github.com/davfranco1/Proyecto5-ProyectoLibre-PreciosAlquileresMadrid)
