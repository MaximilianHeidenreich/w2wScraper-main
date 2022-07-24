import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import os
import sys
import traceback

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

__location_file__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

__location_cwd__ = os.getcwd()


def esc(val:str) -> str:
    valx = str(val)
    mapping = {
        '\"': '~',
        '\'': '~',
        ';': ',',
        '|': ',',
        '\n': '+'
    }

    for k in mapping:
        valx = valx.replace(k, mapping[k])

    return valx


def map(val:any, mapping:dict, default:str='', strcmp:bool=False):
    for x in mapping.keys():
        xs = x
        ms = mapping[x]

        if strcmp:
            xs = str(xs)
            ms = str(ms)

        if xs == val:
            return ms

    return default



def getsel(soup:BeautifulSoup, selstr:str, attr:str=None, raw:bool=False, notnone:bool=True, strip:bool=False):
    ret = None
    for res in soup.select(selstr):
        if attr != None:
            ret  = res[attr]
        elif raw:
            ret = res
        else:
            ret = res.text
    

        # if html:
        #     return res.html
        # else: #text
        #     return res.text    

    if notnone and ret == None:
        return ''
    else:
        if strip == True:
            ret = ret.strip()

        return ret

def fill_arr(arr:list, cnt:int, default:any):
    ret = []

    for i in range(cnt):
        if len(arr) > i:
            ret.append(arr[i])
        else:
            ret.append(default)

    return ret


def re_groups(src_str:str, re_str:str, fnames:list=[], default:str='', error:str='?', skip0:bool=False, single:bool=False):
    #m = re.match('^(.+), (.{2})-(\d{4}) (.+)$', data['adr_full'])
    m = re.match(re_str, src_str)

    ret = {}

    for idx, fnf in enumerate(fnames):
        if idx == 0 and skip0:
            continue

        if fnf[0:2] == '//':
            continue

        #name:type:pos
        if ':' in fnf:
            (fnn, fnt, fnp) = fill_arr(fnf.split(':'), 3, '')
        else:
            fnn = fnf
            fnt = 'str'


        if m == None:
            ret[fnn] = default
        else:
            try:
                ret[fnn] = m.group(idx)
                if fnt == 'str':
                    ret[fnn] = str(ret[fnn])
                elif fnt == 'int':
                    ret[fnn] = int(ret[fnn])
                elif fnt == 'float':
                    ret[fnn] = float(ret[fnn])
            except Exception as e:
                ret[fnn] = error

        if single:
            return ret[fnn]


    return ret



def get_soup(url:str):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def detail(url:str, doprint:bool=False):

    mitarbeiter = {
        '1 – 4': 1,
        '5 – 9': 5,
        '10 – 19': 10,
        '20 – 49': 20,
        '50 – 99': 50,
        '100 – 199': 100,
        '200 – 499': 200,
        '500 – 999': 500,
        '1,000+': 1000,
    }

    map_country = {
        'AT': 'Austria',
        'DE': 'Germany',
        'CH': 'Switzerland',
        'IT': 'Italy',
        'FL': 'Liechtenstein',
        'SK': 'Slovakia',
        'CZ': 'Czech Republic',
        'HU': 'Hungary',
    }

    #ret = []
    #url = f"https://www.herold.at/gelbe-seiten/{bld_long}/hotel/?page={pnr}"
    #response = requests.get(url, headers=headers)

    data = {}

    #soup = BeautifulSoup(response.text, 'html.parser')
    soup = get_soup(url)

    data['Source URL'] = url

    data['Company'] = getsel(soup, 'h1', strip=True)

    # <address class="location-and-contact__address" data-v-3743af0a="" data-v-6baa5d14=""><strong data-v-3743af0a="" data-v-6baa5d14="">GRITEC AG</strong> <div data-v-3743af0a="" data-v-6baa5d14=""><div data-v-3743af0a="" data-v-6baa5d14="">Trutwisstrasse 9</div> <div data-v-3743af0a="" data-v-6baa5d14="">CH-7214 Grüsch</div></div> <!-- --></address>
    addr_tag = soup.find('address')

    # adr = {}
    tmp_company = addr_tag.find('strong').text

    # strasse_tag, plzland_tag = addr_tag.find('div').find_all('div')
    # Trutwisstrasse 9
    # CH-7214 Grüsch

    # data['Street'] = strasse_tag.text
    # adr = re_groups(plzland_tag.text, '^(.{1,3})-(\d+) (.+)$', ['adr_full', 'Country_Short', 'Zip Code', 'City'])

    # adr['adr_full'] = f"{data.get('Street')}, {adr.get('adr_full')}"


    # Hetmanekgasse 15, AT-1230 Wien
    adr_full = getsel(soup, 'div.business-card__address')
    # #data['adr_full'] = adr_full.strip()
    adr_full = adr_full.strip()

    adr = re_groups(adr_full, '^(.+), (.{1,3})-(\d+) (.+)$', ['adr_full', 'Street', 'Country_Short', 'Zip Code', 'City'])

    data = {**data, **adr}

    data['Country'] = map(data['Country_Short'], map_country)

    # m = re.match('^(.+), (.{2})-(\d{4}) (.+)$', data['adr_full'])
    # if m == None:
    #     data['plz'] = ''
    #     data['ort'] = ''
    #     data['strasse'] = ''
    # else:     
    #     data['land'] = m.group(2)   
    #     data['plz'] = m.group(3)
    #     data['ort'] = m.group(4)
    #     data['strasse'] = m.group(1)


    tel_full = getsel(soup, '.phone-button')
    # 'Telefonnummer anzeigen : +43 1 5955110\n  '

    telx = re_groups(tel_full, '^(.+) \: (.+)', ['//tel_full', '//dummy', 'Phone'])

    data = {**data, **telx}

    # m = re.match('^(.+) \: (.+)', tel_full)
    # data['tel'] = m.group(2).strip()

    #data['tel'] = getsel(soup, '.phone-button__text')
    data['Email'] = getsel(soup, 'a#location-and-contact__email span')
    # data['Website'] = getsel(soup, '#location-and-contact__website', strip=True) ##location-and-contact__website
    data['Website'] = getsel(soup, '#location-and-contact__website', attr='href') ##location-and-contact__website

    data['No. of Employees'] = '?'

    for x in mitarbeiter.keys():
        if x in str(soup):
            data['No. of Employees'] = str(mitarbeiter[x])
            break
    
    descr = getsel(soup, 'p.company-summary__text')
    descr = descr.strip()
    data['Description'] = descr


    #data['json'] = getsel(soup, 'script[data-n-head="ssr"]', strip=True)

    #data[''] = getsel(soup, 'h1', strip=True)

    if doprint:
        print(data)

    return data



