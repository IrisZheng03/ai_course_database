from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv

# Search keywords
search_keywords = ["artificial intelligence", "machine learning", "neural networks", "data science"]

# Initialize the Chrome driver
driver = webdriver.Chrome()
driver.get('https://atlas.emory.edu/')

# Create a dictionary to hold course details and avoid duplicates
unique_courses = {}

for keyword in search_keywords:
    # Wait for the search box to be clickable
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID, "crit-keyword")))

    # Clear the search box, enter the keyword and submit
    element.clear()
    element.click()
    element.send_keys(keyword)
    element.send_keys(Keys.ENTER)

    # Wait for the results to load
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'result--group-start')))

    # Extract the page source
    html_content = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    divs = soup.find_all('div', class_='result result--group-start')

    for div in divs:
        course_code = div.find('span', class_='result__code').get_text(strip=True) if div.find('span', class_='result__code') else 'N/A'
        course_title = div.find('span', class_='result__title').get_text(strip=True) if div.find('span', class_='result__title') else 'N/A'
        instructor = div.find('span', class_='result__flex--9').get_text(strip=True) if div.find('span', class_='result__flex--9') else 'N/A'

        if course_code == 'MD 920' and course_title not in ['Translation: Elective: Artif.Intell/Machine Learning', 'Translation: Elective: Clinical Informatics']:
            continue

        # Use course code and title as a unique key
        course_key = (course_code, course_title)
        if course_key not in unique_courses:
            unique_courses[course_key] = [course_code, course_title, instructor]

# Close the driver after all searches are done
driver.quit()

# Save to CSV
with open('courses.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Course Code', 'Course Title', 'Instructor'])  # CSV Headers

    for course in unique_courses.values():
        writer.writerow(course)
