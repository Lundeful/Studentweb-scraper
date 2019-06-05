from selenium import webdriver # For accessing studentweb
from selenium.webdriver.chrome.options import Options # For accessing studentweb
from bs4 import BeautifulSoup as bs # For parsing the studentweb results
from result import Result # storing results as objects
import configparser # For reading the config-file
import time # For sleeping
import pickle # For saving and loading results
import smtplib # For emailing
from email.message import EmailMessage # For emailing
import random # Used to randomize results for testing. Can be removed

"""This is a script that checks for new grades on StudentWeb and emails the
results back to you. Mainly created for OsloMet students, but small changes
may allow fetching from other institutions as well.

Instructions:
1.  Set up a gmail address with "Allow less secure apps" set to ON.
    I suggest a new email for this purpose.

2.  Then edit the config file with login and email information
    ssn = Your social security number
    pin = The 4 digit pincode for login into studentweb
    from_mail = The gmail you created for sending the emails
    password = The password for this email
    to_mail = The email you want to receive updates on

Note: This only works with the "Norwegian Bokmål" version of Studentweb for now.
If there is any errors check config file for mistakes or change sleep times
to higher numbers to wait for the browser to load completely."""

print("// Running Studentweb script")
print("// Reading config file")
# Read config file
config = configparser.ConfigParser()
config.read('config.cfg')
ssn = config['DEFAULT']['ssn']
pin = config['DEFAULT']['pin']
from_mail = config['DEFAULT']['from_mail']
password = config['DEFAULT']['password']
to_mail = config['DEFAULT']['to_mail']

print("// Checking for previous results")
# Load previous results for comparing
try:
    with open('results.dat', 'rb') as f:
        previous_results = pickle.load(f)
        print("// Previous results found")
        compare_results = True

        # Randomise a few results for testing. These three lines can be removed
        # random.choice(previous_results).grade = 'F'
        # random.choice(previous_results).grade = 'E'
        # previous_results.remove(random.choice(previous_results))

except FileNotFoundError:
    print("// Previous results not found. Will create new file with results")
    compare_results = False

##########################
#### Access studentweb ###
##########################

# Emulate mobile browser for easier navigation of website
mobile_emulation = {
    "deviceMetrics": { "width": 720, "height": 900, "pixelRatio": 3.0 },
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"
    }

# Chrome driver
chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
chrome_options.add_argument("--headless") # Headless mode / runs in background
driver = webdriver.Chrome(options = chrome_options)
driver.implicitly_wait(5) # Waits up to 5 seconds in case operations takes time

# Load the login website
print("// Loading login site")
driver.get('https://fsweb.no/studentweb/login.jsf?inst=FSHIOA#')

# Find and fill in username
username_box = driver.find_element_by_xpath( "//*[contains(@id, 'fodselsnummer')]" )

print("// Entering username")
username_box.send_keys(ssn)

# Find and fill in PIN
pin_box = driver.find_element_by_xpath( "//*[contains(@id, 'pincode')]" )

print("// Entering PIN")
pin_box.send_keys(pin)
time.sleep(1)

# Log in
print("// Logging in")
driver.find_element_by_xpath( "//*[contains(@id, ':login')]").click()
time.sleep(1) # Let new elements load

# Get results page
print("// Loading results page")
driver.get('https://fsweb.no/studentweb/resultater.jsf')
driver.refresh()
time.sleep(1) # Load page before clicking radio button to change results view
driver.find_element_by_xpath( "//*[contains(@id, 'resultatlisteForm:j_idt154:1')]").click()
time.sleep(1) # Wait and click again to ensure it loads correctly
driver.find_element_by_xpath( "//*[contains(@id, 'resultatlisteForm:j_idt154:1')]").click()
time.sleep(1) # Let the new elements load

# Scrape results using BeautifulSoup
print("// Scraping results")
html = bs(driver.page_source, 'html.parser')
driver.quit() # Closes all browser windows and safely ends the session

table_id = "resultatlisteForm:HeleResultater:resultaterPanel"
# Load table with results
table = html.find('table', { "id" : table_id }).find('tbody')

# Get each result as a row
rows = table.find_all('tr', recursive=False)

# List to store results
results = []

# Loop through and store results
for row in rows:
    # Skip rows which are not relevant
    if row['class'][0] == "resultat":
        continue

    # Load cells with information about a result
    cells = row.find_all('td')

    # Get result information
    semester = cells[0].get_text().split('\n')[3].strip()
    course = cells[1].find_all('div', { "class" : "infoLinje"})
    code = course[0].get_text().strip()
    name = course[1].get_text().strip()
    grade = cells[5].find('div', { "class" : "infoLinje"}).get_text().strip()

    # Check if grade exist or
    if grade != "Godkjent":
        # Create new result object
        result = Result(semester, name, code, grade)
        # Add result to list
        results.append(result)

print("// Scraping complete ")

################################
#### Compare and log results ###
################################

# List of new results to be sent to user via email
notification_list = []

# If previous results exist, compare with new ones
if compare_results:
    print("// Comparing results ")

    # Loop through results for comparison
    for result in results:
        new_course = True  # Used to see if previous grade is registered or not
        for prev in previous_results:
            if result.code == prev.code:
                new_course = False # Previous grade is resistered
                if result.grade != prev.grade:
                    print("// Change in grade for " + result.name + " found")
                    notification_list.append([prev, result]) # Add to list for notification
                continue

        if new_course:
            print("// New course grade found for " + result.name)
            notification_list.append([result]) # Add to list for notification

    print("// Comparison complete")

if len(notification_list) == 0:
    print("// No changes in results found")
elif len(notification_list) > 0:
    print("// Sending email with changes")
    content = ""
    for new_result in notification_list:
        if len(new_result) > 1: # Show both previous and new grade
            content += "\nChange in grade registered\n"
            content += "\nPrevious grade:\n"
            content += str(new_result[0])
            content += "\n\nChanged grade:\n"
            content += str(new_result[1])
            content += "\n"
        else: # No previous grade
            content += "\nNew grade registered\n\n"
            content += str(new_result[0])
            content += "\n"

    # Login and send email with new grades
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(from_mail, password)
    server.sendmail(from_mail, to_mail, content.encode('utf-8'))


# Save results to file
print("// Saving new results to file")
try:
    with open('results.dat', 'wb+') as f:
        pickle.dump(results, f)
except Exception:
    pass

print("// Script finished")
