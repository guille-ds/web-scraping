import time
import json
import re
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ------- FUNCIONES --------

def parserFunc():
    # FLAGS
    parser = ArgumentParser(description="Nos imprime los parámetros")
    parser.add_argument("mode", type=str, nargs="+", choices=["list", "get"]) # parámetro que indica el modo (list o get) que queremos.
    parser.add_argument("code", type=str, nargs="+") # parámetro que indica el schoolID que queremos.
    args = parser.parse_args()
    mode = args.mode
    code = args.code
    return mode, code
          
def dataExtract():
    # extrae todos los datos de cada colegio, los ordena y devuelve un json.
    # SCHOOL
    
    if soup.find('span', attrs={'itemprop':'faxNumber'}): 
        out["fax"] = soup.find('span', attrs={'itemprop':'faxNumber'}).text
    if soup.find_all('span', attrs={'itemprop':'title'}):
        e = soup.find_all('span', attrs={'itemprop':'title'})
        provincia = re.findall("\w.+", e[1].text)[0].rstrip()
        regionID = busca_en_api("regions", provincia)
        out["regionID"] = regionID
        municipio = re.findall("\w.+", e[2].text)[0].rstrip()
        cityID = busca_en_api("regions/14", municipio)
        out["cityID"] = cityID
        out["location"] = re.findall("\w.+", e[2].text)[0].rstrip()
        out["name"] = re.findall("\w.+",e[3].text)[0].rstrip()   
    if soup.select('div strong[class="g-font-size-11"]'):
        e = soup.select('div strong[class="g-font-size-11"]')
        out["typeID"] = soup.find(string="Tipo Centro").next.next.text
        icono = soup.find("i", class_="icon-pin d-inline-block g-font-size-50 g-color-otros-colegios g-mb-30")
        scope = [e.string for e in icono.next_siblings][3]
        out["scope"] = busca_en_api("scopes",scope)
    if soup.find(string="Titular"):
        out["owner"] = soup.find(string="Titular").next.next.text
    if soup.select('aside ul li span'):
        out["postal"] = int(re.findall("\d{5}",soup.select('aside ul li span')[0].text)[0])
    if soup.find('span', attrs={'itemprop':'tel'}):
        out["phone"] = soup.find('span', attrs={'itemprop':'tel'}).text.replace(" ", "")
    if soup.find('span', attrs={'itemprop':'email'}):
        out["accessemail"] = soup.find('span', attrs={'itemprop':'email'}).text
    if soup.find('span', attrs={'itemprop':'url'}):
        out["website"] = soup.find('span', attrs={'itemprop':'url'}).text
    if soup.select('aside ul li span'):
        out["address"] = soup.select('aside ul li span')[0].text
    if soup.find('li', attrs={'data-original-title':'Facebook'}):
        facebook = soup.find('li', attrs={'data-original-title':'Facebook'}).a['href']
        if "Busco-Colegio" not in facebook:
            out["facebook"] = facebook
    if soup.find('li', attrs={'data-original-title':'Twitter'}):
        twitter = soup.find('li', attrs={'data-original-title':'Twitter'}).a['href']
        if "buscocolegio" not in twitter:
            out["twitter"] = twitter
    if soup.find('li', attrs={'data-original-title':'Canal youtube'}):
        youtube = soup.find('li', attrs={'data-original-title':'Canal youtube'}).a['href']
        if "UCZgmJ15BL5f3DtpRcZroc0Q" not in youtube:
            out["youtube"] = youtube
    if soup.find('img', attrs={'class':'img-fluid mx-auto d-block'}):
        logo = soup.find('img', attrs={'class':'img-fluid mx-auto d-block'})['src']
        if "47007653_1.jpg" not in logo:
            out["logo"] = logo
    if soup.select('#gMap iframe'):
        out["latitude"] = float(re.findall("\-?\d+\.+\d+", soup.select('#gMap iframe')[0]['src'])[0])
        out["longitude"] = float(re.findall("\-?\d+\.+\d+", soup.select('#gMap iframe')[0]['src'])[1])
    if soup.find(string=" Nº Alumnos"):
        out["totalStudents"] = int(soup.find(string=" Nº Alumnos").next.next.text)
    if soup.select('#pkg-servicios div'):
        serv = soup.select('#pkg-servicios div')[0].text.replace('\n',"///").lower()
        out["trans"] = True if 'ruta' in serv or 'transporte' in serv else False
        out["horario"] = True if 'horario ampliado' in serv or 'horario extendido' in serv else False
        out["comedor"] = True if 'comedor' in serv else False
        if "cocina" in serv:
            out["cocina"] = 1
        elif "catering" in serv:
            out["cocina"] = 0
        out["activities"] = True if 'actividades extaescolares' in serv or 'clases extraescolares' in serv else False
        out["residencia"] = True if 'residencia' in serv else False
    out["religionID"] = 9
    if soup.find(string=" Info Adicional"):
        info = soup.find(string=" Info Adicional").next.next.text.lower()
        eduModels = [d["name"] for d in apiModels]
        out["educataionalModelID"]=1
        for e in eduModels:
            if e in info:
                out["educationalModelID"] = busca_en_api("edumodels", e)
        laico = ["laico", "laica"]
        religioso = ["católico", "evangelio", "evangelizar", "cristiano", "cristiana", "biblia", "eucaristía", "dios", "virgen"]
        for e in laico:
            if e in info:
                out["religionID"] = 1
        for e in religioso:
            if e in info:
                out["religionID"] = 2
    if soup.find(string="Calendario Escolar"):
        links = soup.find(string="Calendario Escolar").parent.parent
        for e in links:
            try:
                link = (re.findall("(?<=\').+(?=\')", e.attrs['href'])[0])
                if "buscolegio" not in link:
                    out["calendario_url"] = link
            except: pass
    
    check = [("Clases Particulares","clases_particulares_url"),("Campamentos","campamentos_url")]
    for e in check:
        if soup.find(string=e[0]):
            links = soup.find(string=e[0]).parent.parent.parent
            for e in links:
                try:
                    link = e.attrs['href']
                    if ".action" not in link:
                        out[e[1]] = link
                except: pass
                
    if soup.find(string="Becas y Ayudas al Estudio"):
        links = soup.find(string="Becas y Ayudas al Estudio").parent.parent.parent
        for e in links:
            try:
                link = e.attrs['href']
                if "buscocolegio" not in link:
                    out["becas_ayudas_url"] = link
            except: pass
    out["origin"] = "buscocolegio"
    if soup.find(string="Vídeo"):
        foto = soup.find('img', attrs={'class':'img-fluid w-100'})['src']
        video = re.findall("(?<=vi/).+(?=\/\d.jpg)", foto)[0]
        out["video_url"] = "youtube.com/watch?v="+video
        i+=1
    school["school"] = out
    print("extrayendo datos school")
    
    # SCHOOL_LANGUAGE
    if soup.find(string="Bilingüe"):
        idiomas = re.findall("\w+",soup.find(string="Bilingüe").next.next.text)
        listado = []
        for idioma in idiomas:
            lang = {}
            lang["languageID"] = idioma; lang["level"] = "Medio"
            listado.append(lang)
        school["school_language"] = listado
        print("extrayendo datos school_language")

    
    # SCHOOL_VALUATIONS
    school_valuations["source"] = "buscocolegio"
    school_valuations["votes"] = 0
    alumn = 0
    prof = 0
    inst = 0
    if soup.find(string=" Alumnado"):
        alumn = float(soup.find(string=" Alumnado").parent.parent.span['data-rating'])
        school_valuations["students"] = alumn
    if soup.find(string=" Profesorado"):
        prof = float(soup.find(string=" Profesorado").parent.parent.span['data-rating'])
        school_valuations["stuff"] = prof
    if soup.find(string=" Instalaciones"):
        inst = float(soup.find(string=" Instalaciones").parent.parent.span['data-rating'])
        school_valuations["installations"] = inst
    if soup.find(string=re.compile("\d+\s{1}Opiniones.")):
        opiniones = soup.find(string=re.compile("\d+\s{1}Opiniones."))
        num = int(re.findall("\d+", opiniones)[0])
        school_valuations["votes"] = num
    if alumn+prof+inst!=0:
        school_valuations["total"] = round((alumn+prof+inst)/3,4)
        
    school["school_valuations"] = school_valuations
    print("extrayendo datos school_valuations")

    # SCHOOL_RESULT (notas)   
    if soup.find_all("script", attrs={"type":"text/javascript"}):
        print("extrayendo datos school_result")
        listado = []
        scripts = soup.find_all("script", attrs={"type":"text/javascript"})
        for script in scripts:

            # PRUEBA DE ACCESO A LA UNIVERSIDAD (PAU)
            if "#notasSelectividad" in script.string:
                search = "#notasSelectividad"
                text = "notas_PAU"
                text_api = "PAU/EVAU"
                years, notas = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    courseID = busca_en_api("course", years[e])
                    if courseID != None:
                        temp["courseID"] = courseID
                    else:
                        print(f"Due to missing {elem[0]} courseID in api/courses, some {text}_data is missing. Please update")
                    temp["result"] = notas[e]
                    listado.append(temp)
            if "#alumnosSelectividad" in script.string:
                search = "#alumnosSelectividad"
                text = "alumnos_PAU"
                years, alumnos = extract_notas(script, search, text)
                for elem in list(zip(years, alumnos)):
                    courseID = busca_en_api("course", elem[0])
                    if courseID!=None:
                        for e in listado:
                            if e["courseID"] == courseID:
                                e["students"] = elem[1]
                    else:
                        print(f"Due to missing {elem[0]} courseID in api/courses, some {text}_data is missing. Please update")
            if "#aptosSelectividad" in script.string:
                search = "#aptosSelectividad"
                text = "aptos_PAU"
                years, aptos = extract_notas(script, search, text)
                for elem in list(zip(years, aptos)):
                    courseID = busca_en_api("course", elem[0])
                    if courseID!=None:
                        for e in listado:
                            if e["courseID"] == courseID:
                                e["competent"] = elem[1]
                    else:
                        print(f"Due to missing {elem[0]} courseID in api/courses, some {text}_data is missing. Please update")
                 
            # EVOLUCION RANKING NOTA PAU, EBAU
            if "#rankingSelectividad" in script.string:
                search = "#rankingSelectividad"
                text = "rank_PAU"
                text_api = "EVOLUCIÓN RANKING NOTA PAU, EvAU, EBAU (Selectividad)"
                years, rank = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["result"] = rank[e]
                    listado.append(temp)
            if "#totalSelectividad" in script.string:
                search = "#totalSelectividad"
                text = "total_PAU"
                years, total = extract_notas(script, search, text)
                for elem in list(zip(years, total)):
                    courseID = busca_en_api("course", elem[0])
                    if courseID!=None:
                        for e in listado:
                            if e["examID"] == temp["examID"] and e["courseID"] == courseID:
                                e["total"] = elem[1]
                    else:
                        print(f"Due to missing {elem[0]} courseID in api/courses, some {text}_data is missing. Please update")
                
            # CDI3
            if "#notasCDI3e" in script.string:
                search = "#notasCDI3e"
                text = "notas_CDI3"
                text_api = "CDI 3º ESO"
                years, notasCDI3 = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["result"] = notasCDI3[e]
                    listado.append(temp)
            if "#aptosCDI3e" in script.string:
                search = "#aptosCDI3e"
                text = "aptos_CDI3"
                years, aptosCDI3 = extract_notas(script, search, text)
                for elem in list(zip(years, aptosCDI3)):
                    courseID = busca_en_api("course", elem[0])
                    if courseID!=None:
                        for e in listado:
                            if e["examID"] == temp["examID"] and e["courseID"] == courseID:
                                e["competent"] = elem[1]
            
            # CDI6
            if "#notasCDI6p" in script.string:
                search = "#notasCDI6p"
                text = "notas_CDI6"
                text_api = "CDI 6º Primaria"
                years, notasCDI6 = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["result"] = notasCDI6[e]
                    listado.append(temp)
            if "#aptosCDI6p" in script.string:
                search = "#aptosCDI6p"
                text = "aptos_CDI6"
                years, aptosCDI6 = extract_notas(script, search, text)
                for elem in list(zip(years, aptosCDI6)):
                    courseID = busca_en_api("course", elem[0])
                    if courseID!=None:
                        for e in listado:
                            if e["examID"] == temp["examID"] and e["courseID"] == courseID:
                                e["competent"] = elem[1]
                
            # NOTAS LEA
            if "#notasLEA" in script.string:
                search = "#notasLEA"
                text = "notas_LEA"
                text_api = "LEA 2º Primaria"
                years, notasLEA = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["result"] = notasLEA[e]
                    listado.append(temp)
            
            # APTOS ESO
            if "#aptosESO" in script.string:
                search = "#aptosESO"
                text = "aptos_ESO"
                text_api = "TITULACIÓN EN EDUCACIÓN SECUNDARIA"
                years, aptosESO = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["competent"] = aptosESO[e]
                    listado.append(temp)
            
            # BACHILLERATO
            if "#notasBach" in script.string:
                search = "#notasBach"
                text = "notas_Bach"
                text_api = "TITULACIÓN EN EDUCACIÓN SECUNDARIA (BACHILLERATO)"
                try:
                    years, notasBach = extract_notas(script, search, text)
                    for e in range(len(years)):
                        temp = {}
                        temp["examID"] = busca_en_api("exam", text_api)
                        temp["courseID"] = busca_en_api("course", years[e])
                        temp["result"] = notasBach[e]
                        listado.append(temp)
                except: pass
            if "#aptosBach" in script.string:
                search = "#aptosBach"
                text = "aptos_Bach"
                years, aptosBach = extract_notas(script, search, text)
                try:
                    for elem in list(zip(years, aptosBach)):
                        courseID = busca_en_api("course", elem[0])
                        if courseID!=None:
                            for e in listado:
                                if e["examID"] == temp["examID"] and e["courseID"] == courseID:
                                    e["competent"] = elem[1] 
                except:
                    text_api = "TITULACIÓN EN EDUCACIÓN SECUNDARIA (BACHILLERATO)"
                    for e in range(len(years)):
                        temp = {}
                        temp["examID"] = busca_en_api("exam", text_api)
                        temp["courseID"] = busca_en_api("course", years[e])
                        temp["competent"] = aptosBach[e]
                        listado.append(temp)
                
            # NIVEL IDIOMAS 2º PRIMARIA
            if "#aptosIdioma2p" in script.string:
                search = "#aptosIdioma2p"
                text = "aptos_Idioma_2p"
                text_api = "PRUEBA EXTERNA EN CENTROS BILINGÜES 2º Primaria"
                years, aptosIdioma2 = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["competent"] = aptosIdioma2[e]
                    listado.append(temp) 
                
            # NIVEL IDIOMAS 4º PRIMARIA
            if "#aptosIdioma4p" in script.string:
                search = "#aptosIdioma4p"
                text = "aptos_Idioma_4p"
                text_api = "PRUEBA EXTERNA EN CENTROS BILINGÜES 4º Primaria"
                years, aptosIdioma4 = extract_notas(script, search, text)
                for e in range(len(years)):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["competent"] = aptosIdioma4[e]
                    listado.append(temp)
            
            # NIVEL IDIOMAS 6º PRIMARIA
            if "#aptosIdioma6p" in script.string:
                search = "#aptosIdioma6p"
                text = "aptos_Idioma_6p"
                text_api = "PRUEBA EXTERNA EN CENTROS BILINGÜES 6º Primaria"
                years, aptosIdioma6 = extract_notas(script, search, text)
                for i,e in enumerate(range(len(years))):
                    temp = {}
                    temp["examID"] = busca_en_api("exam", text_api)
                    temp["courseID"] = busca_en_api("course", years[e])
                    temp["competent"] = aptosIdioma6[e]
                    listado.append(temp)
        if len(listado)>0:
            school["school_result"] = listado
    

    
    # METADATA
    metadata = []
    if soup.find(id="pkg-info"):
        info = soup.find(id="pkg-info").div
        cabeceras = [e.text for e in info.find_all("h3") if e.text!=" Galería de Imágenes"]
        contenido = [e.get_text(separator=" ") for e in info.find_all("p")]
        todo = list(zip(cabeceras, contenido))
        for e in todo:
            temp = metaData("info",e)
            metadata.append(temp)

    if soup.find(id="pkg-servicios"):
        servicios = soup.find(id="pkg-servicios").div
        contenido = [e.get_text(separator=" ") for e in servicios.find_all("p")][1:]
        cabeceras = range(len(contenido))
        todo = list(zip(cabeceras, contenido))
        for e in todo:
            temp = metaData("servicios",e)
            metadata.append(temp)
    print("extrayendo datos school_metadata")

    school["school_metadata"] = metadata
    school["school"] = out
    print("type school pre return", type(school))
    return school

