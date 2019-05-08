import os
import requests
from selenium import webdriver
import selenium as se
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from threading import Thread

import time
from time import sleep
from random import randint
from decimal import Decimal

import datetime
from datetime import datetime

message_sent = []

class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.section_list = []

    def get_course_name(self):
        return self.course_name

    def add_section(self, section):
        self.section_list.append(section)


def login(username, password):
    print(username)
    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
        username_input.send_keys(username)
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        password_input.send_keys(password)
        sendd = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/form/div[4]/button')))
        sendd.click()
        # waits until authentification is finished
        while(driver.current_url != 'https://app.testudo.umd.edu/#/main/dropAdd?null'):
            sleep(1)
    except:
        return -1


def get_term(user_term):
    try:
        table = driver.find_element(
            By.XPATH, '//*[@id="mainContent"]/div[2]/div/div[1]/div/div[2]')
        list_terms = table.find_elements(By.CLASS_NAME, "ng-binding")
        counter = 1
        for term in list_terms:
            if user_term == term.text:
                term_xpath = '//*[@id="mainContent"]/div[2]/div/div[1]/div/div[2]/button[' + str(
                    counter) + "]"
                fall = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, term_xpath)))
                fall.click()
            counter += 1
    except:
        return -1


def sign_out_error():
    got_error = True
    while(got_error == True):
        try:
            error = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="mainContent"]/div[2]/button')))
            error.click()
        except:
            got_error = False


def submit_course_by_name(courseName):
    try:
        course = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="crs_pending"]/td[2]/input')))
        course.send_keys(courseName)
        sleep(1)
        submit = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="submit_changes"]')))
        submit.click()
    except:
        driver.refresh
        sleep(2)
        try:
            get_term("Fall 2019")
        except:
            return -1
        return -1

def get_section_data(course):
    sleep(randint(10, 15))
    try:
        table_id = driver.find_element(
            By.XPATH, '//*[@id="drop_add_form"]/table/tbody/tr[6]/td/div/div[2]/table/tbody')
    except:
        return -1
    # get all of the rows in the table
    rows = table_id.find_elements(By.TAG_NAME, "tr")
    course_index = get_course_index(course)
    for row in rows:
        # Get the columns (all the column 2)
        # note: index start from 0, 1 is col 2
        section = row.find_elements(By.TAG_NAME, "td")[1]
        # note: index start from 0, 1 is col 2
        seats = row.find_elements(By.TAG_NAME, "td")[2]
       
        if(section.text in course_list[course_index].section_list):
            if("status on "+course+" "+ section.text+" numSeates: "+ seats.text not in message_sent):
                post_params = {'bot_id': 'enter-bot_id',
                    'text': "status on "+course+" "+ section.text+" numSeates: "+ seats.text}
                requests.post('https://api.groupme.com/v3/bots/post', params=post_params)
                message_sent.append("status on "+course+" "+ section.text+" numSeates: "+ seats.text)

    cancel = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="drop_add_form"]/table/tbody/tr[6]/td/div/div[3]/button[2]')))
    cancel.click()
    sleep(randint(3, 5))


def get_course_index(course):
    curr_counter = 0
    index_of_course = -1
    for curr_course in course_list:
        if(course.lower() == curr_course.course_name.lower()):
            index_of_course = curr_counter
        curr_counter += 1
    return index_of_course

def is_Testudo_on():
    weekno = datetime.today().weekday()
    date_time = str(datetime.now())
    space_index = date_time.find(" ")
    time = date_time[space_index:]
    # this is the current hour
    current_hour = time[1:3]

    is_weekend = False
    is_on_time = False
    # checks for 7-11 hours
    if(int(current_hour) > 6 and int(current_hour) < 23):
        is_on_time = True
    else:
        is_on_time = False
    # check for weekends
    if weekno<5:
        is_weekend = True
    else:
        is_weekend = False
    # check both vars and returns
    if(is_weekend and is_on_time):
        return True
    else:
        return False

w, h = 8, 5
course_list = []
course_num = 0
first_course_in = False


def main():
    #goes on testudo for add or drop classes
    if(driver.current_url != 'https://app.testudo.umd.edu/#/main/dropAdd?null&termId=201908'):
        url = "https://app.testudo.umd.edu/main/dropAdd"
        driver.get(url)
        sleep(1)
        # print(driver.current_url)
        # new_url = driver.current_url

        # starts group me thread
        t = Thread(target=get_messages)
        t.start()

        username = "enter-username"
        password = "enter-password"
        login(username, password)
        sleep(1)
        get_term("Fall 2019")
        sleep(1)
        sign_out_error()

    if (first_course_in == True):
        while(is_Testudo_on()):
            for course in course_list:
                submit_course_by_name(course.course_name)
                sleep(1)
                get_section_data(course.course_name)
    
def get_messages():
    global course_list
    global course_num
    global first_course_in
    post_params = {'bot_id': 'enter-bot_id',
                        'text': "added new course"}
    requests.post('https://api.groupme.com/v3/bots/post', params=post_params)
    # if section not open, continuously check
    last_message = ""
    remove_mes = "remove"
    while True:
        request_params = {'token': 'enter-your_requestparam_token'}
        request_params['limit'] = 1
        response_messages = requests.get(
            'https://api.groupme.com/v3/groups/enter-yourgroup_id/messages', params=request_params).json()['response']['messages']
        for message in response_messages:
            if(message['user_id'] == 'enter-youruser_id' and message['text'] != last_message):
                # list function
                if(message['text'].lower() == "list"):
                    break
                if(remove_mes in message['text'].lower()):

                    print(message['text'])
                    last_message = message['text']
                    sleep(1)
                    break
                print(message['text'])
                last_message = message['text']
                index_of_space = message['text'].find(" ")
                # accepts new course
                new_course = message['text'][0:index_of_space]
                new_section_num = message['text'][index_of_space +
                                                  1: len(message['text'])]
                got_new = False
                if(get_course_index(new_course) == -1):
                    got_new = True

                # if this is a new course
                if (got_new == True):
                    print("creating new course")
                    # this is where we add a new course
                    course_list.append(Course(new_course.lower()))
                    course_index = get_course_index(new_course)
                    course_list[course_index].section_list.append(
                        new_section_num)
                    course_num += 1
                    first_course_in = True
                    post_params = {'bot_id': 'enter-bot_id',
                        'text': "added new course"}
                    requests.post('https://api.groupme.com/v3/bots/post', params=post_params)
                # adds section to this list
                if (got_new == False):
                    print("adding section to course")
                    course_index = get_course_index(new_course)
                    course_list[course_index].section_list.append(
                        new_section_num)
                    print("added",course_list[course_index].section_list[1] )
                    post_params = {'bot_id': 'enter-bot_id',
                        'text': "added new section"}
                    requests.post('https://api.groupme.com/v3/bots/post', params=post_params)

if __name__ == '__main__':
    options = se.webdriver.ChromeOptions()

    # chrome is set to headless
    options.add_argument('headless')

    driver = se.webdriver.Chrome(chrome_options=options)

    print(is_Testudo_on())
    while(True):
        if(is_Testudo_on()):
            main()
        if(is_Testudo_on() == False):
            # print("sleeping")
            sleep(100)

