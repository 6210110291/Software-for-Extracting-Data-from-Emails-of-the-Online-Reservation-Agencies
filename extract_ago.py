import re
from dateutil import parser
import json
import codecs
from bs4 import BeautifulSoup
from extract_clean import *
from api import *


def extract_agoda(sentence, ota_name, msg_id):
    sentence = clean(sentence)
    text = sentence

    # booking_id, email, tel, adult_amount, kid_amount
    booking_id = find_booking_id(text)
    sentence = re.sub(str(booking_id), '', str(text))

    email = find_email(text)
    tel = find_tel(text)
    adult_amount = find_guest_adult(text)
    kid_amount = find_guest_kid(text)

    # ------------------------------------------
    # firstname, lastname, start, end
    text = cut_text(sentence, "Customer First Name", "Other")
    pattern = r'[*]\s*'
    text = text_to_array(pattern, text)
    # print(text)
    firstname = find_firstname(text)
    lastname = find_lastname(text)
    start = find_checkin(text)
    end = find_checkout(text)

    # ***** don't change  line *****
    text = cut_text(sentence, "Room Type", "Rate Plan")
    pattern = r'[*]\s*'
    text = text_to_array(pattern, text)

    type_code = find_type_code(text)
    numberOfRoom = find_numberOfRoom(text)

    # ******************************

    text = cut_text(sentence, "Net rate", 0)
    paid_amount = find_total(text)

    # booking_date = find_booking_date(pay_type, text)
    # breakfast = find_breakfast(text)

    promotion = ""
    breakfast = False
    booking_date = ""
    ota_payment_status = ""

    data = create_json(numberOfRoom, start, end, type_code, firstname, lastname, tel, email, booking_id,
                       booking_date, ota_name, promotion, breakfast, adult_amount, kid_amount, paid_amount, ota_payment_status)
    post_data(data, msg_id)


def format_date(text):
    match = re.search(r'([A-Za-z]{3,10})\s(\d{2}),\s(\d{4})', text)
    if match:
        text = match.group(0)
    date = parser.parse(text)
    return date.strftime("%Y-%m-%d")


def format_payment(text):
    text = re.sub(r'(,)', '', text)
    return text


def short_room_type(argument):
    switcher = {
        "Standard Double Room Fan": "STD",
        "Deluxe room": "DEL",
        "Executive room": "EXE",
    }
    return switcher.get(argument, "none")


def find_booking_id(subject):
    patterns_id = r'\d{9}'
    match = re.search(patterns_id, subject)
    if match:
        id = match.group()
    else:
        id = ""
    return id


def find_email(text):
    patterns_email = r'\b[\w\.-]+@(?!agoda)[\w\.-]+\b'
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
    amount = re.search(r'\d{1,2}\s+(Adult|Adults)', text)
    if amount:
        amount = re.search(r'\d{1,2}', amount.group())
        amount = int(amount.group())
    else:
        amount = 0
    return amount


def find_guest_kid(text):
    amount = re.search(r'\d{1,2}\s+(Kid|Kids)', text)
    if amount:
        amount = re.search(r'\d{1,2}', amount.group())
        amount = int(amount.group())
    else:
        amount = 0
    return amount


def find_firstname(text):
    index = text.index('Customer First Name')
    if index >= 0:
        text = re.sub(r'\n|\s{2,}', '', str(text[index+1]))
        return text
    return ""


def find_lastname(text):
    index = text.index('Customer Last Name')
    if index >= 0:
        text = re.sub(r'\n|\s{2,}', '', str(text[index+1]))
        return text
    return ""


def find_checkin(text):
    index = text.index('Check-in')
    if index >= 0:
        return format_date(text[index+1])
    return ""


def find_checkout(text):
    index = text.index('Check-out')
    if index >= 0:
        return format_date(text[index+1])
    return ""


def find_booking_date(type, text):
    if type == "pay upon check-in":
        index = text.index('BookedonUTC')
        return format_date(text[index+3])
    else:
        index = text.index('Booking time (UTC+0)')
        return format_date(text[index+1])
    return ""


def find_total(text):
    total = ""
    total = re.search(r'\d{0,3}\,*\d{1,6}\.?\d{0,3}', text)
    if total:
        total = total.group()

    return format_payment(total)


def find_numberOfRoom(text):
    numberOfRoom = -1
    index = 0
    index = text.index('No. of Rooms')
    if index >= 0:
        text = text[index + 3]
        match = re.search(r'\d{1,2}', text)
        if match:
            numberOfRoom = int(match.group())
    return numberOfRoom


def find_type_code(text):
    index = 0
    index = text.index('Room Type')
    if index >= 0:
        text = text[index + 4]
        type_code = re.search(r'.+Room', text)
        if type_code:
            type_code = type_code.group()
        else:
            type_code = ""
    else:
        type_code = ""
    return type_code
