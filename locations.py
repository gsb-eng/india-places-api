"""
Module to get location data from google geocode api. 
"""
import urllib2
import json
import time
import threading

from config import (GOOGLE_GEOCODE_URL as URL,
                    KEY)
from Queue import Queue, Empty
from pincodes import PincodeData


class LocationCrawler(threading.Thread):
    """
    Thread generator to fetch location from google geocode api.
    """
    def __init__(self, kwargs=None):

        threading.Thread.__init__(self)
        self.kwargs = kwargs
        self.stop_fetch = False
        self.err_count = 0

    def run(self):
        """
        
        """
        terminate = False
        in_queue = self.kwargs.get('in_queue')
        out_queue = self.kwargs.get('location_out_queue')

        while True:
            try:
                # Wait for maximum of 5 seconds for data over queue.
                data = in_queue.get(timeout=5)
                for loc in data:
                    location_data = json.load(urllib2.urlopen(URL + loc['pincode']))
                    location_data['results'][0]['geometry']['location']['pincode'] = loc['pincode']
                    out_queue.put(location_data['results'][0]['geometry']['location'])
                    time.sleep(1)

            except Empty, e:
                # Queue is empty means, cenrtainly there is no data comingup
                # in the queue to process
                break
            except Exception, e:
                # If any issues with the gecode api wait for 50 times and break.
                if self.err_count > 50: break
                self.err_count += 1

    def merge_dicts(pincode, location):
        location['pincode'] = pincode['pincode']

class LocationData(PincodeData):
    '''
    Class which fetches location data from google maps api.
    '''

    def __init__(self, offset_max, max_workers, state):
        self.state = state
        self.offset_max = offset_max
        self.max_workers = max_workers # max workers for fetcing pincodes.
        super(LocationData, self).__init__(offset_max, max_workers, state)

    def fetch_locations(self):
        data = {}
        out_queue = Queue() # Queue to capture the worker prcessed pincode data.
        terminate_queue = Queue() # To send terminate signal to workers.
        offset_queue = self.get_offset_queue() # To make offset logic thread safe.

        location_out_queue = Queue()

        # Pincode fetch workers kepps sending retrived data over the queues
        # which ontern processed by location workers in parallel.
        self.fetch_pincodes(out_queue, offset_queue, terminate_queue)

        worker_pool = []

        # Hardcoding workers here to maintain sync between threads to make
        # sure efficient use of gecode api.
        # 10 workers because gecode api allows 10 requests per second, so each
        # and goes to sleep for 1 second.
        for i in xrange(10):
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
