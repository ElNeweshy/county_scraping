import time
from selenium import webdriver
import pandas as pd
from bs4 import BeautifulSoup
from copy import deepcopy
import numpy as np
import ast


def read_inputs(csv_file):
    data = pd.read_csv(csv_file, header=None)
    from_date = str(data.iloc[0][1].replace('.', '-'))
    to_date = str(data.iloc[1][1].replace('.', '-'))
    return (from_date, to_date)


def get_number_of_pages(from_date, to_date):
    driver = webdriver.Chrome('chromedriver')
    driver.get(
        'https://okcountyrecords.com/results/recorded-start={}:recorded-end={}/page-1'.format(from_date, to_date))
    time.sleep(1)
    number_of_results_row = driver.find_element_by_xpath('//*[@id="result-stats"]').text
    number_of_results = eval(number_of_results_row.split('results')[0][:-1].replace(',', ''))

    number_of_pages = int(number_of_results / 15) + 1

    print('Number of search results is:', number_of_results)
    print('Number of pages is:', number_of_pages)

    driver.close()

    return number_of_pages


def get_page_link(from_date, to_date, page_number):
    return ('https://okcountyrecords.com/results/recorded-start={}:recorded-end={}/page-{}'.format(from_date, to_date,
                                                                                                   page_number))


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
            'Legal_Description': '',
            }

    County = BeautifulSoup(str(tds[0]), 'html.parser').text
    dict.update({'County': County})

    try:
        Instrument = BeautifulSoup(str(tds[1]), 'html.parser').text.replace('\n', '')
        dict.update({'Instrument': Instrument})
    except:
        pass

    try:
        Type = BeautifulSoup(str(tds[2]), 'html.parser').find('a').text
        dict.update({'Type': Type})
    except:
        pass

    Book = BeautifulSoup(str(tds[3]), 'html.parser').text
    dict.update({'Book': Book})

    Recorded = BeautifulSoup(str(tds[7]), 'html.parser').text.replace('\n', '')
    dict.update({'Recorded': Recorded})

    People = BeautifulSoup(str(tds[5]), 'html.parser').text
    if '\n' in People:
        People = People[1:]
        People = People.replace('\n', '***')
    dict.update({'People': People})

    if Instrument != '':

        # Scrap secondary page
        driver.get('https://okcountyrecords.com/detail/' + County + '/' + Instrument)

        Filing_Fees = driver.find_element_by_xpath('//*[@id="detail-fees"]/table/tbody/tr[1]/td').text
        dict.update({'Filing_Fees': Filing_Fees})

        Mortgage_amount = driver.find_element_by_xpath('//*[@id="detail-fees"]/table/tbody/tr[2]/td').text
        dict.update({'Mortgage_amount': Mortgage_amount})

        Document_stamps = driver.find_element_by_xpath('//*[@id="detail-fees"]/table/tbody/tr[3]/td').text
        dict.update({'Document_stamps': Document_stamps})

        try:
            Grantor = driver.find_element_by_xpath('//*[@id="detail-people"]/ul/li[1]/ul').text
            if 'Search\n' in Grantor:
                Grantor = Grantor[7:]
                Grantor = Grantor.replace('\nSearch\n', '***')
            dict.update({'Grantor': Grantor})
        except:
            pass

        try:
            Grantee = driver.find_element_by_xpath('//*[@id="detail-people"]/ul/li[2]/ul').text
            if 'Search\n' in Grantee:
                Grantee = Grantee[7:]
                Grantee = Grantee.replace('\nSearch\n', '***')
            dict.update({'Grantee': Grantee})
        except:
            pass

        try:
            Legal_Description = driver.find_element_by_xpath('//*[@id="detail-legals"]/ul').text
            if 'Search\n' in Legal_Description:
                Legal_Description = Legal_Description[7:]
                Legal_Description = Legal_Description.replace('\nSearch\n', '***')
            dict.update({'Legal_Description': Legal_Description})
        except:
            pass

        Recorded_on = driver.find_element_by_xpath('//*[@id="detail-fees"]/table/tbody/tr[4]/td').text
        dict.update({'Recorded_on': Recorded_on})

        try:
            Instrument_date = driver.find_element_by_xpath('//*[@id="detail-fees"]/table/tbody/tr[5]/td').text
            dict.update({'Instrument_date': Instrument_date})
        except:
            pass

        Returned_on = driver.find_element_by_xpath('//*[@id="secondary-details"]/table/tbody/tr[2]/td').text
        dict.update({'Returned_on': Returned_on})

        Page = driver.find_element_by_xpath('//*[@id="primary-details"]/table/tbody/tr[2]/td').text
        dict.update({'Page': Page})

    driver.close()

    return dict


def create_csv_form_text_file(text_file, output_file_name):
    columns = ['Type',
               'Book',
               'Page',
               'County',
               'Instrument',
               'Recorded',
               'Filing_Fees',
               'Mortgage_amount',
               'Document_stamps',
               'Recorded_on',
               'Instrument_date',
               'Returned_on',
               'Grantor',
               'Grantee',
               'Legal_Description'
               ]

    dicts = open(text_file, 'r').readlines()

    df = pd.DataFrame(columns=columns)
    for dict in dicts:
        dict = ast.literal_eval(dict)
        df = df.append(dict, ignore_index=True)

    df.index = np.arange(1, len(df) + 1)
    df.to_csv(output_file_name)


if __name__ == "__main__":

    inputs = read_inputs("inputs.csv")
    number_of_pages = get_number_of_pages(inputs[0], inputs[1])

    with open('output.txt', 'w') as output_text_file:
        pass

    # dicts = []
    for page_number in range(number_of_pages):
        print('Page:', page_number + 1)
        page_link = get_page_link(inputs[0], inputs[1], page_number + 1)
        print('Page link: ', page_link)

        for row_index in range(15):
            print('Row:', row_index + 1)
            try:
                dict = extract_data_from_page(page_link, row_index + 1)
            except:
                continue

            print(dict)

            with open('output.txt', 'a') as output_text_file:
                output_text_file.write(str(dict))
                output_text_file.write('\n')
                # dicts.append(deepcopy(dict))
                create_csv_form_text_file('output.txt', 'output.csv')
