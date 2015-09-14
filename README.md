# API for fetching pincode data from data.gov.in and location from google geocode api.

Required Software:

```
Python 2.7
MySql
```
API runs on Python with the Flask microframework. You will need to install all the requirements listed in requirements.txt using easy_install or pip:
```
$ pip install -r requirements.txt
```

Update ```db.py``` witht the connection details.
```
engine = create_engine("mysql://user:password:@localhost/dbname",
isolation_level="READ UNCOMMITTED",
convert_unicode=True)
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
