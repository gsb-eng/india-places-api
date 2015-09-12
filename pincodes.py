"""
Module to get pincode data from data.gov.in.
"""
import json
import time
import threading
import urllib2

from config import (DATA_GOV_URL as URL,
                    KEY)
from Queue import Queue, Empty


def get_url(URL, key, offset, state, limit=100):
    """
    Method to make URL based on the parameters.

    :param string URL: Base URL for the api.
    :param string key:  Key for authorizing over data.gov.in.
    :param string state: State for which pincode search is happening.
    :param integer limit: Number of records to fetch at a time, defaults to 100 records.
    """

    uri = "&offset={offset}&api-key={key}&limit={limit}&filters[statename]={state}"
    uri = uri.format(key=key,
		     limit=limit,
		     offset=offset,
		     state=state)
    if offset %100 == 0:
        print URL + uri
    return URL + uri


class PincodeCrawler(threading.Thread):

    def __init__(self, kwargs=None):
        threading.Thread.__init__(self)
        self.kwargs = kwargs
        self.stop_fetch = False

    def run(self):
        """
        Method which will be executed by each worker to fetch pincode data.         
        """

        terminate = False
        state = self.kwargs.get('state') # state for wich pincode data is processing.
        offset_queue = self.kwargs.get('offset_queue')
        out_queue = self.kwargs.get('out_queue')
        terminate_queue = self.kwargs.get('terminate_queue')

        while True:
            try:
                offset = offset_queue.get(timeout=1)
                data = json.load(urllib2.urlopen(get_url(URL, KEY, offset, state)))
                out_queue.put(data['records'])
                if not data['count']:
                    # Terminate the worker and put a signal to alert other
                    # workers to stop.
                    terminate_queue.put(1)
                    self.stop_fetch = True
                    break

                if offset_queue.empty():
                    # If offset queue is empty they stop the worker.
                    self.stop_fetch = True
                    break
                elif terminate_queue.get(timeout=0.01):
                    # If terminate signal found, stop the worker and
                    # put the same signal in the queue to stop all the other
                    # still running.
                    self.stop_fetch = True
                    terminate_queue.put(1)
                    terminate = True
                    break

            except Empty, e:
                # If there is terminate flag enabled then break the worker flow,
                # else continue the flow.
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
        """
        Method to create offset queue.

        :param integer start_from: This allows to get more offset values
            from the previously defined limit.
        """
        in_queue = Queue()
        for i in xrange(start_from, start_from + self.offset_max):
            in_queue.put(i)
        return in_queue

    def fetch_pincodes(self, out_queue, offset_queue, terminate_queue):
        """
        Method to fetch pincode data from data.gov.in.

        Over data.gov.in there are cenrtain restricions like, max fetch would be
        100 records at a time and this can be resolved by using offset.

        What we are doing here is that, starting with offset "0" we'll be sending
        offset upto 5000 ver queue, each worker pickup one offset and retrives the info
        when there is no data found for any of the offset that worker sends a terminate
        signal to other workers.

        :param object out_queue: Queue for collecting data from workers.
        :param object offseet_queue: Queue for sending offset info to workers.
        :param object terminate_queue: Queue for sending terminate signal to workers.
        """
        data = []
        worker_pool = []

        # Worker count defined in the config file.
        for i in xrange(self.max_workers):
            worker = PincodeCrawler(kwargs={'offset_queue': offset_queue,
                                            'out_queue': out_queue,
                                            'terminate_queue': terminate_queue,
                                            'state': self.state})
            worker_pool.append(worker)
            worker.start()

    def get_worker_status(self, workers):
        """
        Method to know the status of the workers whether they are alive or not.

        :param list worker: Pool of worker objects.
        """
	alive = False
	for worker in workers:
	    if not worker.stop_fetch:
	        alive = True
	return alive

