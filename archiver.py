# import modules
import os
from datetime import datetime
import pytz
from github import Github
import requests
import tempfile
from selenium import webdriver # requires ChromeDriver and Chromium/Chrome
from selenium.webdriver.chrome.options import Options

# access repo
token = os.environ['GH_TOKEN']
g = Github(token)
repo = g.get_repo('jeanpaulrsoucy/covid-19-canada-gov-data')

# commit string
t = datetime.now(pytz.timezone('America/Toronto'))
commit = 'Nightly update: ' + str(t.date())

# create temporary directory
tmpdir = tempfile.TemporaryDirectory()

# setup webdriver
options = Options()
options.binary_location = os.environ['GOOGLE_CHROME_BIN']
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
prefs = {'download.default_directory' : str(tmpdir)}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(executable_path=os.environ['CHROMEDRIVER_PATH'], options=options)

# function: download and commit file
def dl_file(url, path, file, commit, user=False, ext='.csv'):
        if user == True:
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
                data = requests.get(url, headers=headers).content
        else:
                data = requests.get(url).content
        name = file + '_' + datetime.now(pytz.timezone('America/Toronto')).strftime('%Y-%m-%d_%H-%M')
        repo.create_file(path + name + ext, commit + ' (' + path + ')', data)

# function: download and commit csv from AB - "COVID-19 Alberta statistics"
def dl_ab_cases(url, path, file, commit, ext='.csv'):

        ## click to export
        driver.get(url)
        elements = driver.find_elements_by_tag_name("li")
        for element in elements:
                if element.text == 'Data export':
                        element.click()
        elements = driver.find_elements_by_tag_name("button")
        for element in elements:
                if element.text == 'CSV':
                        element.click()

        ## commit file
        with open(os.path.join(str(tmpdir), file + ext), 'r') as f:
                data = f.read()
        name = file + '_' + datetime.now(pytz.timezone('America/Toronto')).strftime('%Y-%m-%d_%H-%M')
        repo.create_file(path + name + ext, commit + ' (' + path + ')', data)

# function: download and commit csv from AB - "COVID-19 relaunch status map"
def dl_ab_relaunch(url, path, file, commit, ext='.csv'):
        
        ## click to export
        driver.get(url)
        elements = driver.find_elements_by_tag_name("button")
        for element in elements:
                if element.text == 'CSV':
                        element.click()

        ## commit file
        with open(os.path.join(str(tmpdir), file + ext), 'r') as f:
                data = f.read()
        name = file + '_' + datetime.now(pytz.timezone('America/Toronto')).strftime('%Y-%m-%d_%H-%M')
        repo.create_file(path + name + ext, commit + ' (' + path + ')', data)

# AB - COVID-19 Alberta statistics
dl_ab_cases('https://www.alberta.ca/stats/covid-19-alberta-statistics.htm',
            'ab/cases/',
            'covid19dataexport',
            commit)

# AB - COVID-19 relaunch status map
dl_ab_relaunch('https://www.alberta.ca/maps/covid-19-status-map.htm',
               'ab/active-cases-by-region/',
               'covid19dataexport-relaunch',
               commit)

# AB - COVID-19 in Alberta: Current cases by local geographic area (Edmonton)
dl_file('https://data.edmonton.ca/api/views/ix8f-s9xp/rows.csv?accessType=DOWNLOAD',
        'ab/edmonton-cases-by-area/',
        'COVID-19_in_Alberta__Current_cases_by_local_geographic_area',
        commit)

# BC - BC COVID-19 Data (Case data)
dl_file('http://www.bccdc.ca/Health-Info-Site/Documents/BCCDC_COVID19_Dashboard_Case_Details.csv',
        'bc/case-data/',
        'BCCDC_COVID19_Dashboard_Case_Details',
        commit)

# BC - BC COVID-19 Data (Laboratory data)
dl_file('http://www.bccdc.ca/Health-Info-Site/Documents/BCCDC_COVID19_Dashboard_Lab_Information.csv',
        'bc/laboratory-data/',
        'BCCDC_COVID19_Dashboard_Lab_Information',
        commit)

