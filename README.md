# Studentweb-scraper
This is a Python script used to check for updated grades on Studentweb and send the results to your email. The email also adds a screenshot of the results table to the email. The scripts also has support for partial grades, where you receive one or two grades before the final one. 

**Instructions:**

1.  Set up a gmail address with the "Allow less secure apps" set to ON. I suggest a new email for this purpose.
2.  Then edit the config file with login and email information
    * ssn = Your social security number
    * pin = The 4 digit pincode for login into studentweb
    * from_mail = The gmail you created for sending the emails
    * password = The password for this email
    * to_mail = The email you want to receive updates on
3.  Schedule the script to run periodically with crontab

**Dependencies:**

* Chromedriver in your python/Scripts folder or in PATH variable

* selenium

* beautifulsoup4

I recommend using Pipenv or similar tools to manage dependencies. Pipfiles are included in repo.

