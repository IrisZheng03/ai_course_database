from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import csv
import time

# Set Chrome options for incognito mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")

# Initialize the Chrome driver with the options
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the website
driver.get('https://ece.emory.edu/')

# Wait and click the search icon
wait = WebDriverWait(driver, 10)
search_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.navbar__search-toggle.icon-magnifier')))
search_icon.click()

# Wait for the search input page to load
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.gsc-input')))

# Find the search input element and input the keyword
search_input = driver.find_element(By.CSS_SELECTOR, 'input.gsc-input')
search_input.send_keys('artificial intelligence')
search_input.send_keys(Keys.ENTER)

# Data to be saved in CSV
data_to_save = []

current_page = 1
max_pages = 5  # You can adjust this to the number of pages you want to process

while current_page <= max_pages:
    # Wait for search results to load
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs-title a.gs-title')))

    # Extract all relevant links
    links = driver.find_elements(By.CSS_SELECTOR, 'div.gs-title a.gs-title')
    google_redirect_links = set(link.get_attribute('href')
                                for link in links
                                if link.get_attribute('href') and 'areas-of-study' in link.get_attribute('href'))

    for url in google_redirect_links:
        try:
            # Navigate to the URL
            driver.get(url)

            # Wait for the required element to load and extract the content
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.hero__heading')))
            h1_content = driver.find_element(By.CSS_SELECTOR, 'h1.hero__heading').text
            page_url = driver.current_url

            # Add the extracted data to the list
            data_to_save.append([h1_content, page_url])
        except TimeoutException:
            print(f"Element 'h1.hero__heading' not found on {url}. Continuing to next URL.")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}. Continuing to next URL.")
        finally:
            # Small delay to avoid rapid-fire requests
            time.sleep(1)

        '''still troubleshooting how to navigate the next page'''
    try:
        # Wait for the pagination bar to be fully loaded
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gsc-cursor-box')))
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, "div.gsc-cursor-page")

        if current_page < len(pagination_elements):
            # Use JavaScript to click on the next page element
            next_page_element = pagination_elements[current_page]  # next page is current_page index in list
            driver.execute_script("arguments[0].click();", next_page_element)

            current_page += 1
            print(f"Moving to page {current_page}")
            time.sleep(2)  # Wait for the next page to load
        else:
            print("No more pages or reached the maximum page limit.")
            break
    except NoSuchElementException:
        print("Failed to find the next page element.")
        break

# Write data to CSV file
with open('extracted_ece_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['H1 Content', 'URL'])  # CSV Headers
    for row in data_to_save:
        writer.writerow(row)

# Close the driver
driver.quit()