# CAN - Coronavirus disease 2019 (COVID-19): Epidemiology update
dl_file('https://health-infobase.canada.ca/src/data/covidLive/covid19.csv',
        'can/epidemiology-update/',
        'covid19',
        commit)

# ON - Confirmed positive cases of COVID19 in Ontario
dl_file('https://data.ontario.ca/dataset/f4112442-bdc8-45d2-be3c-12efae72fb27/resource/455fd63b-603d-4608-8216-7d8647f43350/download/conposcovidloc.csv',
        'on/confirmed-positive-cases/',
        'conposcovidloc',
        commit)

# ON - Status of COVID-19 cases in Ontario
dl_file('https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv',
        'on/status-of-cases/',
        'covidtesting',
        commit)

# ON - City of Toronto COVID-19 Summary
dl_file('https://docs.google.com/spreadsheets/d/1euhrML0rkV_hHF1thiA0G5vSSeZCqxHY/export?format=xlsx&id=1euhrML0rkV_hHF1thiA0G5vSSeZCqxHY',
        'on/toronto-covid-summary/',
        'CityofToronto_COVID-19_Data',
        commit,
        ext='.xlsx')

# ON - COVID-19 Cases in Toronto
# run only on Wednesdays
if t.weekday() == 2:
        dl_file('https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=csv',
                'on/toronto-cases/',
                'COVID19_cases',
                commit)

# QC - COVID-19 data
dl_file('https://www.inspq.qc.ca/sites/default/files/covid/donnees/combine.csv',
        'qc/covid-data/',
        'combine',
        commit,
        user=True)

# QC - COVID-19 data (charts)
dl_file('https://www.inspq.qc.ca/sites/default/files/covid/donnees/combine2.csv',
        'qc/covid-data-charts/',
        'combine2',
        commit,
        user=True)

# QC - Deaths by RSS (health region) and living environment
dl_file('https://www.inspq.qc.ca/sites/default/files/covid/donnees/tableau-rpa.csv',
        'qc/deaths-by-rss-and-living-environment/',
        'tableau-rpa',
        commit,
        user=True)

# QC - Cases by RSS (health region) and RLS (local service network)
dl_file('https://www.inspq.qc.ca/sites/default/files/covid/donnees/tableau-rls.csv',
        'qc/cases-by-rss-and-rls/',
        'tableau-rls',
        commit,
        user=True)

# QC - Montréal cases and deaths by CIUSSS (integrated health and social services centres)
dl_file('https://santemontreal.qc.ca/fileadmin/fichiers/Campagnes/coronavirus/situation-montreal/ciusss.csv',
        'qc/montreal-cases-and-deaths-by-ciusss/',
        'ciusss',
        commit,
        user=True)

# QC - Montréal cases by area
dl_file('https://santemontreal.qc.ca/fileadmin/fichiers/Campagnes/coronavirus/situation-montreal/municipal.csv',
        'qc/montreal-cases-by-area/',
        'municipal',
        commit,
        user=True)

# QC - Montréal cases and deaths by age group
dl_file('https://santemontreal.qc.ca/fileadmin/fichiers/Campagnes/coronavirus/situation-montreal/grage.csv',
        'qc/montreal-cases-and-deaths-by-age-group/',
        'grage',
        commit,
        user=True)

# QC - Montréal cases and deaths by sex
dl_file('https://santemontreal.qc.ca/fileadmin/fichiers/Campagnes/coronavirus/situation-montreal/sexe.csv',
        'qc/montreal-cases-and-deaths-by-sex/',
        'sexe',
        commit,
        user=True)

# QC - Montréal epidemic curve
dl_file('https://santemontreal.qc.ca/fileadmin/fichiers/Campagnes/coronavirus/situation-montreal/courbe.csv',
        'qc/montreal-epidemic-curve/',
        'courbe',
        commit,
        user=True)