def extract_notas(script, search, text):
    # extrae datos referentes a las notas del colegio, imprime en terminal y devuelve 2 listas de curso y datos
    lineas = re.findall(f"(?<={search}).+(?=;)",script.string)
    years = ["-".join(re.findall("\d{4}", linea)) for linea in lineas]
    data = [[float(e.strip("><")) for e in re.findall("(>\d+<|>\d+.\d+<)", linea)][0] for linea in lineas]
    print(text, "\n", list(zip(years, data)), "\n-----------------------------")
    return years, data

def metaData(tag,e):
    # ordena metadata en estructura tipo diccionario y la añade a lista "metadata"
    temp = {}
    temp["source"] = "buscocolegio"
    temp["tag"] = tag
    temp["metakey"] = e[0]
    temp["metadata"] = e[1]
    return temp

def api_data (endpoint):
    # extrae la info de micole/api para poder asignar courseID y examID
    try:
        user = "micoleAPI"
        password = "M9^&yAzHTvVedh4="
        url = f"https://{user}:{password}@www.micole.net/api/{endpoint}"
        data = requests.get(url).text
        soup = BeautifulSoup(data, 'html.parser')
        new = json.loads(str(soup))
        return new
    except:
        print("No se ha podido conectar con la API")
    
def busca_en_api (tipo, text_api):
    # devuelve examID / courseID / cityID / regionID desde la API.
    if tipo == "exam":
        for e in apiExams:
            if text_api == e["name"]:
                return e["id"]
    elif tipo == "course":
        for i,e in enumerate(apiCourses):
            if text_api == e["name"]:
                return e["id"]
            elif text_api != e["name"] and i==len(apiCourses)-1:
                print("missing courseID in API")
                pass
    elif tipo == "regions/14":
        for i,e in enumerate(apiCities):
            if text_api.lower() == e["name"].lower():
                return e["id"]
            elif text_api != e["name"] and i==len(apiCities)-1:
                print(f"Missing cityID. No match in API for {text_api}")
                pass
    elif tipo == "regions":
        for e in apiRegions:
            if text_api.lower() == e["name"].lower():
                return e["id"]
    elif tipo == "scopes":
        for e in apiScopes:
            if text_api.lower() == e["name"].lower():
                return e["id"]
            elif "concertado" in text_api.lower() and "privado" in text_api.lower():
                return 4
            else:
                return 9
    elif tipo == "edumodels":
        for e in apiModels:
            if text_api.lower() == e["name"].lower():
                return e["id"]
            else:
                return 1

