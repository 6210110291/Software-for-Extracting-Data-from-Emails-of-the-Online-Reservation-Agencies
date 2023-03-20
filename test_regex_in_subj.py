# https://www.thepythoncode.com/article/use-gmail-api-in-python
from __future__ import print_function

import os.path

# for encoding/decoding messages in base64
import base64
from base64 import urlsafe_b64decode, urlsafe_b64encode

import re
import email
import pickle
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
import requests

from extract_traveloka import *
from extract_clean import *
from api import *

# for dealing with attachement MIME types
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.image import MIMEImage
# from email.mime.audio import MIMEAudio
# from email.mime.base import MIMEBase
# from mimetypes import guess_type as guess_mime_type


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def parse_parts(service, parts, message, subject, ota_name, pay_type):
    q = 0
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
                    print(text)
                    # extract_traveloka(text, subject, ota_name, pay_type)
                    # q += 1
                    # if(q == 2):
                    #     quit()
                    # quit()
            # elif mimeType == "text/html":
            #     # if the email part is an HTML content
            #     # save the HTML file and optionally open it in the browser
            #     if not filename:
            #         filename = "index.html"
            #     # filepath = os.path.join(folder_name, filename)
            #     print("Saving HTML to", filepath)
            #     with open(filepath, "wb") as f:
            #         f.write(urlsafe_b64decode(data))
            # else:
            #     # attachment other than a plain text or HTML
            #     for part_header in part_headers:
            #         part_header_name = part_header.get("name")
            #         part_header_value = part_header.get("value")
            #         if part_header_name == "Content-Disposition":
            #             if "attachment" in part_header_value:
            #                 # we get the attachment ID
            #                 # and make another request to get the attachment itself
            #                 # print("Saving the file:", filename,
            #                 #       "size:", get_size_format(file_size))
            #                 attachment_id = body.get("attachmentId")
            #                 attachment = service.users().messages() \
            #                     .attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
            #                 data = attachment.get("data")
            #                 filepath = os.path.join(folder_name, filename)
            #                 if data:
            #                     with open(filepath, "wb") as f:
            #                         f.write(urlsafe_b64decode(data))


def extract_traveloka(sentence, subject, ota_name, pay_type):
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
    booking_date = find_booking_date(pay_type, text)

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

    paid_amount = find_total(pay_type, text)
    promotion = find_promo(text)

    # ------------------------------------------
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

    # query = r'"subject:^CONFIRMED|^Expedia"'
    query = r'"subject:New Agoda"'

    # Call the API to retrieve the matching messages.
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])

    # count number of email
    counting = 0

    # Print the subject of each matching email.
    for msg in messages:
        msg = service.users().messages().get(
            userId='me', id=msg['id']).execute()
        headers = msg['payload']['headers']
        parts = msg['payload']['parts']

        subject = next(
            (header['value'] for header in headers if header['name'] == 'Subject'), None)

        # r'(^CONFIRMED.*Traveloka\sItinerary\sID)|(^Expedia.*New\sBooking.*Arriving)', subject)
        # check agency "Traveloka"

        if re.match(r'(^CONFIRMED.*Traveloka\sItinerary\sID)', subject):
            ota_name = "traveloka"
            print("\nSubject: " + subject + "\n")
            if re.search("Pay upon Check-in", subject):
                pay_type = "pay upon check-in"
            else:
                pay_type = "paid"

        counting += 1
        ota_name = "traveloka"
        pay_type = "paid"
        parse_parts(service, parts,
                    msg, subject, ota_name, pay_type)

        # parse_parts(service, parts, folder_name,
        #             msg, subject, ota_name, pay_type)

        # check agency "Expedia"
        # else if re.match(r'(^Expedia.*New\sBooking.*Arriving)', subject):

        # check agency "Agoda"
        # else if re.match(r'(^Expedia.*New\sBooking.*Arriving)', subject):

    print("Number of email that is filtered  = " + str(counting))


if __name__ == '__main__':
    main()