def page(url:str, limit:bool=None):
    soup = get_soup(url)

    cnt_full = getsel(soup, 'a.search-tabs-supplier-link', strip=True)

    idx = -1

    for x in soup.find_all('a', {'class':'company-title-link'}): #'company-link'
        idx += 1

        href = x.get('href')
        if not href:
            continue
        
        if not 'firma' in href:
            continue

        if limit != None and idx >= limit:
            break

        url_detail = f"https://wlw.at{href}"
        
        data = detail(url_detail)

        #print(f"{data['firmenname']}:\n")
        #print(data)
        yield data


def full(fname:str, searchoptions:dict, page_from:int=None, page_to:int=None, page_limit:int=None, static_values:dict={}, filterd:dict={}, csv_sep:str=';', csv_nl:str='\n'):
    #kategorie:str=None, searchquery:str=None,

    if not static_values:
        static_values = {}

    if not filterd:
        filterd = {}
        

    # url_list_base = 'https://www.wlw.at/de/suche/personalrekrutierung/wien/page/2'
    if 'kategorie' in searchoptions.keys():
        topic = searchoptions['kategorie']

        if 'ort' in  searchoptions.keys():
            ort = searchoptions['ort']
            url_list_base = f"https://www.wlw.at/de/suche/{searchoptions['kategorie']}/{searchoptions['ort']}/page/"
        else:
            ort = None
            url_list_base = f"https://www.wlw.at/de/suche/{searchoptions['kategorie']}/page/"

        if 'searchquery' in searchoptions.keys():
            searchquery = searchoptions['searchquery']
        else:
            searchquery = ''

    
    # https://www.wlw.at/de/suche/page/2?q=personaldienstleister
    elif 'searchterm' in searchoptions.keys():
        topic = searchoptions['searchterm']
        searchquery = 'q=' + topic
        url_list_base = 'https://www.wlw.at/de/suche/page/'
    elif 'searchquery' in searchoptions.keys():
        topic = re_groups(searchoptions['searchquery'], '^(.*)q=(.+)', ['//sq_full', '//dummy', 'topic'], single=True)
        searchquery = searchoptions['searchquery']
        url_list_base = 'https://www.wlw.at/de/suche/page/'

    else:
        print('?????????????????')


    

    # https://www.wlw.at/de/suche/page/2?employeeCounts=50-99&q=personaldienstleister
    #url_list_base = 'https://www.wlw.at/de/suche/personalrekrutierung/wien/page/2'

    url = f"{url_list_base}{1}?{searchquery}"
    print(f"base-url: {url}")

    soup = get_soup(url)
    cnt_full = getsel(soup, 'a.search-tabs-supplier-link', strip=True)
    cnt = re_groups(cnt_full, '^(\d+) Anbieter$', ['//dummy_full', 'anbieter:int'], single=True)
    p_max = round(cnt / 30) + 1

    print(f"cnt: {cnt} -> p_max: {p_max}")

    if not page_from:
        page_from = 1
    elif page_from > p_max:
        page_from = p_max
    
    if not page_to:
        page_to = p_max
    elif page_to > p_max:
        page_to = p_max
    
    if not fname:
        fname = f"wlw_{topic}_{page_from:02d}-{page_to:02d}.csv"

    print(f"Writing to {fname}\n")

    first_line = True
    
    with open(os.path.join(__location_file__, fname), 'w+', buffering=1) as csv_out:
        for pnr in range(page_from, page_to+1):
            url = f"{url_list_base}{pnr}?{searchquery}"
            print(f"*** Scraping Page {pnr} ({page_from} bis {page_to}) ***")

            for data in page(url, limit=page_limit):

                try:

                    pinfo = {'page_nr': str(pnr)}
                    data = {**pinfo, **data, **static_values}

                    skip = False
                    for x in filterd.keys():
                        m = re.match(filterd[x], data[x])
                        
                        if not m:
                            skip = True
                            break

                    if skip:
                        print('!', end='')
                        continue
                    else:    
                        print('.', end='')

                    for k in data.keys():
                        data[k] = esc(data[k])


                    if first_line:
                        first_line = False
                        csv_out.write(csv_sep.join(data.keys()) + csv_nl)

                    csv_out.write(csv_sep.join(data.values()) + csv_nl)
                except Exception as e:
                    print('X')
                    print(traceback.format_exc())
            print()


