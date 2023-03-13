import inspect
import requests
import socks
import socket
import os

from bs4 import BeautifulSoup


def get_file_dir():
    filename = inspect.getframeinfo(inspect.currentframe()).filename
    path = os.path.dirname(os.path.abspath(filename))
    return path


def connect_to_tor():
    print("Connecting to Tor")
    print("Before:")
    check_ip()

    socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
    socket.socket = socks.socksocket

    print("After:")
    check_ip()


def check_ip():
    ip = requests.get('http://checkip.dyndns.org').content
    soup = BeautifulSoup(ip, 'html.parser')

    print(soup.find('body').text)


def execute_captcha(page):
    try:
        page.locator("input[class=CheckboxCaptcha-Button]").click(timeout=2000)
        print("Enter the captcha text:")
        captcha_text = input()
        page.locator("input[class=Textinput-Control]").input_value(captcha_text)
        page.locator("button[class=CaptchaButton CaptchaButton_view_action]").click()
    except:
        None
