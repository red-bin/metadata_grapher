#!/usr/bin/python3

from selenium import webdriver
from time import sleep
from host import environ

from urllib.parse import urlparse

import re

from requests import get

def auth_creds():
    fh = open('%s/.seattle_creds.txt' % environ['HOME'], 'r')
    lines = ( l.strip() for l in fh.readlines() )

    return lines 

driver = webdriver.Chrome()

url = "http://www.seattle.gov/public-records/public-records-request-center"

driver.get(url)

next_page = driver.find_element_by_link_text("Go to Public Records Request Center")
next_page.click()

sleep(5)

driver.switch_to_window(driver.window_handles[1])

next_page = driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/form/div[2]/div[7]/div/div[3]/div[2]/p/h600")
next_page.click()

next_page = driver.find_element_by_xpath('//*[@id="lnkMyIssues"]')
next_page.click()

email_field = driver.find_element_by_xpath('//*[@id="ASPxFormLayout1_txtUsername_I"]')
pass_field = driver.find_element_by_xpath('//*[@id="ASPxFormLayout1_txtPassword_I"]')

creds = auth_creds()
email_field.send_keys(auth_creds.__next__())
pass_field.send_keys(auth_creds.__next__())

submit = driver.find_element_by_xpath('//*[@id="ASPxFormLayout1_btnLogin"]')

submit.click()

view_files = driver.find_element_by_xpath('//*[@id="roundPanel_issuesListView_ctrl0_btnViewFiles_BTC"]')
view_files.click()

file_divs = driver.find_elements_by_class_name("qac_attachment")

s3_urls = []
for file_div in file_divs:
    input_divs = file_div.find_elements_by_tag_name("input")

    if input_divs:
        s3_url = input_divs[1].get_attribute("value")
        s3_urls.append(s3_url)

download_path = '/opt/data/foia/seattle_emails'
for url in s3_urls:
    resp = get(url)

    filename = re.split('(.*filename...|&)', url)[2]

    write_path = "%s/%s" % (download_path, filename)
    fh = open(write_path, 'wb')
    fh.write(resp.content)
    fh.close()
