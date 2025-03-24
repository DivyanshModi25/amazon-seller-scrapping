import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

# Initialize WebDriver
def initialize_driver():
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# Scrape the trending topics
def enter_location(driver,locations,asin_list,host_url):

    finalData=[]

    for asin in asin_list:
        seller_list=[]
        target_webpage=f"{host_url}{asin}"

        driver.get(target_webpage)

        for location in locations:
            wait = WebDriverWait(driver, 5)  # wait up to 10 seconds
            link = wait.until(EC.presence_of_element_located((By.ID, "contextualIngressPtLink")))
            link.click()
            time.sleep(3)


            input=driver.find_element(By.ID,"GLUXZipUpdateInput")
            input.clear()
            input.send_keys(location+Keys.ENTER)

            time.sleep(3)

            seller=driver.find_element(By.ID,"sellerProfileTriggerId")
            seller_list.append({
                "pincode":location,
                "seller":seller.text
            })

        finalData.append({
            "asin":asin,
            "locations":seller_list
        })

    return finalData
    

# Main function to orchestrate login and scraping
def amazon_main(locations,asin_list,host_url):
    
    # Initialize WebDriver
    driver = initialize_driver()
    

   
    seller = enter_location(driver,locations,asin_list,host_url)
    print(seller)
    
    # Close the driver after scraping
    driver.quit()

    return seller


locations=["400097","560001","110001"]
asin_list=["B000HDV7YS"]
host_url="https://www.amazon.in/Nordic-Naturals-Ultimate-Omega-Lemon/dp/"
amazon_main(locations,asin_list,host_url)