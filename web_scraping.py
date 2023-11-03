from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def fetch_course_data(url, keywords, driver_path):
    # Setting up the Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Running Chrome in headless mode

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        # Input the keyword in the search box and hit enter
        search_box = driver.find_element(By.NAME, "search")  # Adjust the name attribute as needed
        search_box.send_keys("artificial intelligence")
        search_box.send_keys(Keys.RETURN)

        # Wait for the JavaScript content to load
        time.sleep(5)

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find elements that may contain course information
        course_elements = soup.find_all('div', class_='result result--group-start')

        for course in course_elements:
            course_title = course.find('span', class_='result__title')
            if course_title and any(keyword.lower() in course_title.get_text().lower() for keyword in keywords):
                # Extracting additional information
                course_code = course.find('span', class_='result__code').get_text() if course.find('span', class_='result__code') else ''
                meeting_time = course.find('span', class_='flex--grow').get_text() if course.find('span', class_='flex--grow') else ''
                instructor = course.find('span', class_='result__flex--9').get_text() if course.find('span', class_='result__flex--9') else ''
                
                # Printing the course info
                print(f"Course Code: {course_code}")
                print(f"Title: {course_title.get_text()}")
                print(f"Meeting Time: {meeting_time.strip()}")
                print(f"Instructor: {instructor.strip()}")
                print("-" * 50)

    finally:
        driver.quit()

# URL of the website to scrape
url = 'https://atlas.emory.edu/'

# Keywords to search for
keywords = ['artificial intelligence', 'ai', 'machine learning', 'deep learning']

# Path to your WebDriver
# download from https://sites.google.com/chromium.org/driver/downloads before use
driver_path = '/Users/iriszheng/Downloads/chromedriver-mac-arm64/chromedriver' 

# Fetch and print course data
fetch_course_data(url, keywords, driver_path)