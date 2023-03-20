import re
from dateutil import parser
import json
import codecs
from bs4 import BeautifulSoup
from extract_clean import *
from api import *


def extract_traveloka(sentence, subject, ota_name, msg_id):
    if re.search("Pay upon Check-in", subject):
        ota_payment_status = "pay upon check-in"
    else:
        ota_payment_status = "paid"

    sentence = clean(sentence)
    text = sentence

    # booking_id, email, tel, adult_amount, kid_amount
    booking_id = find_booking_id(subject)
    sentence = re.sub(str(booking_id), '', str(text))

    email = find_email(text)
    tel = find_tel(text)
    adult_amount = find_guest_adult(text)
    kid_amount = find_guest_kid(text)

    # ------------------------------------------
    # breakfast, numberOfRoom
    text = cut_text(sentence, "Breakfast", "Special")

    breakfast = find_breakfast(text)
    numberOfRoom = find_numberOfRoom(text)

    # ------------------------------------------
    # firstname, lastname, start, end, booking_date
    text = cut_text(sentence, "City", "Room")
    text = text.replace('\n\n', ' ')
    text = text.replace(r'\s*', ' ')
    text = [line.strip() for line in text.strip().split('\n')]
    while '' in text:
        text.remove('')

    firstname = find_firstname(text)
    lastname = find_lastname(text)
    start = find_checkin(text)
    end = find_checkout(text)
    booking_date = find_booking_date(ota_payment_status, text)

    # ------------------------------------------
    # type_code
    text = cut_text(sentence, "Room Type", "Breakfast")
    pattern = r'\s{2,}'
    text = text_to_array(pattern, text)

    type_code = find_type_code(text)

    # ------------------------------------------
    # paid_amount, promotion
    text = cut_text(sentence, "Promotion", 0)
    pattern = r'\s{2,}'
    text = text_to_array(pattern, text)

    paid_amount = find_total(ota_payment_status, text)
    promotion = find_promo(text)

    # ------------------------------------------
    data = create_json(numberOfRoom, start, end, type_code, firstname, lastname, tel, email, booking_id,
                       booking_date, ota_name, promotion, breakfast, adult_amount, kid_amount, paid_amount, ota_payment_status)

    post_data(data, msg_id)


def format_date(text):
    match = re.search(r'([A-Za-z]{3,10})\s(\d{2}),\s(\d{4})', text)
    if match:
        text = match.group(0)
    date = parser.parse(text)
    return date.strftime("%d-%m-%Y")


def short_room_type(argument):
    switcher = {
        "Standard Double Room Fan": "STD",
        "Deluxe room": "DEL",
        "Executive room": "EXE",
    }
    return switcher.get(argument, "none")


def find_booking_id(subject):

    patterns_id = r'\d{10}'
    match = re.search(patterns_id, subject)
    if match:
        id = match.group()
    else:
        id = ""
    return id


def find_email(text):
    patterns_email = r'\b[\w\.-]+@(?!traveloka)[\w\.-]+\b'
    email = ""
    match_email = re.search(patterns_email, text)
    if match_email:
        email = str(match_email.group())
    else:
        email = ""
    return email


def find_tel(text):
    patterns_tel = r'((\+66|0)+(\d{1,2}\-?\d{3}\-?\d{3,4}))'
    tel = ""
    match_tel = re.search(patterns_tel, text)
    if match_tel:
        tel = str(match_tel.group())
    else:
        tel = ""
    return tel


def find_guest_adult(text):
    patterns = r'\d{1,2}'
    amount = re.search(r'[\d ]+(Adult|Adults)', text)
    if amount:
        amount = re.search(patterns, amount.group())
        amount = int(amount.group())
    else:
        amount = 0
    return amount


def find_guest_kid(text):
    patterns = r'\d{1,2}'
    amount = re.search(r'[\d ]+(Kid|Kids)', text)
    if amount:
        amount = re.search(patterns, amount.group())
        amount = int(amount.group())
    else:
        amount = 0
    return amount


