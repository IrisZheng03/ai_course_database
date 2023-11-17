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

# Save to CSV
with open('courses_all.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Course Code', 'Course Title', 'Instructor'])  # CSV Headers

    for course in unique_courses.values():
        writer.writerow(course)



'''categorize into different files'''

# Dictionaries for categorized courses
medical_school_courses = {}
graduate_school_courses = {}
business_school_courses = {}
law_school_courses = {}
other_courses = {}

# Function to get the numeric part of the course code
def get_numeric_part(course_code):
    parts = course_code.split()  # Split the course code into parts
    for part in parts:
        if part.isdigit():  # Check if the part is a number
            return int(part)
    return None  # Return None if no numeric part is found

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

# Function to write courses to CSV
def write_courses_to_csv(courses, file_name):
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Course Code', 'Course Title', 'Instructor'])  # CSV Headers
        for course in courses.values():
            writer.writerow(course)

# Write categorized courses to separate CSV files
write_courses_to_csv(medical_school_courses, 'medical_school_courses.csv')
write_courses_to_csv(business_school_courses, 'business_school_courses.csv')
write_courses_to_csv(law_school_courses, 'law_school_courses.csv')
write_courses_to_csv(graduate_school_courses, 'graduate_school_courses.csv')
write_courses_to_csv(other_courses, 'other_courses.csv')

# Close the driver
driver.quit()
