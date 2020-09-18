#!/usr/bin/env python3

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import ipdb
import requests
import time
import random
import sys
import configparser


config = configparser.ConfigParser()
config.read('my.ini')
username  = config['DEFAULT'].get('studentid')
password  = config['DEFAULT'].get('password')
ftposturl = config['DEFAULT'].get('ftposturl')
selenium_server = config['DEFAULT'].get('seleniumserver')

FUDANDAILYURL = 'https://zlapp.fudan.edu.cn/site/ncov/fudanDaily'

#ipdb.set_trace()

def notify(content):
    content = content.replace(' ', '_')
    notify_str = '{}text={}。'.format(ftposturl, content)
    print('push notification raw data = {}'.format(notify_str))
    requests.get(notify_str)


if len(sys.argv) == 2:
    time.sleep(random.randint(10,3600))

# check in 
firefox_options = webdriver.FirefoxOptions()
driver = webdriver.Remote(
    command_executor= selenium_server,
    options=firefox_options
)
wait = WebDriverWait(driver, 10)
driver.get(FUDANDAILYURL)

# login, input the forms
wait.until(EC.title_is('复旦大学统一身份认证'))
username_elem = driver.find_element_by_name("username")
username_elem.clear()
username_elem.send_keys(username)
username_elem.send_keys(Keys.RETURN)
pwd_elem = driver.find_element_by_name("password")
pwd_elem.clear()
pwd_elem.send_keys(password)
pwd_elem.send_keys(Keys.RETURN)


# login success, then redirect 
wait.until(EC.url_matches(FUDANDAILYURL))
time.sleep(10)
try:
    # first time(not checkin yet), will promt an alarm dialog
    ok_button = driver.find_element_by_css_selector(".wapat-btn")
    ok_button.click()

    # click location form
    loc_input_elem = driver.find_element_by_css_selector(".form > ul:nth-child(1) > li:nth-child(6) > div:nth-child(1) > input:nth-child(2)")
    loc_input_elem.click()

    time.sleep(15)
    submit_button = driver.find_element_by_css_selector(".footers > a:nth-child(1)")

    submit_button.click()

    final_submit_button = driver.find_element_by_css_selector("div.wapcf-btn:nth-child(2)")
    final_submit_button.click()
    time.sleep(10)
except Exception as e:
    notification_string = '尝试打卡失败啦，呜呜呜'
    print(notification_string)
    notify(notification_string)


try:
    # check finish
    driver.get(FUDANDAILYURL)
    wait.until(EC.url_matches(FUDANDAILYURL))

    location = driver.find_element_by_css_selector("body > div.item-buydate.form-detail2.ncov-page > div > div.form-detail.form-detail2.item-buydate > section > div.form.fudanform > ul > li:nth-child(6) > div > input[type=text]")
    time.sleep(20)
    current_location = location.get_attribute('value')

    notification_string = '打卡成功 地点为 {}'.format(current_location)
    print(notification_string)
    notify(notification_string)
except Exception as e:
    notification_string = '问题很大，为啥检查失败了'
    print(notification_string)
    notify(notification_string)
finally:
    driver.close()
    exit(0)


#finally:
#    driver.close()