def customFichas(i):
    # MODIFICO DROPDOWN
    time.sleep(2)
    elemento = wd.find_element_by_xpath("/html/body/div[2]/form/div/div[2]/div/p/span[2]/select/option[2]")
    wd.execute_script("arguments[0].value = arguments[1]", elemento, numFichas)
    if i==1:
        wd.find_element_by_xpath("/html/body/div[2]/form/div/div[2]/div/p/span[2]/select/option[text()='15']").click()
        time.sleep(1)
        elemento = wd.find_element_by_xpath("/html/body/div[2]/form/div/div[2]/div/p/span[2]/select/option[2]")
        wd.execute_script("arguments[0].value = arguments[1]", elemento, numFichas)
    wd.execute_script("arguments[0].setAttribute('selected', 'selected')", elemento)
    time.sleep(2)

def extractor():
    # EXTRAIGO CODIGOS MEC
    presentUrl = wd.page_source
    soup = BeautifulSoup(presentUrl, 'html.parser')
    time.sleep(1)
    print("- extrayendo códigos MEC")
    for a in soup.find_all('a', href=codigoColegio):
        schoolID = (a['href'][-8::])
        codigosMec.append(schoolID)
    print("- extrayendo nombres de colegios")
    for a in soup.find_all('strong')[2::]:
        name = a.text
        nombresColes.append(name)

