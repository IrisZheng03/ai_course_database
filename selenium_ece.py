from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
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

# Wait for search results to load
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.gs-title a.gs-title')))

''' bug from here on'''
# Extract all relevant links
links = driver.find_elements(By.CSS_SELECTOR, 'div.gs-title a.gs-title')
google_redirect_links = [link.get_attribute('href') for link in links if link.get_attribute('href') and 'areas-of-study' in link.get_attribute('href')]

# Function to parse Google redirect URLs and extract the actual URL
def extract_actual_url(google_url):
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(google_url)
    query_params = parse_qs(parsed_url.query)
    actual_url = query_params.get('q', [None])[0]
    return actual_url

# Process each Google redirect URL to get the actual URLs
actual_urls = [extract_actual_url(url) for url in google_redirect_links if url]

'''to here '''

# Data to be saved in CSV
data_to_save = []

# Iterate through each actual URL and extract required information
for url in actual_urls:
    # Navigate to the URL
    driver.get(url)

    # Wait for the required element to load and extract the content
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.hero__heading')))
    h1_content = driver.find_element(By.CSS_SELECTOR, 'h1.hero__heading').text
    page_url = driver.current_url

    # Add the extracted data to the list
    data_to_save.append([h1_content, page_url])
    
    # Small delay to avoid rapid-fire requests
    time.sleep(1)

# ... [rest of the code for saving data and closing the driver] ...

# Close the driver
driver.quit()

# Write data to CSV file
with open('extracted_ece_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['H1 Content', 'URL'])  # CSV Headers
    for row in data_to_save:
        writer.writerow(row)
