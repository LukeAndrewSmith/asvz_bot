#!/user/bin/env python

"""
Created on: Oct 27, 2020
Author: Luke Smith
License: BSD 3-Clause
Description: Script for automatic enrollment in ASVZ classes on Schalter page
"""
"""
A little change of the bot by jstiefel https://github.com/jstiefel/asvz_bot
The change was to avoid the case where there are several events at the same
time but with different levels (beginner, advanced, etc...), the original
bot didn't identify the level.
NOTE:
This could also be implemented in the original bot by including an extra
variable that identifies the level and by finding this level in the html.
You'd have to be careful of the language.
"""

############################# Edit this: ######################################

# ETH credentials:
username = 'xxx'
password = 'xxx'
lesson_time = '19:15'
enrollment_time_difference = 24 # how many hours before registration starts
# link directly to enrollment
schalter_page = 'https://schalter.asvz.ch/tn/lessons/141573'

###############################################################################

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def waiting_fct():
    # if script is started before registration time. Does only work if script is executed on day before event.
    currentTime = datetime.today()
    enrollmentTime = datetime.strptime(lesson_time, '%H:%M')
    enrollmentTime = enrollmentTime.replace(hour=enrollmentTime.hour + (24-enrollment_time_difference))

    while currentTime.hour < enrollmentTime.hour:
        print("Wait for enrollment to open")
        time.sleep(60)
        currentTime = datetime.today()

    if currentTime.hour == enrollmentTime.hour:
        while currentTime.minute < enrollmentTime.minute-1:
            print("Wait for enrollment to open")
            time.sleep(30)
            currentTime = datetime.today()

    return


def asvz_enroll():
    options = Options()
    options.headless = True
    options.add_argument("--private") # open in private mode to avoid different login scenario
    driver = webdriver.Firefox(options = options)

    try:
        driver.get(schalter_page)
        driver.implicitly_wait(20) # wait 20 seconds if not defined differently
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-default ng-star-inserted' and @title='Login']"))).click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='btn btn-warning btn-block' and @title='SwitchAai Account Login']"))).click()

        # choose organization:
        organization = driver.find_element_by_xpath("//input[@id='userIdPSelection_iddtext']")
        organization.send_keys('ETH Zurich')
        organization.send_keys(u'\ue006')

        driver.find_element_by_xpath("//input[@id='username']").send_keys(username)
        driver.find_element_by_xpath("//input[@id='password']").send_keys(password)
        driver.find_element_by_xpath("//button[@type='submit']").click()

        # wait for button to be clickable for 5 minutes, which is more than enough
        # still needs to be tested what happens if we are on the page before button is enabled
        WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='btnRegister' and @class='btn-primary btn enrollmentPlacePadding ng-star-inserted']"))).click()
        print("Successfully enrolled. Train hard and have fun!")
    except: # using non-specific exceptions, since there are different exceptions possible: timeout, element not found because not loaded, etc.
        driver.quit()
        raise #re-raise previous exception

    driver.quit # close all tabs and window
    return True

# run enrollment script:
i = 0 # count
success = False

waiting_fct()

# if there is an exception (no registration possible), enrollment is tried again in total 5 times and then stopped to avoid a lock-out
while not success:
    try:
        success = asvz_enroll()
        print("Script successfully finished")
    except:
        if i<4:
            i += 1
            print("Enrollment failed. Start try number {}".format(i+1))
            pass
        else:
            raise