def codigoColegio(href):
    return href and re.compile("\/Colegio\/detalles-colegio.action\?id=\s*([^\n\r]*)").search(href)

# ------- EXECUTION --------

if __name__ == '__main__':
    mode, codigoCole = parserFunc()

def checker():
    schoolID = soup.find(string="Código").next.next.text
    if codigoCole[0] != schoolID:
        print("El código solicitado no existe")
        return
    else:
        out["schoolID"] = schoolID
        return 1
    
if mode[0] == "get":
    url = f'https://www.buscocolegio.com/Colegio/detalles-colegio.action?id={codigoCole[0]}'
    print(url)
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    out={}
    filtro = checker()
    if filtro == 1:
        school = {} #contiene todo
        school_language = {}
        school_result = {}
        school_comment = {}
        school_valuations = {}
        school_metadata = {}
        apiExams = api_data("exams")
        apiCourses = api_data("courses")
        apiCities = api_data("regions/14")
        apiRegions = api_data("regions")
        apiScopes = api_data("scopes")
        apiModels = api_data("educational-models")
        school = dataExtract()
        print("type school post return", type(school))
        school = json.dumps(school, indent=4, ensure_ascii=False)
        print("type school post dumps", type(school))
        print(school)
    
if mode[0] == "list" and codigoCole[0].lower() == "madrid":
    provincia = "Madrid"
    numFichas = int(input("----------\nIntroduce el número de colegios por página que quieres cargar.\nDependiendo de la máquina, un valor demasiado alto podría paralizar el proceso:\n"))
    scan = int(input("----------\nIntroduce el número de páginas que quieres recorrer. 0 si quieres recorrer todas:\n"))

    # ENTRO
    options = Options()
    options.headless = False
    wd = webdriver.Chrome(options=options, executable_path="/Users/guille/Documents/Scraping/chromedriver")
    print("--- Abriendo Web Driver")
    url = f"https://www.buscocolegio.com/{provincia}/buscador-de-colegios.jsp#busqueda"
    wd.get(url)
    wd.find_element_by_xpath("/html/body/section[2]/form/div/div/div[4]/a[2]").click()
    time.sleep(1)
    totalColegios = int(wd.find_element_by_xpath("/html/body/div[2]/form/div/div[2]/div/p/span[1]/button/span").text)

    if totalColegios%numFichas == 0:
        paginacion = totalColegios/numFichas
    else:
        paginacion = (totalColegios//numFichas)+1

    print (paginacion, "páginas disponibles")

    # PAGINO
    i=1
    codigosMec = []
    nombresColes = []
    if scan == 0:
        paginas = paginacion
    else:
        paginas = scan 

    while i < paginas:
        print("extrayendo información en página", i, "de", paginas, "...")
        customFichas(i)
        extractor()
        wd.execute_script(f"navegar({i}+1)")
        i+=1
        time.sleep(2)
    print("extrayendo información en página", paginas, "de", paginas, "...")
    extractor()

    # SALGO
    time.sleep(3)
    wd.quit()
    print("--- Cerrando Web Driver")

    print(len(codigosMec),"codigos MEC")
    print(len(nombresColes), "nombres de colegio")
    out = [{'id':(codigosMec[i]),'name':(nombresColes)[i]} for i in range(len(codigosMec))]
    out = json.dumps(out)
    print(out)
    print("--- Proceso finalizado")

#-----------------------------------------