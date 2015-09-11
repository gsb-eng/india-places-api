from collections import OrderedDict

from db import db_session, engine
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
            data = self.get_data_from_db(state)
        else:
            loc_data = LocationData(offset_max=1, max_workers=1, state=state)
            data = self.save_pincode_data(loc_data.fetch_locations(), state)
        return self.mark_directions(data, state)

    def get_data_from_db(self, state):
        return db_session.query(Pincodes).join(States).filter(States.name==state).all()


    def check_state_exist(self, state):
        state = db_session.query(States).filter(States.name==state).all()
        return state

    def save_pincode_data(self, data, state):
        self.save_state(state)
        state_id = self.get_state_id(state).id
 
        pincode_objects = self.__bind_to_pincode(data, state_id)
        db_session.add_all(pincode_objects)
        db_session.commit()
        return pincode_objects


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

    def get_center_lat_lng(self, state):
        query = """
            SELECT 
                180 * atan2(s.zeta, s.xi) / pi() AS avg_lon,
                s.avg_lon_naive AS avg_lon_naive,
                s.avg_lat AS avg_lat
            FROM (
                SELECT 
                    avg(sin(pi() * longitude / 180)) AS zeta, 
                    avg(cos(pi() * longitude / 180)) AS xi,
                    avg(longitude) AS avg_lon_naive,
                    avg(latitude) AS avg_lat
                FROM pincodes AS pin
                JOIN states AS sta
                    ON sta.id = pin.state_id AND sta.name='%s'
            ) AS s
        """
        data = engine.execute(query%state).first()
        return data['avg_lat'], data['avg_lon']

    def mark_directions(self, data, state):
        north_pincodes, south_pincodes, east_pincodes, west_pincodes = [], [], [], []

        ref_lat, ref_lng = self.get_center_lat_lng(state)
        reference_point = "{lat},{lng}".format(lat=ref_lat, lng=ref_lng)

        total = 0
        for row in data:
            total += 1
            if row.latitude > ref_lat:
                north_pincodes.append(str(row.pincode))
            else:
                south_pincodes.append(str(row.pincode))

            if row.longitude > ref_lng:
                east_pincodes.append(str(row.pincode))
            else:
                west_pincodes.append(str(row.pincode))


        return OrderedDict([
            ('state', state),
            ('reference_point', reference_point),
            ('total_pincodes', total),
            ('north_pincodes', north_pincodes),
            ('south_pincodes', south_pincodes),
            ('east_pincodes', east_pincodes),
            ('west_pincodes', west_pincodes)])

