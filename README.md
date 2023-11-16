# Automated Mail Project

Developed a simple .py file that executed once in a day for checking is there any friends, family members and etc. have birthday today/tomorrow. If there is/are, sending mail to myself. Using SMTP Protocol library to send mails and connecting MySQl to retrieve birthday data. It is significant to remind that keys of MySQL database & SMTP are stored in a local json file and did not commit with .py file. However, the code is executed on my local and read these json files as well. The .py file is triggered for 9 AM every day of week via *crontab* on MacOS.
