import json
import requests
import re
import os.path
import os
from datetime import datetime
from extract_clean import *


def create_json(numberOfRoom, start, end, type_code, firstname, lastname, tel, email, booking_id, booking_date, ota_name, promotion, breakfast, adult_amount, kid_amount, paid_amount, ota_payment_status):
    # print_data("ota_name", ota_name)
    # print_data("booking_id", booking_id)
    # print_data("email", email)
    # print_data("tel", tel)
    # print_data("adult_amount", adult_amount)
    # print_data("kid_amount", kid_amount)
    # print_data("firstname", firstname)
    # print_data("lastname", lastname)
    # print_data("start", start)
    # print_data("end", end)
    # print_data("numberOfRoom", numberOfRoom)
    # print_data("type_code", type_code)
    # print_data("paid_amount", paid_amount)
    # print_data("ota_payment_status", ota_payment_status)
    # print_data("promotion", promotion)
    # print_data("breakfast", breakfast)
    # print_data("booking_date", booking_date)
    data = {
        "outerServiceBooking": True,
        "numberOfRoom": numberOfRoom,
        "start": start,
        "end": end,
        "type_code": "STD",
        "customer": {
            "firstname": firstname,
            "lastname": lastname,
            "tel": tel,
            "email": email
        },
        "ota_attribute": {
            "booking_id": booking_id,
            "ota_name": ota_name,
            "promotion": promotion,
            "breakfast": breakfast,
            "adult_amount": adult_amount,
            "kid_amount": kid_amount
        },
        "remark": "",
        "payment": {
            "paid_amount": paid_amount,
            "ota_payment_status": ota_payment_status,
            "discount_amount": 0,
            "paid_type": ""
        }
    }

    json_formatted_str = json.dumps(data, indent=4)

    print(json_formatted_str)
    print("\n"*3)
    return data


def post_data(data, msg_id):
    # Convert the JSON object to a string
    json_data = json.dumps(data)

    # Define the Bearer token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYyOGI1NGFjOTgyZDgwMDAxMzg0YzI3OCIsInVzZXJuYW1lIjoiYWRtaW4iLCJleHAiOjE2ODQzOTk2NzEsImlhdCI6MTY3NjYyMzY3MX0.8VyGyYLlm095K-6sTdWLLcT93yKiDz2PMKPHUEcp-18"

    # Send the JSON data to a website using the HTTP POST method with the Authorization header
    url = 'https://demo.eaccom.net/api/v1/booking'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(url, data=json_data, headers=headers)

    # Print the response from the website
    print(response.text)

    match = re.search("error", response.text)
    if match:
        if not os.path.exists("log_api.txt"):
            f = open("log_api.txt", "a")
            f.write("")
        with open('log_api.txt', "a") as f:
            f.write("msg_id " + msg_id + ' \ ' + str(datetime.now()) +
                    ' : ' + str(response.text) + '\n\n')
            f.close()


def delete_data(booking_id):

    # Define the Bearer token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYyOGI1NGFjOTgyZDgwMDAxMzg0YzI3OCIsInVzZXJuYW1lIjoiYWRtaW4iLCJleHAiOjE2ODQzOTk2NzEsImlhdCI6MTY3NjYyMzY3MX0.8VyGyYLlm095K-6sTdWLLcT93yKiDz2PMKPHUEcp-18"

    url = f'https://demo.eaccom.net/api/v1/booking/ota/868677217'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.delete(url, headers=headers)
    print(url)
    # print content of request
    print(response.json())
