# https://www.thepythoncode.com/article/use-gmail-api-in-python
from __future__ import print_function
from api import *
from extract_clean import *
from extract_ago import *
import requests
import json
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import pickle
import email
import re
from base64 import urlsafe_b64decode, urlsafe_b64encode
import base64
import os.path
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


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

    data = create_json(numberOfRoom, start, end, type_code, firstname, lastname, tel, email,
                       booking_id, booking_date, ota_name, promotion, breakfast, adult_amount, kid_amount, paid_amount)

    # post_data(data, msg_id)


def main():
  # Variable creds will store the user access token.
    # If no valid token found, we will create one.
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Connect to the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    query = r'"subject:Traveloka"|"subject:Agoda"'

    # Call the API to retrieve the matching messages.
    result = service.users().messages().list(
        userId='me', q=query, labelIds=['INBOX']).execute()
    messages = result.get('messages', [])

    count = 0

    for msg in messages:
        # get data from list of id
        msg = service.users().messages().get(
            userId='me', id=msg['id']).execute()
        parts = msg['payload']['parts']

        # get subject's email
        headers = msg['payload']['headers']
        subject = next(
            (header['value'] for header in headers if header['name'] == 'Subject'), None)
        print("\nSubject: " + subject + "\n")

        # check msg_id.txt file (msg_id.txt - for keep message id of confirmed email)
        if not os.path.exists("msg_id.txt"):
            f = open("msg_id.txt", "a")
            f.write("")
            f.close()

        # get id' email for save in msg_id.txt
        msg_id = str(msg['id'])

        with open('msg_id.txt', "r") as f:
            search_id = re.search(msg_id, f.read())
            if not search_id:
                #  filter by subject' email
                if re.match(r'(Agoda\sBooking\sID\s\d{9})', subject):
                    ota_name = "agoda"
                    if re.search(r'(CONFIRMED)', subject):
                        print("filtered!")
                        parse_parts(service, parts, msg, ota_name, msg_id)
                        # save msg id in txt file
                        # with open('msg_id.txt', 'a') as f:
                        #     f.write(msg['id'] + '\n')
                        count += 1
                    elif re.search(r'(CANCELLED)', subject):

                        match = re.search(r'\d{9}', subject)
                        print("cancelled! id = " + match.group())
                        # break
                        delete_data(match.group())

        break
    print("\nAgoda confirmed emails that was filtered = " + str(count))


def parse_parts(service, parts, message, ota_name, msg_id):
    """
    Utility function that parses the content of an email partition
    """
    if parts:
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")
            if part.get("parts"):
                # recursively call this function when we see that a part
                # has parts inside
                parse_parts(service, part.get("parts"), folder_name, message)
            if mimeType == "text/plain":
                # if the email part is text plain
                if data:
                    text = urlsafe_b64decode(data).decode()
                    if ota_name == "agoda":
                        extract_agoda(text, ota_name, msg_id)
                    # elif ota_name == "traveloka":
                    #     extract_traveloka(text, ota_name, msg_id)
                    # elif ota_name == "expedia":
                    #     extract_expedia(text, ota_name, msg_id)

        # parts = msg['payload']['parts']
        # mimeType = parts.get("mimeType")
        # body = parts.get("body")
        # data = body.get("data")

        # if parts.get("parts"):
        #     if mimeType == "text/plain":
        #         # if the email parts is text plain
        #         if data:
        #             text = urlsafe_b64decode(data).decode()
        #             print(text)
        #             return text

        # if 'parts' in msg['payload']:
        #     if msg['payload']['parts'][0]['mimeType'] == "multipart/alternative":
        #         return msg['payload']['parts'][0]['parts'][0]['body']['data']
        #     else:
        #         return msg['payload']['parts'][0]['body']['data']
        # else:
        #     return msg['payload']['body']['data']


if __name__ == '__main__':
    main()
