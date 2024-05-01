import requests
from bs4 import BeautifulSoup
import smtplib
import re
import os
import time
from dotenv import load_dotenv


course_links = ["https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=1245&subject=CS&cournum=234", "https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?level=under&sess=1245&subject=CS&cournum=231"]



def course_details(url):
    # Regex pattern to capture values after 'subject=' and 'cournum='
    pattern = r"subject=([A-Za-z0-9]+)&cournum=([0-9]+)"
    match = re.search(pattern, url)
    if match:
        subject, course_number = match.groups()
        return subject, course_number
    else:
        return None



def send_email(course_code, course_num):
    load_dotenv('.env')
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    receiver_email = os.getenv('RECEIVER_EMAIL')
    
    # creates SMTP session
    s = smtplib.SMTP('smtp-mail.outlook.com', 587)
    # start TLS for security
    s.starttls()
    s.login(sender_email, sender_password)

    # message to be sent
    subject = f"Open Spot for {course_code} {course_num}"
    body = f"Go grab the open spot for {course_code} {course_num}!!"
    message = f"Subject: {subject}\n\n {body}"

    s.sendmail(sender_email, receiver_email, message)
    s.quit()


# Returns True if there is space in the course. False otherwise
def check_availability(course_link):
    response = requests.get(course_link)
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all('table')
    enrollment_table = None
    for table in tables:
        if 'Enrl Cap' in table.text:
            enrollment_table = table
            break

    # Locate the enrl cap and enrl total
    rows = enrollment_table.find_all('td')
    enrl_cap = rows[12].text.strip()
    enrl_tot = rows[13].text.strip()
    
    if enrl_tot < enrl_cap:
        return True
    
    return False


def main():
    while True:
        time.sleep(100)
        for course_link in course_links:
            if check_availability(course_link):
                course_name, course_num  = course_details(course_link)
                send_email(course_name, course_num)



if __name__ == "__main__":
    main()

