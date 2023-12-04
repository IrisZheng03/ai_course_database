from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import csv
import time
import os

def process_url(url, driver, wait):
    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.hero__heading')))
        h1_content = driver.find_element(By.CSS_SELECTOR, 'h1.hero__heading').text
        return [h1_content, url]
    except TimeoutException:
        print(f"Unable to find required elements on {url}.")
        return None
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}.")
        return None

def perform_search(query, driver, wait):
    try:
        driver.get('https://ece.emory.edu/')
        search_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar__search-toggle.icon-magnifier')))
        search_icon.click()
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.gsc-input')))
        search_input.clear()
        search_input.send_keys(query)
        search_input.send_keys(Keys.ENTER)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs-title a.gs-title')))
    except TimeoutException:
        print("Timeout while performing search.")
    except Exception as e:
        print(f"Unexpected error during search: {e}")


# Initialize WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

data_to_save = []
current_page = 1
max_pages = 3


def get_search_results():
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs-title a.gs-title')))
    links = driver.find_elements(By.CSS_SELECTOR, 'div.gs-title a.gs-title')
    return set(link.get_attribute('href') for link in links if link.get_attribute('href') and 'areas-of-study' in link.get_attribute('href'))

perform_search('artificial intelligence', driver, wait)  # Perform initial search

while current_page <= max_pages:
    google_redirect_links = get_search_results()

    for url in google_redirect_links:
        data = process_url(url, driver, wait)
        if data:
            data_to_save.append(data)

    # Return to search results page for pagination
    if current_page < max_pages:
        perform_search('artificial intelligence', driver, wait)  # Reload the search page
        pagination_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.gsc-cursor-page")))
        try:
            pagination_element = pagination_elements[current_page]
            driver.execute_script("arguments[0].scrollIntoView(true);", pagination_element)
            driver.execute_script("arguments[0].click();", pagination_element)
            time.sleep(2) 
        except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
            print(f"Error during pagination: {e}")

    current_page += 1


script_directory = os.path.dirname(os.path.realpath(__file__))
data_csv_directory = os.path.join(script_directory, "data_csv")
if not os.path.exists(data_csv_directory):
    os.makedirs(data_csv_directory)
csv_file_path = os.path.join(data_csv_directory, 'extracted_ece_data.csv')

with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['H1 Content', 'URL'])
    for row in data_to_save:
        writer.writerow(row)

driver.quit()