def find_firstname(text):
    index = text.index('Customer First Name')
    if index >= 0:
        return text[index+4]
    return ""


def find_lastname(text):
    index = text.index('Customer Last Name')
    if index >= 0:
        return text[index+4]
    return ""


def find_checkin(text):
    index = text.index('Check-in')
    if index >= 0:
        return format_date(text[index+4])
    return ""


def find_checkout(text):
    index = text.index('Check-out')
    if index >= 0:
        return format_date(text[index+4])
    return ""


def find_booking_date(type, text):
    if type == "pay upon check-in":
        index = text.index('BookedonUTC')
        return format_date(text[index+3])
    else:
        index = text.index('Booking time (UTC+0)')
        return format_date(text[index+1])
    return ""


def find_total(type, text):
    index = 0
    total = ""
    if type == "pay upon check-in":
        index = text.index('Total you need to collect')
    else:
        index = text.index('Total you will receive')

    if index >= 0:
        total = re.search(r'\d{0,3}\,*\d{1,6}\.?\d{0,3}', text[index+1])
        total = total.group()
    else:
        total = ""

    return total


def find_promo(text):
    index = 0
    promo = ""
    index = text.index('Promotion')
    if index >= 0:
        promo = text[index+2]
    else:
        promo = ""

    return str(promo)


def find_numberOfRoom(text):
    numberOfRoom = 1
    match = re.search(r'\d{1,2}', text)
    if match:
        numberOfRoom = int(match.group())
    return numberOfRoom


def find_type_code(text):
    index = 0
    index = text.index('Room Type')
    if index >= 0:
        type_code = text[index + 3]
    else:
        type_code = ""
    return str(type_code)


def find_breakfast(text):
    breakfast = False
    if re.search("no", text.lower()):
        breakfast = False
    else:
        breakfast = True
    return breakfast


# Driver Code
# if __name__ == '__main__':

    # ota_name = "traveloka"
    # print("ota_name : " + ota_name)
    # # print("\n")

    # clean = re.compile('<.*?>|&nbsp;')
    # text = re.sub(clean, '', str(sentence))
    # # print(text)

    # # ----find id------
    # # booking_id = find_booking_id(text)

    # # ----find contact------
    # tel = find_tel(text)
    # email = find_email(text)

    # # print("\n")
    # adult_amount = find_guest_adult(text)
    # kid_amount = find_guest_kid(text)

    # pos = text.find("Attention Hotel Staff")
    # text = text[0:pos]
    # # text = text.replace('\n\n',' ')

    # text = [line.strip() for line in text.strip().split('\n')]
    # while '' in text:
    #     text.remove('')

    # # ----find name and check in/out------
    # firstname = find_firstname(text)
    # lastname = find_lastname(text)
    # start = find_checkin(text)
    # end = find_checkout(text)
    # find_total_and_promo(text)
    # breakfast = find_breakfast(text)
    # type_code = find_type_code(text)
    # numberOfRoom = find_numberOfRoom(text)

    # print("\n-----JSON-----\n")

    # # Create a Python dictionary
    # data = {
    #     "outerServiceBooking": True,
    #     "numberOfRoom": 35,
    #     "start": start,
    #     "end": end,
    #     "type_code": type_code,
    #     "customer": {
    #         "firstname": firstname,
    #         "lastname": lastname,
    #         "tel": tel,
    #         "email": email
    #     },
    #     "ota_attribute": {
    #         "booking_id": booking_id,
    #         "ota_name": ota_name,
    #         "promotion": "",
    #         "breakfast": breakfast,
    #         "adult_amount": adult_amount,
    #         "kid_amount": kid_amount
    #     },
    #     "remark": "Standard Double Room Fan",
    #     "payment": {
    #         "paid_amount": 282.2
    #     }
    # }

    # # Convert the dictionary to a JSON object
    # json_data = json.dumps(data)

    # print(json_data)
