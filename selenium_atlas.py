from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import os

search_keywords = ["artificial intelligence", "machine learning", "neural networks", "data science"]

# Initialize the Chrome driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)
driver.get('https://atlas.emory.edu/')

unique_courses = {}

for keyword in search_keywords:
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.element_to_be_clickable((By.ID, "crit-keyword")))
    element.clear()
    element.click()
    element.send_keys(keyword)
    element.send_keys(Keys.ENTER)

    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'result--group-start')))

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    divs = soup.find_all('div', class_='result result--group-start')

    for div in divs:
        course_code = div.find('span', class_='result__code').get_text(strip=True) if div.find('span', class_='result__code') else 'N/A'
        course_title = div.find('span', class_='result__title').get_text(strip=True) if div.find('span', class_='result__title') else 'N/A'
        instructor = div.find('span', class_='result__flex--9').get_text(strip=True) if div.find('span', class_='result__flex--9') else 'N/A'

        # this part may need modification each year (all elective courses will be extracted since they are different sections within same elective course)
        if course_code == 'MD 920' and course_title not in ['Translation: Elective: Artif.Intell/Machine Learning', 'Translation: Elective: Clinical Informatics']:
            continue

        # Use course code and title as a unique key
        course_key = (course_code, course_title)
        if course_key not in unique_courses:
            unique_courses[course_key] = [course_code, course_title, instructor]


'''categorize into different files'''

# Dictionaries for categorized courses, change if needed
medical_school_courses = {}
graduate_school_courses = {}
business_school_courses = {}
law_school_courses = {}
other_courses = {}

# Function to get the numeric part of the course code
def get_numeric_part(course_code):
    parts = course_code.split() 
    for part in parts:
        if part.isdigit(): 
            return int(part)
    return None 

# Categorize courses
for course_key, course_details in unique_courses.items():
    course_code = course_details[0].lower()

    # Medical school courses
    if course_code.startswith('md'):
        medical_school_courses[course_key] = course_details
    # Business school courses
    elif any(business_keyword in course_code for business_keyword in ['fin', 'isom', 'act', 'bus']):
        business_school_courses[course_key] = course_details
    # Law school courses
    elif 'law' in course_code:
        law_school_courses[course_key] = course_details
    else:
        numeric_part = get_numeric_part(course_code)
        # Graduate school courses (not already categorized and numeric part > 500)
        if numeric_part is not None and numeric_part > 500:
            graduate_school_courses[course_key] = course_details
        # All other courses
        else:
            other_courses[course_key] = course_details

script_directory = os.path.dirname(os.path.realpath(__file__))

data_csv_directory = os.path.join(script_directory, "data_csv")

if not os.path.exists(data_csv_directory):
    os.makedirs(data_csv_directory)

def write_courses_to_csv(courses, file_name):
    file_path = os.path.join(data_csv_directory, file_name)
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Code', 'Course Title', 'Instructor']) 
        for course in courses.values():
            writer.writerow(course)

write_courses_to_csv(medical_school_courses, 'medical_school_courses.csv')
write_courses_to_csv(business_school_courses, 'business_school_courses.csv')
write_courses_to_csv(law_school_courses, 'law_school_courses.csv')
write_courses_to_csv(graduate_school_courses, 'graduate_school_courses.csv')
write_courses_to_csv(other_courses, 'other_courses.csv')

write_courses_to_csv(unique_courses, 'courses_all.csv')

driver.quit()
