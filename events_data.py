from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import time
import csv

try:
    options = webdriver.ChromeOptions()

    options.add_argument(f'user-agent={UserAgent().random}')
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.binary_location = 'C:\Program Files\Google\Chrome Beta\Application\chrome.exe' # Chrome location

    path = r'C:\Users\name\Documents\GitHub\chromedriver.exe' # driver location
    service = Service(path)
    driver = webdriver.Chrome(service=service, options=options)

    url = 'https://www.sae.org/attend'

    driver.get(url)
    time.sleep(3)

    while True:
        try:
            but = driver.find_element(By.XPATH, "//button[@class='nx-button nx-button-more']")
            driver.execute_script("arguments[0].scrollIntoView();", but)
            but.click()
            time.sleep(2)
        except NoSuchElementException:
            break

    with open('data.tsv', 'wt', encoding='utf-8') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(['Title', 'Category', 'Data Range', 'Location', 'Link', 'Description', 'Hotel Information'])

    data_tsv = []
    count = 1

    try:
        event_objs = driver.find_elements(By.CLASS_NAME, 'nx-table-list-tbody')[0].find_elements(By.CLASS_NAME, 'nx-table-list-row')
        for event_obj in event_objs:
            title = event_obj.find_elements(By.TAG_NAME, 'div')[0].text
            category = event_obj.find_elements(By.TAG_NAME, 'div')[2].text
            data_range = event_obj.find_elements(By.TAG_NAME, 'div')[3].text
            location = event_obj.find_elements(By.TAG_NAME, 'div')[5].text

            description = None
            hotels = None
            try:
                link = event_obj.find_elements(By.TAG_NAME, 'div')[7].find_element(By.TAG_NAME, 'a').get_attribute('href')
                if link[0] == '/':
                    link = url + link

                try:
                    r = requests.get(url=link)

                    soup = BeautifulSoup(r.text, 'lxml')
                    description = soup.find('article', class_='has-edit-button').text.strip()
                    for i in description:
                        description = description.replace('  ', ' ')

                    r = requests.get(url=link + '/hotel-travel')

                    soup = BeautifulSoup(r.text, 'lxml')
                    all_hotels = soup.find_all(class_='nx-blocked-row')

                    hotels = []
                    for hotel in all_hotels[1:-1]:
                        try:
                            hotel_title = hotel.find_all('div')[-1].find(class_='has-edit-button').find('h2').text.strip()
                        except:
                            hotel_title = None
                        try:
                            hotel_address = hotel.find_all('div')[-1].find(class_='has-edit-button').find_all('p')[
                                1].text.strip()
                        except:
                            hotel_address = None
                        try:
                            hotel_link = hotel.find_all('div')[-1].find(class_='has-edit-button').find_all('p')[1].find(
                                'a').get('href').strip()
                        except:
                            hotel_link = None

                        hotels.append([hotel_title, hotel_address, hotel_link])
                except:
                    print('')

            except:
                link = None

            data_tsv.append([title, category, data_range, location, link, description, hotels])

            print(f'{count}. {title} | {category} | {data_range} | {location} | {link} | {description} | {hotels}')
            count += 1

        with open('data.tsv', 'at', encoding='utf-8') as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t')
            tsv_writer.writerows(data_tsv)

    except Exception as ex:
        print(ex)

except Exception as ex:
    print(ex)

finally:
    driver.stop_client()
    driver.close()
    driver.quit()