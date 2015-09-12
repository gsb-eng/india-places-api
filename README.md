# API for fetching pincode data from data.gov.in and location from google geocode api.

API runs on Python with the Flask microframework. You will need to install all the requirements listed in requirements.txt using easy_install or pip:
```
$ pip install -r requirements.txt
```
Next, create the tables by running the below cmman:
```
$ python create_tables.py
```
Next update the ```config.py``` witht the KEY for more info check this  [data.gov.in](https://data.gov.in/resources/all-india-pincode-directory-along-contact-details/api).
To run the server in development mode:
```
$ python app.py
```
