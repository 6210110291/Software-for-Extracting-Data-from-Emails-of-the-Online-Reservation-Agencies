import re
from dateutil import parser

# Read file Example
import codecs
from bs4 import BeautifulSoup
f = codecs.open("index_ex.html", "r", encoding='utf-8')
sentence = BeautifulSoup(f, 'lxml')

# Extract data "Expedia"


def format_date(text):
    text_clean = re.search(r'([A-Za-z]{3,10})\s(\d{2}),\s(\d{4})', text)
    if text_clean:
        text = text_clean.group(0)
    date = parser.parse(text)
    print(date.strftime("%d-%m-%Y"))


def short_room_type(argument):
    switcher = {
        "standard double room fan": "STD",
        "standard twin room with fan": "TWIN",
        2: "two",
    }
    return switcher.get(argument, "none")

    # ------------------------------------------


def find_contact(text):

    text = re.sub('(ID|Id|id)+\n+[0-9]+', '', text)

    patterns_email = r'\b[\w\.-]+@[\w\.-]+\b'
    patterns_tel = r'((\+66|0)+(\d{1,2}\-?\d{3}\-?\d{3,4}))'

    # email
    print("email :", end=" ")
    match_email = re.finditer(patterns_email, text)
    if match_email:
        for match in match_email:
            print(match.group(), end=" ")
    else:
        print("none")

    # tel
    print("\ntel :", end=" ")
    text = text.lower()
    match_tel = re.search(r'\b(phone|tel|telephone)\b', text)
    if match_tel:
        match_tel = re.finditer(patterns_tel, text)
        if match_tel:
            for match in match_tel:
                print(match.group(), end=" ")
        else:
            print("none")
    else:
        print("none")


def find_id(text):
    print("booking_id :", end=" ")
    pos = text.find("ID:")
    # print(pos)
    if pos:
        text = text[pos:]

    patterns_id = r'[0-9]+'
    match_id = re.search(patterns_id, text)
    if match_id:
        match_id = match_id.group()
        print(match_id)
    else:
        print("none")

        # ------------------------------------------


def find_name(text):
    # Name
    print("firstname :", end=" ")
    for t in text:
        name = re.search(r'Guest: ', t)
        if name:
            name = t[name.end():]
            name = name.split()
            if len(name) == 1:
                print(name[0])
                print("lastname : " + "", end=" ")
            elif len(name) == 2:
                print(name[0])
                print("lastname : " + name[1], end=" ")
            else:
                for x in range(len(name)-1):
                    print(name[x+1], end=" ")
                print("\nlastname : " + name[0], end=" ")


def find_date(text):

    # Check in
    print("start :", end=" ")
    index = text.index('Check-In')
    if index >= 0:
        format_date(text[index+6])

    # Check out
    print("end :", end=" ")
    index = text.index('Check-Out')
    if index >= 0:
        format_date(text[index+6])


def find_total_and_promo(text):

    clean = r'\d{1,6}\.?\d{0,3}'

    # Promotion
    print("promotion :", end=" ")
    for t in text:
        t = t.lower()
        promo = re.search(r'promotion', t)
        if promo:
            promo = t[promo.end():]
            break
        else:
            promo = "none"
    print(promo)

    # Total Paid
    print("paid_amount :", end=" ")
    index = text.index('Total Cost:')
    if index >= 0:
        total = re.search(clean, text[index+1])
        if total.group() == '0':
            total = "none"
        else:
            total = total.group()
        print(total)


def find_information(text):

    clean = r'\d{1,2}'

    # Number of room
    print("numberOfRoom :", end=" ")
    for t in text:
        t = t.lower()
        room = re.search(r'number of room', t)
        if room:
            room = t[room.end():]
            room = re.search(clean, room)
            room = int(room.group())
            break
        else:
            room = 1
    print(room)

    # Room Type
    print("type_code :", end=" ")
    for t in text:
        t = t.lower()
        room = re.search(r'room type code: ', t)
        if room:
            room = t[room.end():]
            break
        else:
            room = "none"
    print(short_room_type(room))

    # Breakfast
    print("breakfast :", end=" ")
    for t in text:
        t = t.lower()
        breakfast = re.search(r'breakfast', t)
        if breakfast:
            breakfast = t[breakfast.end():]
            break
        else:
            breakfast = "no"
    print(breakfast)

    # Remark / Special Request
    print("remark :", end=" ")
    index = text.index('Special Request')
    if index >= 0:
        remark = text[index+1]
    else:
        remark = "none"
    print(remark)


def find_guest_number(text):
    clean = r'\d{1,2}'

    # Number of guest
    print("adult_amount :", end=" ")
    index = text.index('Adults')
    if index >= 0:
        amount = text[index+6]
        amount = re.search(clean, amount)
        amount = int(amount.group())
    else:
        amount = 0
    print(amount)

    print("kid_amount :", end=" ")
    index = text.index('Kids/Ages')
    if index >= 0:
        amount = text[index+6]
        amount = re.search(clean, amount)
        amount = int(amount.group())
    else:
        amount = 0
    print(amount)


# Driver Code
if __name__ == '__main__':

    # print(sentence)
    ota_name = "expedia"
    print("ota_name : " + ota_name)

    text = re.sub(r'<.*?>|&nbsp;', '', str(sentence))
    text = re.sub(r'https?:\/\/.*[\r\n]*', '', str(text))

    pos = text.find("Receive instant notifications")
    text = text[0:pos]
    # text = text.replace('\n\n',' ')

    # ----find id------
    find_id(text)

    # ----find contact------
    find_contact(text)
    # print("\n")

    text = [line.strip() for line in text.strip().split('\n')]
    while '' in text:
        text.remove('')
    # print("\n")
    # print(text)

    # ----find name and check in/out------
    find_name(text)
    print("\n")

    find_date(text)

    find_guest_number(text)

    find_total_and_promo(text)
    # print("\n")

    find_information(text)
