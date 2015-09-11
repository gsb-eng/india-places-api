"""
Module to get pincode data from 
"""
import urllib2
import json
import time
import threading

from Queue import Queue, Empty
from pincodes import PincodeData

KEY = "YOURKEY"

URL = "https://maps.googleapis.com/maps/api/geocode/json?address="


# A thread that pings ip.
class LocationCrawler(threading.Thread):

    def __init__(self, kwargs=None):

        threading.Thread.__init__(self)
        self.kwargs = kwargs
        self.stop_fetch = False

    def run(self):

        terminate = False
        in_queue = self.kwargs.get('in_queue')
        out_queue = self.kwargs.get('location_out_queue')
        terminate_queue = self.kwargs.get('terminate_queue')

        while True:
            try:
                data = in_queue.get(timeout=5)
                #print data
                for loc in data:
                    location_data = json.load(urllib2.urlopen(URL + loc['pincode']))
                    #print location_data
                    #break
                    location_data['results'][0]['geometry']['location']['pincode'] = loc['pincode']
                    out_queue.put(location_data['results'][0]['geometry']['location'])
                    time.sleep(0.7)

            except Empty, e:
                break
            except Exception, e:
                print e, location_data
                time.sleep(1)
                pass

    def merge_dicts(pincode, location):
        location['pincode'] = pincode['pincode']

class LocationData(PincodeData):
    '''
    Class which fetches location data from google maps api.
    '''

    def __init__(self, offset_max, max_workers, state):
        self.state = state
        self.offset_max = offset_max
        self.max_workers = max_workers
        super(LocationData, self).__init__(offset_max, max_workers, state)

    def fetch_locations(self):
        data = {}
        out_queue = Queue()
        terminate_queue = Queue()
        offset_queue = self.get_offset_queue()

        location_out_queue = Queue()

        self.fetch_pincodes(out_queue, offset_queue, terminate_queue)

        worker_pool = []

        for i in xrange(1):
            worker = LocationCrawler(kwargs={'in_queue': out_queue,
                                            'location_out_queue': location_out_queue})
            worker_pool.append(worker)
            worker.start()

        while 1:
            try:
                d = location_out_queue.get(timeout=10)
                data[d['pincode']] = d
            except Empty, e:
                break
        return data.values()

    def _fetch_locations(self):
        return