# def liste(url):
#     soup = get_soup(url)

#     cnt_full = getsel(soup, 'a.search-tabs-supplier-link', strip=True)

#     #
#     cnt = re_groups(cnt_full, '^(\d+) Anbieter$', ['//dummy_full', 'anbieter:float'], single=True)
#     #383 Anbieter
#     print(cnt)

#     for x in soup.find_all('a', {'class':'company-link'}):

#         href = x.get('href')
#         if not href:
#             continue
        
#         if 'firma' in href:
#             print(href)






if __name__ == '__main__':

    # static_values = {'feldname': 'feldwert', 'feldname2': 'feldwert2' }
    static_values = {
        'Last Name': 'DummyXXXXX',
        'Formal/Informal': 'Formal (Sie)',
        'Lead Source': 'Cold Calling',
        'Lead Status': '00a Cold Lead',
        'Contact-Type': 'Kunde',
        'Touchpoints': '0000-00-00 Cold Call',
        'Preferred Communication Channel': 'E-Mail',
        'Buying Temperature': 'Not contacted', 
        'Product Interests': 'EazyStock',
        'Industry': 'Wholesale & Distribution',
    }

    #'personalrekrutierung',
        #'ort': 'wien',
    # searchoptions = {
    #     'kategorie': 'personal-vermittlung',
    #     'searchquery': 'employeeCounts=10-19_100-199_20-49_50-99&locationCity=Wien,%20Österreich&locationRadius=125km'
    # }

# https://www.herold.at/gelbe-seiten/branchen-az/a/
    searchoptions = {
        #'kategorie': 'beratung',
        # 'searchquery': 'q=beratung&employeeCounts=10-19_20-49_50-99&locationCity=Wien,%20Österreich&locationRadius=50km'
        # 'searchquery': 'q=beratung'
        # 'searchquery': 'employeeCounts=10-49_50-199_200%2B&q=filtertechnik&supplierTypes=Großhändler' #suche?
        # 'searchquery': 'employeeCounts=10-49_50-199_200%2B&q=ersatzteile&supplierTypes=Großhändler' #suche?
        # 'searchquery': 'employeeCounts=10-49_50-199_200%2B&q=sanitärbedarf&supplierTypes=Großhändler' #suche?
        'searchquery': 'employeeCounts=10-49_50-199_200%2B&q=befestigungstechnik&supplierTypes=Großhändler' #suche?
    }

    # searchoptions = {
    #     'kategorie': 'lohn-und-gehaltsabrechnung',
    #     'searchquery': 'employeeCounts=10-19_100-199_20-49_50-99&locationCity=Wien,%20Österreich&locationRadius=125km'
    # }

    #full('personaldienstleister')
    #full(None, 'employeeCounts=50-99&q=personaldienstleister', page_from=1, page_to=2, page_limit=3, static_values=static_values, filterd={'Country_Short': '^AT$'})
    # full(None, searchoptions=searchoptions, page_from=None, page_to=None, page_limit=None, static_values=static_values, filterd={'Country_Short': '^AT$'})
    full(None, searchoptions=searchoptions, page_from=None, page_to=None, page_limit=None, static_values=static_values, filterd=None)
    #liste('https://www.wlw.at/de/suche?employeeCounts=50-99&q=personaldienstleister')
    #      https://www.wlw.at/de/suche/page/2?employeeCounts=50-99&q=personaldienstleister
    #
    # quit()

    #print('\n\n\n')
    #detail('https://www.wlw.at/de/firma/roesler-oberflaechentechnik-gmbh-583217')
    #detail('https://www.wlw.at/de/firma/jl-personalmanagement-gmbh-1043587')
    #print('\n\n\n')