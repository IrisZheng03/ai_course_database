from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Replace '/path/to/chromedriver' with the actual path to your ChromeDriver
driver_path = '/Users/iriszheng/Downloads/chromedriver-mac-arm64/chromedriver' 
service = Service(executable_path=driver_path)

driver = webdriver.Chrome(service=service)
driver.get("https://www.selenium.dev/")
