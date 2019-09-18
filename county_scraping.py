import time
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup


def read_inputs(csv_file):
    data = pd.read_csv(csv_file, header=None)
    from_date = str(data.iloc[0][1].replace('.', '-'))
    to_date = str(data.iloc[1][1].replace('.', '-'))
    return (from_date, to_date)

def get_number_of_pages(from_date, to_date):
    driver = webdriver.Chrome('chromedriver')
    driver.get('https://okcountyrecords.com/results/recorded-start={}:recorded-end={}/page-1'.format(from_date, to_date))
    time.sleep(1)
    number_of_results_row = driver.find_element_by_xpath('//*[@id="result-stats"]').text
    number_of_results = eval(number_of_results_row.split('results')[0][:-1].replace(',', ''))

    number_of_pages = int(number_of_results / 15) + 1

    return number_of_pages


def get_page_link(from_date, to_date, page_number):
    return('https://okcountyrecords.com/results/recorded-start={}:recorded-end={}/page-{}'.format(from_date, to_date, page_number))

def extract_data_from_page(page_link, row_index):
    driver = webdriver.Chrome('chromedriver')
    driver.get(page_link)
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.find_all('tr')

    target_row = rows[row_index]
    parse_row = BeautifulSoup(str(target_row), 'html.parser')
    tds = parse_row.find_all('td')

    dict = {'Type': '',
            'Book': '',
            'Page': '',
            'County': '',
            'Instrument': '',
            'Recorded': '',
            'Filing_Fees': '',
            'Mortgage_amount': '',
            'Document_stamps': '',
            'Recorded_on': '',
            'Instrument_date': '',
            'Returned_on': '',
            'Grantor': '',
            'Grantee': '',
            'Legal Description': '',
            }

    County = BeautifulSoup(str(tds[0]), 'html.parser').text
    dict.update({'County': County})

    url_code = BeautifulSoup(str(tds[1]), 'html.parser').text

    Type = BeautifulSoup(str(tds[2]), 'html.parser').find('a').text
    dict.update({'Type': Type})

    Book = BeautifulSoup(str(tds[3]), 'html.parser').text
    dict.update({'Book': Book})

    Recorded_on = BeautifulSoup(str(tds[7]), 'html.parser').text.replace('\n', '')
    dict.update({'Recorded_on': Recorded_on})

    People = BeautifulSoup(str(tds[5]), 'html.parser').text.replace('\n', '')
    dict.update({'People': People})

    driver.get('https://okcountyrecords.com/detail/' + County + '/' + url_code)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    return dict


if __name__ == "__main__":

    inputs = read_inputs("inputs.csv")
    number_of_pages = get_number_of_pages(inputs[0], inputs[1])

    for page_number in range(number_of_pages):
        print('Page: ', page_number + 1)
        page_link = get_page_link(inputs[0], inputs[1], page_number + 1)
        print('Page link: ', page_link)
        for row_index in range(15):
            print('Row: ', row_index + 1)
            data = extract_data_from_page(page_link, row_index + 1)
            print(data)

