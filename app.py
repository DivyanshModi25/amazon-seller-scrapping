from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from io import StringIO
import csv
from datetime import datetime



app = Flask(__name__)

# Enable CORS for all routes
CORS(app)


# @app.route('/get-data')
# def getData():
  

#     # Define the scope
#     scope = ["https://spreadsheets.google.com/feeds", 
#                  "https://www.googleapis.com/auth/spreadsheets",
#                  "https://www.googleapis.com/auth/drive"]

#     # Load credentials from the downloaded JSON
#     creds = ServiceAccountCredentials.from_json_keyfile_name("/home/divyansh/Downloads/practical-theme-433607-e1-883bba711d0c.json", scope)

#     # Authorize the client
#     client = gspread.authorize(creds)


#     sheet = client.open("amazon_seller").sheet1  # or .worksheet("Sheet1")

#     # Read data
#     data = sheet.get_all_records()
#     # print("Current Data:", data)

#     ssn_list = [row['ssn'] for row in data]
#     print(ssn_list)
#     website_host="https://www.amazon.in/Nordic-Naturals-Ultimate-Omega-Lemon/dp"
#     city_list = [key for key in data[0].keys() if key != 'ssn']
#     print(city_list)


#     return jsonify({"status": "success", "data": data})


now = datetime.now()
timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
filename_str = now.strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
url_link="https://www.amazon.in/Nordic-Naturals-Ultimate-Omega-Lemon/dp/"



@app.route('/scrape-data',methods=['POST'])
def scrapper():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read CSV content
        csv_data = file.read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_data))

        # Extract the first column
        asin_list = df.iloc[:, 0].tolist()



        # import bot
        pincodes=["400097"]
        data=[]



        with open(filename_str, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Header row
            writer.writerow(['Item', 'Pincode', 'Seller', 'Price', 'Timestamp'])

            # Data rows
            for entry in data:
                asin = entry['asin']
                for location in entry['locations']:
                    row = [
                        asin,
                        timestamp_str,
                        location['pincode'],
                        location['seller'],
                        location['price']
                    ]
                    writer.writerow(row)





        return jsonify({"asin_list": asin_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




 
if __name__ == '__main__':
    app.run(debug=True)