from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import csv
import time

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

# Set Chrome options for incognito mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

# Initialize the Chrome driver with the options
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

# Data to be saved in CSV
data_to_save = []
current_page = 1
max_pages = 5

'''
while current_page <= max_pages:
    perform_search('artificial intelligence', driver, wait)  # Corrected function call
    if current_page > 1:
        pagination_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.gsc-cursor-page")))
        # Get the specific pagination element for the current page
        pagination_element = pagination_elements[current_page - 1]

        # Scroll into view of the pagination element and then click using JavaScript
        driver.execute_script("arguments[0].scrollIntoView(true);", pagination_element)
        driver.execute_script("arguments[0].click();", pagination_element)

        # Wait for the page to load after pagination click
        # (You might need to adjust the wait condition based on the specific behavior of the site)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs-title a.gs-title')))


    # Fetch search result links
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs-title a.gs-title')))
    links = driver.find_elements(By.CSS_SELECTOR, 'div.gs-title a.gs-title')
    google_redirect_links = set(link.get_attribute('href') for link in links if link.get_attribute('href') and 'areas-of-study' in link.get_attribute('href'))

    for url in google_redirect_links:
        data = process_url(url, driver, wait)
        if data:
            data_to_save.append(data)

    current_page += 1

'''

# Perform the initial search
perform_search('artificial intelligence', driver, wait)

while current_page <= max_pages:
    # Wait for and fetch search result links
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs-title a.gs-title')))
    links = driver.find_elements(By.CSS_SELECTOR, 'div.gs-title a.gs-title')
    google_redirect_links = set(link.get_attribute('href') for link in links if link.get_attribute('href') and 'areas-of-study' in link.get_attribute('href'))

    for url in google_redirect_links:
        data = process_url(url, driver, wait)
        if data:
            data_to_save.append(data)

    # Handle pagination
    if current_page < max_pages:
        try:
            pagination_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.gsc-cursor-page")))
            if current_page < len(pagination_elements):
                next_page_element = pagination_elements[current_page]  # Index for next page
                next_page_element.click()
                current_page += 1
                print(f"Moved to page {current_page}")
                time.sleep(2)  # Adjust as needed
            else:
                print("No more pages or reached the maximum page limit.")
                break
        except TimeoutException: # it kept giving me time out exception, what to do with turning pages?? 
            print(f"Timeout occurred on page {current_page}.")
            break
        except Exception as e:
            print(f"An unexpected error occurred on pagination: {e}")
            break
    else:
        break



# Write data to CSV file
with open('extracted_ece_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['H1 Content', 'URL'])
    for row in data_to_save:
        writer.writerow(row)

# Close the driver
driver.quit()
