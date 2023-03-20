# https://www.thepythoncode.com/article/use-gmail-api-in-python
from __future__ import print_function
from api import *
from extract_clean import *
from extract_ago import *
from extract_traveloka import *
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

    count_cf = 0
    count_cc = 0

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
                        parse_parts(service, parts, msg,
                                    subject, ota_name, msg_id)
                        # save msg id in txt file
                        # with open('msg_id.txt', 'a') as f:
                        #     f.write(msg['id'] + '\n')
                        count_cf += 1
                    elif re.search(r'(CANCELLED)', subject):
                        match = re.search(r'\d{9}', subject)
                        print("cancelled! id = " + match.group())
                        # break
                        # delete_data(match.group())
                        count_cc += 1
                if re.match(r'(^CONFIRMED.*Traveloka\sItinerary\sID\s\d{10})', subject):
                    if re.search(r'(CONFIRMED)', subject):
                        ota_name = "traveloka"
                        print("filtered!")
                        parse_parts(service, parts, msg,
                                    subject, ota_name, msg_id)
                        # save msg id in txt file
                        # with open('msg_id.txt', 'a') as f:
                        #     f.write(msg['id'] + '\n')
                        count_cf += 1
                    elif re.search(r'(CANCELLED)', subject):
                        match = re.search(r'\d{10}', subject)
                        print("cancelled! id = " + match.group())
                        # break
                        # delete_data(match.group())
                        count_cc += 1

        # break
    print("\nconfirmed emails that was filtered = " + str(count_cf))
    print("\ncancelled emails = " + str(count_cc))


def parse_parts(service, parts, message, subject, ota_name, msg_id):
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
                    elif ota_name == "traveloka":
                        extract_traveloka(text, subject, ota_name, msg_id)
                    # elif ota_name == "expedia":
                    #     extract_expedia(text, ota_name, msg_id)


if __name__ == '__main__':
    print("-"*80)
    main()
    time.sleep(2)
    # while True:
    #     main()
    #     print("sleep")
    #     time.sleep(12)
