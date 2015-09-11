"""
Config file for india places api.
"""
# data.gov.in key for autherization.
KEY = "YOUR KEY"

# max offset count.
MAX_OFFSET = 5000
MAX_WORKERS = 10

GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json?address="
DATA_GOV_URL = "https://data.gov.in/api/datastore/resource.json&fields=pincode"
DATA_GOV_URL += "&resource_id=0a076478-3fd3-4e2c-b2d2-581876f56d77"

