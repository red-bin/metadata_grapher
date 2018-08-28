#!/usr/bin/python3

from selenium import webdriver
from csv import DictWriter

from time import sleep


def nav_searchpage():
    w.get("https://webapps1.cityofchicago.org/employeephonedirectory/search")
    more_options = w.find_element_by_xpath("/html/body/div[3]/form/div[2]/a")
    more_options.click()
 
def nav_dept(dept_name):
    """navigate to department page from main searchpage and change results # to 100"""
    nav_searchpage()

    sleep(.5)

    dept_dropdown = w.find_element_by_xpath('//*[@id="department"]')
    dept_elems = dept_dropdown.find_elements_by_id("department")[1:]

    sleep(.5)

    dept_elem = [ d for d in dept_elems if d.text == dept_name][0]
    dept_elem.click()

    submit_elem = w.find_element_by_xpath('//*[@id="submit"]')
    submit_elem.click()

    entry_numelem = w.find_element_by_xpath('/html/body/div[3]/form/div[6]/div/div[2]/div[1]/label/select/option[4]')
    entry_numelem.click()

def extract_table():
    """extract rows from table and parse"""
    table = w.find_element_by_xpath('/html/body/div[3]/form/div[6]/div/table/tbody')
    rows = table.find_elements_by_tag_name("tr")

    parsed_rows = [parse_row(row) for row in rows]
    return parsed_rows

def parse_row(row):
    """extract info from rows"""
    cols = row.find_elements_by_tag_name("td")
    last_name = cols[0].get_attribute('innerHTML')
    first_name = cols[1].get_attribute('innerHTML')
    phone_number = cols[2].find_elements_by_tag_name("a")[0].get_attribute('innerHTML')
    department = cols[3].get_attribute('innerHTML')
    title = cols[4].get_attribute('innerHTML')

    return dict(last_name=last_name, first_name=first_name, phone_number=phone_number, department=department, title=title)

def department_phones(dept_name):
    """navigate to each dept page and extract each page's rows"""
    nav_dept(dept_name)

    all_phones = []
    while True:
        all_phones += extract_table()
        next_button = w.find_element_by_xpath('//*[@id="resultstable_next"]')

        if 'ui-state-disabled' in next_button.get_attribute("class"):
            break

        else:
            next_button.click()

    return all_phones

w = webdriver.Firefox()

nav_searchpage()
dept_names = w.find_element_by_id("department").text.split('\n')[1:]

final_results = []

print(dept_names)
for dn in dept_names: 
    print(dn)
    final_results += department_phones(dn)

fh = open('/tmp/chicago_phones.csv','w')
fieldnames = ['last_name', 'first_name', 'phone_number', 'department', 'title']
w = DictWriter(fh, fieldnames=fieldnames)
w.writeheader()
w.writerows(final_results)
