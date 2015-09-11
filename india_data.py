from db import db_session
from locations import LocationData
from models import States, Pincodes


class IndiaData(object):
    '''
    Class to fetch india data.
    '''
    def __init__(self):
        pass

    def pincode_data(self, state):
        if self.get_state_id(state):
            return self.get_data_from_db(state)
        else:
            loc_data = LocationData(offset_max=1, max_workers=1, state=state)
            self.save_pincode_data(loc_data.fetch_locations(), state)
        return 1

    def check_state_exist(self, state):
        state = db_session.query(States).filter(States.name==state).all()
        return state

    def save_pincode_data(self, data, state):
        self.save_state(state)
        state_id = self.get_state_id(state).id
        db_session.add_all(self.__bind_to_pincode(data, state_id))
        db_session.commit()


    def __bind_to_pincode(self, data, state_id):
        pincodes = []
        for val in data:
            pincodes.append(Pincodes(pincode=int(val['pincode']),
                                     state_id=state_id,
                                     latitude=float(val['lat']),
                                     longitude=float(val['lng'])))
        return pincodes

    def save_state(self, state):
        db_session.add(States(name=state, latlongs=1, pincodes=1))
        db_session.commit()

    def get_state_id(self, state):
        state = db_session.query(States).filter(States.name==state).all()
        if state:
            return state[0]

ind = IndiaData()
ind.pincode_data('DELHI')
#ind.save_state('DELHI')
#print ind.get_state_id('DELHI')

