import json
import pathlib
import sys
import time
import traceback
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
config = {}

label_mapping = [
    {'text': 'Great news', 'label': 'serviceable'},
    {'text': 'Your building can get Starry', 'label': 'petition'},
    {'text': 'We’re on our way', 'label': 'waitlist'},
    {'text': 'Enter your info below', 'label': 'noservice'},
]


def init_config(config_file='{}/config.json'.format(CURRENT_DIR)):
    """
    Read configuration file from current directory or from the given path
    :return:
    """
    print('initializing config')
    with open(config_file, encoding='utf-8') as json_file:
        data = json.load(json_file)

    config.update(data)

    config['headless'] = True if config.get('headless_mode', None) == 'Y' else False


def init_webdriver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--ignore_ssl")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--log-level=3")

    headless = config.get('headless', True)
    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(executable_path=config.get('chromedriver_path'), options=options)

    print('got driver')
    return driver


def save_to_excel(final_result):
    """
    save result to csv file
    :param final_result: data to be saved to excel file
    :return: None
    """
    print('saving to csv file')
    df = pd.DataFrame(final_result)

    # df.drop(columns=['html_text'], inplace=True)
    # save to csv file
    csv_file_name = config.get('output_csv_file_location')
    df.to_csv(csv_file_name, encoding='utf-8', index=False)

    print('saved to : {}'.format(csv_file_name))


def process_address(driver, address: str) -> list:
    """
    serarch for address via chrome driver
    :param driver: chrome driver
    :param address: street address
    :return: result list
    """
    # open page
    driver.get(config.get('web_url'))
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'check-availability-input')))

    # send input data
    driver.find_element_by_id('check-availability-input').send_keys(address)
    time.sleep(1)

    # Find if its possible to wait on any element
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@class='results']/li[1]")))

    time.sleep(1)
    driver.find_element_by_xpath("//*[@class='results']/li[1]").click()

    # time.sleep(5)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'h3')))
    # time.sleep(2)

    # get header text
    _label_mapping = config.get('label_mapping', label_mapping)
    counter = 0
    while True:
        if counter > 100:
            break
        try:
            header_text = driver.find_element_by_tag_name('h3').text.strip()
            _tmp = [True for row in _label_mapping if str(row['text']).lower() in str(header_text).lower()]
            if _tmp:
                break
        except:
            pass
        time.sleep(1)
        counter += 1

    print(header_text)

    # parse html text using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')
    html_page_source = soup.text

    # collect status for the given address
    result = [{'address': address, 'label': row['label']} for row in _label_mapping
              if str(row['text']).lower() in str(header_text).lower()]

    # print(result)

    # write html text to file
    with open('{}/{}.text'.format(config.get('output_text_file_path'), address), mode='a',
              encoding='utf-8') as file:
        file.write(html_page_source)

    return result[0] if result else None


def starry_scrape(driver) -> pd.DataFrame:
    """
    :param driver: web driver
    :return:
    """
    final_result = []
    with open(config.get('input_address_text_file'), 'r') as file:
        address_list = [str(txt_file).strip() for txt_file in file.readlines()]
        # print('address_list: {}\n'.format(address_list))
        print('total address: {}'.format(len(address_list)))

    total_count = len(address_list)
    for index, address in enumerate(address_list):
        print('Processing {} of {}, address: {}'.format(index + 1, total_count, address))
        try:
            processed_res = process_address(driver, address)
            final_result.append(processed_res)
            # wait b/w each address scrape
            time.sleep(int(config.get('seconds_to_wait_between_scrape', 5)))
        except:
            final_result.append({'address': address, 'label': None})
            print('Error scrapping for address: {}'.format(address))
            traceback.print_exc()
            # wait for 10sec when errored
            time.sleep(10)

    print('result count : {}'.format(len(final_result)))
    df = pd.DataFrame(final_result)

    return df


def main_scrape(config_file):
    """
    main scrapper method
    :return:
    """
    start_time = datetime.now()
    print('in main scraper')
    init_config(config_file)
    status_flag = False
    try:
        for counter in range(0, config['retry_count_when_failed']):
            print('Trial: {}'.format(counter + 1))
            try:
                # initialize driver
                driver = init_webdriver()

                # scrape data
                df = starry_scrape(driver)
                print(df.to_string())
                # save to excel file
                save_to_excel(df)
                status_flag = True
                break
            except Exception as ex:
                print('Exception block')
                print(traceback.format_exc())
            finally:
                # close web driver session
                driver.close()

            # wait time b/w each failed attempt
            time.sleep(10)

        print('end of script')
    finally:
        print('cleanup any resources')

    end_time = datetime.now()
    diff = relativedelta(end_time, start_time)
    print('Execution time: {} hours {} minutes {} seconds'.format(diff.hour, diff.minutes, diff.seconds))

    return status_flag


if __name__ == '__main__':
    input_args = sys.argv[1:]
    print(input_args)
    if not input_args:
        print('Input configuration is missing. Please provide config.json path as argument')

    success = main_scrape(input_args[0])
