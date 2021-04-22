import requests
from datetime import datetime
import smtplib
import time as t

MY_LAT = 50.735380
MY_LONG = 7.104300
ERROR_DEGREE = 5


def send_mail():
    my_email = os.environ["MY_EMAIL"]
    my_email_password = os.environ["MY_PASSWORD"]
    smtp_server = os.environ["MY_SMTP_SERVER"]

    recipient_email = "arasch13@web.de"
    email_subject = f"LOOK INTO THE SKY"
    email_text = "The ISS is currently above your location. Have a look around!"
    with smtplib.SMTP(smtp_server) as connection:
        connection.starttls()
        connection.login(user=sender_email, password=sender_email_password)
        connection.sendmail(
            from_addr=sender_email,
            to_addrs=recipient_email,
            msg=f"Subject:{email_subject}\n\n{email_text}"
        )


# run until found
not_found_yet = True
while not_found_yet:
    # get iss position
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    # get current time
    current_hour = int(datetime.today().hour)

    # get sunrise and sunset of my location
    parameters = {
        'lat': MY_LAT,
        'lng': MY_LONG,
        'formatted': 0
    }
    response = requests.get(url="https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = data['results']['sunrise']
    sunrise_hour = int(sunrise.split("T")[1].split(":")[0])
    sunset = data['results']['sunset']
    sunset_hour = int(sunset.split("T")[1].split(":")[0])

    # check if it is dark at my location
    is_dark = (sunset_hour <= current_hour <= 24) or (0 <= current_hour <= sunrise_hour)

    # check if the ISS is close to my current position
    is_near = MY_LAT - ERROR_DEGREE <= iss_latitude <= MY_LAT + ERROR_DEGREE \
              and MY_LONG - ERROR_DEGREE <= iss_longitude <= MY_LONG + ERROR_DEGREE

    # send email when both conditions are met and exit loop then
    if is_dark and is_near:
        send_mail()
        not_found_yet = False
    else:
        # wait 1 minute
        t.sleep(60)
