import time
import re
from copy import deepcopy
import ast
import os

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def read_inputs(csv_file):
    data = pd.read_csv(csv_file, header=None)

    from_date = data.iloc[0][1]
    to_date = data.iloc[1][1]

    return (from_date, to_date)


def search_website(from_date, to_date):
    driver = webdriver.Chrome('chromedriver')
    driver.get("")
    time.sleep(1)

    from_date_field = driver.find_element_by_xpath('//*[@id="search-recorded-start"]')
    to_date_field = driver.find_element_by_xpath('//*[@id="search-recorded-end"]')

    from_date_field.send_keys(from_date)
    to_date_field.send_keys(to_date)

    # submit
    # driver.find_element_by_xpath('//*[@id="advanced-search-form"]/div[2]/button/span').click()

    time.sleep(500)


if __name__ == "__main__":
    inputs = read_inputs("inputs.csv")
    search_website(inputs[0], inputs[1])
