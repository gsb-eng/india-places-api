"""
Module to get pincode data from 
"""
import urllib2
import json
import time
import threading

from Queue import Queue, Empty

KEY = "YOURKEY"

URL = "https://data.gov.in/api/datastore/resource.json&fields=pincode"
URL += "&resource_id=0a076478-3fd3-4e2c-b2d2-581876f56d77"


def get_url(URL, key, offset, state, limit=100):
    uri = "&offset={offset}&api-key={key}&limit={limit}&filters[statename]={state}"
    uri = uri.format(key=key,
		     limit=limit,
		     offset=offset,
		     state=state)
    if offset %100 == 0:
        print URL + uri
    return URL + uri

# A thread that pings ip.
class PincodeCrawler(threading.Thread):

    def __init__(self, kwargs=None):
        threading.Thread.__init__(self)
        self.kwargs = kwargs
        self.stop_fetch = False

    def run(self):

        terminate = False
        state = self.kwargs.get('state')
        offset_queue = self.kwargs.get('offset_queue')
        out_queue = self.kwargs.get('out_queue')
        terminate_queue = self.kwargs.get('terminate_queue')

        while True:
            try:
                offset = offset_queue.get(timeout=1)
                data = json.load(urllib2.urlopen(get_url(URL, KEY, offset, state)))
                out_queue.put(data['records'])
                if not data['count']:
                    terminate_queue.put(1)
                    self.stop_fetch = True
                    break

                if offset_queue.empty():
                    self.stop_fetch = True
                    break
                elif terminate_queue.get(timeout=0.01):
                    self.stop_fetch = True
                    terminate_queue.put(1)
                    terminate = True
                    break

            except Empty, e:
                if terminate: break
                pass

            except Exception, e:
                self.stop_fetch = True
                print str(e)

class PincodeData(object):
    '''
    Class which fetches pincode data from data.gov.in api.
    '''

    def __init__(self, offset_max, max_workers, state):
        self.state = state
        self.offset_max = offset_max
        self.max_workers = max_workers

    def get_offset_queue(self, start_from=0):
        in_queue = Queue()
        for i in xrange(start_from, start_from + self.offset_max):
            in_queue.put(i)
        return in_queue

    def fetch_pincodes(self, out_queue, offset_queue, terminate_queue):
        data = []
        worker_pool = []

        for i in xrange(self.max_workers):
            worker = PincodeCrawler(kwargs={'offset_queue': offset_queue,
                                            'out_queue': out_queue,
                                            'terminate_queue': terminate_queue,
                                            'state': self.state})
            worker_pool.append(worker)
            worker.start()

    def get_worker_status(self, workers):
	alive = False
	for worker in workers:
	    if not worker.stop_fetch:
	        alive = True
	return alive

