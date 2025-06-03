import os
import pandas as pd
from datetime import datetime
import csv
import smtplib
import mimetypes
from email.message import EmailMessage
from bot import amazon_main 
from dotenv import load_dotenv
from multiprocessing import Pool
import tempfile


load_dotenv()

# emailing function
def send_email(output_filename, recipient_email,pincodes,company):
    timestamp_now = datetime.now().strftime("Date: %d-%m-%Y TIME:%H:%M:%S")

    sender_email = os.getenv("SENDER_EMAIL")  
    sender_password = os.getenv("SENDER_PASSWORD") 
    subject = f"Amazon Scraped Data CSV for - {timestamp_now}"
    body = f"Please find the attached CSV file containing the scraped data dated for {company} - {timestamp_now} for pincodes :- {pincodes} "

    # Create Email Message
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach CSV file
    with open(output_filename, "rb") as file:
        file_data = file.read()
        file_name = os.path.basename(output_filename)
        mime_type, _ = mimetypes.guess_type(output_filename)
        main_type, sub_type = mime_type.split("/") if mime_type else ("application", "octet-stream")
        msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=file_name)

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:  
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")



def scrape_single_location(args):
    location, asin_list, host_url, city_map, getCompetitorFlag, getProductTitleFlag, getProductTitleFlagHeader = args
    timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
    temp_file = f"./amazon_data/temp_{location}_{timestamp}.csv"

    # Write header for individual file
    with open(temp_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if getProductTitleFlagHeader:
            writer.writerow(['Asin','buy_box_flag' ,'Timestamp', 'Pincode', 'City', 'Seller', 'Price', 'coupon_text','Free Delivery','Fastest Delivery','seller count','Minimum Price','product_title'])
        else:
            writer.writerow(['Asin','buy_box_flag' ,'Timestamp', 'Pincode', 'City', 'Seller', 'Price', 'coupon_text','Free Delivery','Fastest Delivery','seller count','Minimum Price'])

    amazon_main([location], asin_list, host_url, temp_file, city_map, getCompetitorFlag, getProductTitleFlag)
    return temp_file




# Main function
# def main(company,pincodes,city_map,sendMailFlag,getCompetitorFlag,getProductTitleFlag):
    
    
#     output_dir = "./amazon_data"
#     os.makedirs(output_dir, exist_ok=True)

#     csv_file_path = f'./{company}.csv'  # Input CSV path

#     if not os.path.exists(csv_file_path):
#         print(f"File not found: {csv_file_path}")
#         exit()

#     try:
#         df = pd.read_csv(csv_file_path)
#         asin_list = df.iloc[:, 0].tolist()
#     except Exception as e:
#         print(f"Error reading CSV: {e}")
#         exit()

    
#     host_url = "https://www.amazon.in/dp/"

#     timestamp_now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
#     output_filename = f"./amazon_data/{company}_{timestamp_now}.csv"

#     try:
#         with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
#             writer = csv.writer(file)
#             if(getProductTitleFlag):
#                 writer.writerow(['Asin','buy_box_flag' ,'Timestamp', 'Pincode', 'City', 'Seller', 'Price', 'coupon_text','Free Delivery','Fastest Delivery','seller count','Minimum Price','product_title'])  # Header
#             else:
#                 writer.writerow(['Asin','buy_box_flag' ,'Timestamp', 'Pincode', 'City', 'Seller', 'Price', 'coupon_text','Free Delivery','Fastest Delivery','seller count','Minimum Price'])  # Header

#         print(f"CSV header written to {output_filename}")
#     except Exception as e:
#         print(f"Error creating CSV: {e}")
#         exit()

#     amazon_main(pincodes, asin_list, host_url, output_filename, city_map,getCompetitorFlag,getProductTitleFlag)

#     print(f"\nAll data written to {output_filename}")

#     # Send email after CSV is created
#     if(sendMailFlag):
#         recipient_emails = os.getenv("RECIPIENT_EMAIL")
#         send_email(output_filename, recipient_emails,pincodes,company)


def main(company, pincodes, city_map, sendMailFlag, getCompetitorFlag, getProductTitleFlag):
    os.makedirs("./amazon_data", exist_ok=True)
    csv_file_path = f'./{company}.csv'

    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        return

    try:
        df = pd.read_csv(csv_file_path)
        asin_list = df.iloc[:, 0].tolist()
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    host_url = "https://www.amazon.in/dp/"
    timestamp_now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    final_output = f"./amazon_data/{company}_{timestamp_now}.csv"

    # Prepare multiprocessing tasks
    tasks = [
        (pincode, asin_list, host_url, city_map, getCompetitorFlag, getProductTitleFlag, getProductTitleFlag)
        for pincode in pincodes
    ]

    print(f"Starting parallel scraping for {len(pincodes)} pincodes...")

    with Pool(processes=min(4, len(pincodes))) as pool:
        temp_files = pool.map(scrape_single_location, tasks)

    print("Merging results into final CSV...")

    # Merge all temp CSVs into one
    with open(final_output, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        header_written = False
        for temp_file in temp_files:
            with open(temp_file, mode='r', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                header = next(reader)
                if not header_written:
                    writer.writerow(header)
                    header_written = True
                for row in reader:
                    writer.writerow(row)
            os.remove(temp_file)

    print(f"Final data written to {final_output}")

    if sendMailFlag:
        recipient_emails = os.getenv("RECIPIENT_EMAIL")
        send_email(final_output, recipient_emails, pincodes, company)



if __name__ == "__main__":

    company='nordic'
    pincodes = ["400001","110001","560001","500001","600001","226001","700002"]
    city_map = {
        "400001": "Mumbai",
        "110001": "Delhi",
        "560001": "Bangalore",
        "500001": "Hyderabad",
        "201301": "noida",
        "600001": "Chennai",
        "700002": "Kolkata",
        "226001":"Lucknow"
    }
    sendMailFlag=True    
    getCompetitorFlag=True
    getProductTitleFlag=False 
    main(company,pincodes,city_map,sendMailFlag,getCompetitorFlag,getProductTitleFlag)
