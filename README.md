# PET HEALTH MONITOR
#### Video Demo:  https://youtu.be/FH3PCliw7u8
#### Description:
Final project for CS50's Introduction to Computer Science.

Web application PET HEALTH MONITOR helps to keep track of your pets' vaccinations and other regular treatments, as well as to record pets' medical history and to plan visits to vet clinic. Having all records and medical tests results at one place maybe helpful for more precise diagnosis and better treatment especially if you change your vet clinic or veterinarian.

## Architecture
#### Frontend
Languages:
* HTML
* CSS
  
Main Framework/Libraries:
* Bootstrap 5

#### Backend
Languages:
* Python 3
  
Main Framework/Libraries:
* Flask
  
#### Database
* SQLite3

## Content
Web application has the next sections:
* **main page** (displays upcoming and recent events; deadline notifications)
* **add a pet** (type, name, date of birth)
* **my pets**
* **add vaccinations and treatments** (regular vaccinations and regular treatments like deworming and flee or tick treatment)
* **vaccinations and treatments**
* **add medical tests** (blood tests, biochemistry profile, urinanalysis, ultrasound etc.)
* **medical tests**
* **add visits to vet**
* **visits to vet**

To add or view information user must be logged in.


## Features
Web application allows to:
* add any number of pets, remove pets, edit pets;
* add, remove and edit information about regular vaccinations and treatments (including name of vaccine or drug, date of procedure, expiration date);
* add, remove and edit information about medical tests (including reason for, comments, date of test, date of re-test);
* add files with results of medical tests (application accepts .pdf, .png, .jpg, .jpeg; to avoid filenames conflict, filenames are modified so that the number of already uploaded files is added to a filename);
* add, remove and edit information about visits to vet clinic (including name of clinic, veterinarian, reason for, diagnosis, treatment, comments, date of a visit, date for the next visit).
#### Other features:
* if a required field in any form is missing, error message flashes;
* if expiration dates and dates of re-examinations are not specified by user they are calculated automatically based on standard practice (like a year for vaccination or 3 months for deworming treatment);
* information in tables is displayed chronologically (in descending or ascending order, depending on purpose) and - except for main page where chronology is more important - is ordered by pet;
* main page displays all upcoming events (starting from a day after the current date, organized into categories: regular procedures, medical tests, visits to vet clinic) and last events (3 in every category);
* main page also flashes notification if user possibly missed deadline for regular treatments or medical tests (user is supposed to check it manually and either to extend current deadline, or to add missing information, or to take the necessary action);
* if there is no information to display, welcome (instructional) message is displayed with redirect to a relevant page (e.g. "you have no pets yet, start from adding a pet").


## Contact
Anzhalika Dubasava, anzhalikad@gmail.com

Linkedin: https://www.linkedin.com/in/adubasava/