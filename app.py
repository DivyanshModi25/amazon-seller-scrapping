import os
import pandas as pd
from datetime import datetime
import csv
from bot import amazon_main



# main function
def main():
    csv_file_path = './fry_amazon_india_data.csv'  # Input CSV path

    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        exit()

    try:
        df = pd.read_csv(csv_file_path)
        asin_list = df.iloc[:, 0].tolist()
        print(f"ASINs Extracted: {asin_list}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        exit()

    pincodes = ["400097", "110001"]
     

    city_map = {
        "400097": "mumbai",
        "110001": "delhi",
        "560001": "bangalore",
        "500001": "hyderabad",
        "201301": "noida",
        "600001": "Tamil Nadu",
        "700002": "kolkata",
    }
    host_url = "https://www.amazon.in/Nordic-Naturals-Ultimate-Omega-Lemon/dp/"

    timestamp_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"amazon_scraped_{timestamp_now}.csv"

    try:
        with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Asin', 'Timestamp', 'Pincode', 'City', 'Seller', 'Price'])  # Header
        print(f"CSV header written to {output_filename}")
    except Exception as e:
        print(f"Error creating CSV: {e}")
        exit()

    amazon_main(pincodes, asin_list, host_url, output_filename, city_map)

    print(f"\nAll data written to {output_filename}")


if __name__ == "__main__":
    main()