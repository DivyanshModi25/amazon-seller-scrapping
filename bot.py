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
    driver.get("https://www.amazon.in/dp/B015TQ7USO")
    time.sleep(3)
    for location in locations:
        try:
            # Go to Amazon home page to change location first
            driver.get("https://www.amazon.in/dp/B015TQ7USO")
            time.sleep(2)

            wait = WebDriverWait(driver, 5)
            link = wait.until(EC.presence_of_element_located((By.ID, "contextualIngressPtLink")))
            link.click()
            time.sleep(2)

            input_box = driver.find_element(By.ID, "GLUXZipUpdateInput")
            input_box.clear()
            input_box.send_keys(location + Keys.ENTER)
            time.sleep(3)

            print(f"Location updated to {location} ({city_map.get(location, 'Unknown')})")
        except Exception as e:
            print(f"Failed to set location {location}: {e}")
            # Continue scraping with next location
            continue

        # After setting location, scrape all ASINs for this location
        for asin in asin_list:
            target_webpage = f"{host_url}{asin}"
            driver.get(target_webpage)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            city = city_map.get(location, "Unknown")
            seller_text = "no_buy_box"
            price_text = ""
            coupon_text=""

            try:
                time.sleep(2)

                # Scrape seller
                seller = driver.find_element(By.ID, "sellerProfileTriggerId")
                seller_text = seller.text

                # Scrape price (adjust XPATH if needed)
                price = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[5]/div[1]/div[4]/div/div[1]/div/div/div/form/div/div/div/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span[2]")
                price_text = price.text

                # Coupon scraping
                try:
                    label = driver.find_element(By.XPATH, "//label[contains(@id, 'couponText')]")
                    # print("scrapped label")
                    coupon_text = label.text.split("\n")[0].strip()
                    coupon_text=coupon_text.replace("Apply","").strip()
                    # print("failed here")
                except:
                    coupon_text = "no discount"

                print(f"Success: Pincode {location}, ASIN {asin}, Seller: {seller_text}, Price: {price_text},coupon:{coupon_text}")

            except Exception as e:
                print(f"Error at Pincode {location}, ASIN {asin}: {e}")
                # Leave seller_text and price_text empty

            # Write data to CSV regardless
            row = [asin, timestamp, location, city, seller_text, price_text ,coupon_text]
            with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
                csv.writer(file).writerow(row)
            print(f"Written data for ASIN {asin}, Pincode {location}")




# scrapper initializer
def amazon_main(locations, asin_list, host_url, output_filename, city_map):
    driver = initialize_driver()
    enter_location(driver, locations, asin_list, host_url, output_filename, city_map)
    driver.quit()

