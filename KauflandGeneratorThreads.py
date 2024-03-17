import requests
import uuid
import json
import time
import re
import os
import threading


AccountsToGenerate = 30

def GenerateAccount():
    url = "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=50000"

    responce = requests.get(url)

    jtext = json.loads(responce.text)

    chosenEmail = jtext[1]
    teile = chosenEmail.split("@")
    Username = teile[0]
    domain = teile[1]

    def GetRequestID():
        url = "https://account.kaufland.com/authz-srv/authrequest/authz/generate"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "de-DE",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Referer": "https://www.kaufland.de/",
            "Origin": "https://www.kaufland.de",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Connection": "keep-alive",
            "TE": "trailers"
        }

        data = {
            "client_id": "885e28ab-bbfe-4ee1-b437-5c31854a327d",
            "redirect_uri": "https://www.kaufland.de/iam/success",
            "scope": "profile email offline_access openid",
            "response_type": "code",
            "ui_locales": "de-DE",
            "state": "eyJzIjoiaHR0cHM6Ly93d3cua2F1ZmxhbmQuZGUifQ=="
        }

        response = requests.post(url, headers=headers, json=data)
        responsej = json.loads(response.text)
        finalrequestId = responsej["data"]["requestId"]
        return finalrequestId


    email = chosenEmail


    def GetEmails():
        loginurl = f"https://www.1secmail.com/api/v1/?action=getMessages&login={Username}&domain={domain}" ## {jtext[1]}

        Emails = requests.get(loginurl)

        if Emails and Emails.text != "[]":
            JEmails = json.loads(Emails.text)
            return JEmails
        else:
            return Emails.text




    x_request_id = GetRequestID()

    #885e28ab-bbfe-4ee1-b437-5c31854a327d

    url = "https://account.kaufland.com/users-srv/register"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de-DE",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Referer": "https://www.kaufland.de/",
        "requestId": x_request_id,
        "Origin": "https://www.kaufland.de",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive",
        "TE": "trailers"
    }

    data = {
        "given_name": email,
        "family_name": email,
        "provider": "self",
        "password": email,
        "customFields": {
            "marketplace_tos_de": True,
            "marketplace_closing_terms": True,
            "preferredStore": "DE0000"
        },
        "contact_source": "marketplace",
        "email": email
    }

    response = requests.post(url, headers=headers, json=data)

    url = "https://account.kaufland.com/verification-srv/account/initiate/sdk"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de-DE",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "Referer": "https://www.kaufland.de/",
        "Origin": "https://www.kaufland.de",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive",
        "TE": "trailers"
    }

    data = {
        "requestId": x_request_id,
        "processingType": "CODE",
        "email": email,
        "verificationMedium": "email"
    }

    response = requests.post(url, headers=headers, json=data)

    accvid = json.loads(response.text)["data"]["accvid"]

    # print("accvid:",accvid)

    IsCodeHere = None

    while IsCodeHere == None:   
        if GetEmails() != "[]":
            IsCodeHere = True
        time.sleep(1)

    if GetEmails() != "[]":
        email_data = GetEmails()
        pattern = re.compile(r'Aktivierungs-Code: (\d+)')

        match = pattern.search(str(email_data))
        if match:
            EmailCode = match.group(1)
        else:
            print("Account Failed -> No Code Found!")
            return None


        url = "https://account.kaufland.com/verification-srv/account/verify"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "de-DE",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Referer": "https://www.kaufland.de/",
            "Origin": "https://www.kaufland.de",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Connection": "keep-alive",
            "TE": "trailers",
            "x-cidaas-ref-number":"67cacc0e9dfd9c28:35305d6d0950eb99:67cacc0e9dfd9c28:0",
            "etag": 'W/"bc-9j1akpaClQKUYBE0vAeO31EQp+o"'

        }

        data = {
            "accvid": str(accvid),
            "code": str(EmailCode)
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print("Account Generated ->", email)
            return email


def thread_function():
    try:
        GenerateAccount()
    except:
        IDontCare = True

def main():
    threads = []
    for _ in range(AccountsToGenerate):
        thread = threading.Thread(target=thread_function)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
    
os.system("pause")
