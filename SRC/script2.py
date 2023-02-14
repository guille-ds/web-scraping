import time
import json
import re
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def parserFunc():
    # FLAGS
    parser = ArgumentParser(description="Nos imprime los parámetros")
    parser.add_argument("mode", type=str, nargs="+", choices=["list", "get"]) # parámetro que indica el modo (list o get) que queremos.
    parser.add_argument("code", type=str, nargs="+") # parámetro que indica el schoolID que queremos.
    args = parser.parse_args()
    mode = args.mode
    code = args.code
    return mode, code

if __name__ == '__main__':
    mode, codigoCole = parserFunc()

# DEFINICION DE FUNCIONES:
def dataExtract():
    # BUSQUEDA Y EXTRACCION DE DATOS DE UN COLEGIO
    out={}
    i=0
    if soup.select('div strong[class="g-font-size-11"]'):
        schoolID = [soup.select('div strong[class="g-font-size-11"]')[1].text]
        if codigoCole != schoolID:
            print("El código solicitado no existe")
            exit()
        out["schoolID"] = schoolID
        i+=1
    if soup.find('span', attrs={'itemprop':'faxNumber'}): 
        out["fax"] = soup.find('span', attrs={'itemprop':'faxNumber'}).text
        i+=1
    if soup.find_all('span', attrs={'itemprop':'title'}):
        e = soup.find_all('span', attrs={'itemprop':'title'})
        out["regionID"] = re.findall("\w.+", e[1].text)[0].rstrip()
        # TO-DO: cityID tiene que llamar a API de micole para sacar ID
        out["cityID"] = re.findall("\w.+", e[2].text)[0].rstrip()
        out["location"] = re.findall("\w.+", e[2].text)[0].rstrip()
        out["name"] = re.findall("\w.+",e[3].text)[0].rstrip()
        i+=4
    if soup.select('div strong[class="g-font-size-11"]'):
        e = soup.select('div strong[class="g-font-size-11"]')
        out["typeID"] = e[3].text
        out["owner"] = e[4].text
        out["scopeID"] = e[2].text
        i+=3
    if soup.select('aside ul li span'):
        out["postal"] = int(re.findall("\d{5}",soup.select('aside ul li span')[0].text)[0])
        i+=1
    if soup.find('span', attrs={'itemprop':'tel'}):
        out["phone"] = soup.find('span', attrs={'itemprop':'tel'}).text
        i+=1
    if soup.find('span', attrs={'itemprop':'email'}):
        out["accessemail"] = soup.find('span', attrs={'itemprop':'email'}).text
        i+=1
    if soup.find('span', attrs={'itemprop':'url'}):
        out["website"] = soup.find('span', attrs={'itemprop':'url'}).text
        i+=1
    if soup.select('aside ul li span'):
        out["address"] = soup.select('aside ul li span')[0].text
        i+=1

    '''
    if soup.select('aside ul li span'): 
        out["location"] = soup.select('aside ul li span')[1].text
        i+=1
    '''

    if soup.find('li', attrs={'data-original-title':'Facebook'}):
        facebook = soup.find('li', attrs={'data-original-title':'Facebook'}).a['href']
        if "Busco-Colegio" not in facebook:
            out["facebook"] = facebook
            i+=1
    if soup.find('li', attrs={'data-original-title':'Twitter'}):
        twitter = soup.find('li', attrs={'data-original-title':'Twitter'}).a['href']
        if "buscocolegio" not in twitter:
            out["twitter"] = twitter
            i+=1
    if soup.find('li', attrs={'data-original-title':'Youtube'}):
        youtube = soup.find('li', attrs={'data-original-title':'Youtube'}).a['href']
        if "UCZgmJ15BL5f3DtpRcZroc0Q" not in youtube:
            out["youtube"] = youtube
            i+=1
    if soup.find('img', attrs={'class':'img-fluid mx-auto d-block'}):
        out["logo"] = soup.find('img', attrs={'class':'img-fluid mx-auto d-block'})['src']
        i+=1
    if soup.select('#gMap iframe'):
        out["latitude"] = float(re.findall("\-?\d+\.+\d+", soup.select('#gMap iframe')[0]['src'])[0])
        out["longitude"] = float(re.findall("\-?\d+\.+\d+", soup.select('#gMap iframe')[0]['src'])[1])
        i+=2
    if soup.find(string=" Nº Alumnos"):
        out["totalStudents"] = int(soup.find(string=" Nº Alumnos").next.next.text)
        i+=1
    if soup.select('#pkg-servicios div'):
        serv = soup.select('#pkg-servicios div')[0].text.replace('\n',"///").lower()
        out["trans"] = True if 'ruta' in serv or 'transporte' in serv else False
        out["horario"] = True if 'horario ampliado' in serv or 'horario extendido' in serv else False
        out["comedor"] = True if 'comedor' in serv else False
        out["cocina"] = True if 'cocina' in serv else False
        out["activities"] = True if 'actividades extaescolares' in serv or 'clases extraescolares' in serv else False
        i+=5

    print (i, "/ 26 datos extraídos")
    out = json.dumps(out)
    print(out)
    return out

'''
[{"school":{"field1":1, "field2":"value", "field3":"2020-01-01"},
"school_language":[{"languageID":1,"level":"Nativo"},{"languageID":2,"level":"Medio"}]},
"school_stage":{},
"school_result":{}

{"school":{"field1":2,"field2":"value","field3":"2020-01-02"},
"school_language":[{"languageID":2,"level":"Nativo"},{"languageID":3,"level":"Bajo"}]}]
'''


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

# --------------------------

if mode[0] == "get":
    url = f'https://www.buscocolegio.com/Colegio/detalles-colegio.action?id={codigoCole[0]}' 
    print(url)
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    dataExtract()

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

#----------------------------------------