import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import csv
from datetime import datetime


# driver
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver




# scraper
def enter_location(driver, locations, asin_list, host_url, output_filename, city_map):
    for asin in asin_list:
        target_webpage = f"{host_url}{asin}"
        driver.get(target_webpage)

        for location in locations:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            city = city_map.get(location, "Unknown")
            seller_text = ""
            price_text = ""  # Placeholder for price (you can implement price scraping later)

            try:
                time.sleep(2)
                wait = WebDriverWait(driver, 5)
                link = wait.until(EC.presence_of_element_located((By.ID, "contextualIngressPtLink")))
                link.click()
                time.sleep(2)
                # print("click done")

                input_box = driver.find_element(By.ID, "GLUXZipUpdateInput")
                input_box.clear()
                input_box.send_keys(location + Keys.ENTER)
                time.sleep(3)
                # print("new locations updated")

                seller = driver.find_element(By.ID, "sellerProfileTriggerId")
                seller_text = seller.text
                # print("fetched seller")

                price=driver.find_element(By.XPATH,"/html/body/div[2]/div/div/div[5]/div[4]/div[13]/div/div/div[4]/div[1]/span[3]/span[2]/span[2]")
                price_text=price.text
                # print("fetched price")

                time.sleep(2)

                print(f"Success: ASIN {asin}, Pincode {location}, Seller: {seller_text}")

            except Exception as e:
                print(f"Error at ASIN {asin}, Pincode {location}: {e}")
                # Seller and Price remain blank in this case

            # Write to CSV regardless of success or failure
            row = [asin, timestamp, location, city, seller_text, price_text]
            with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
                csv.writer(file).writerow(row)
            print(f"Written data for ASIN {asin}, Pincode {location}")




# scrapper initializer
def amazon_main(locations, asin_list, host_url, output_filename, city_map):
    driver = initialize_driver()
    enter_location(driver, locations, asin_list, host_url, output_filename, city_map)
    driver.quit()


