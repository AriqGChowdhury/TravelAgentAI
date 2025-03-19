import os
from dotenv import load_dotenv, find_dotenv, set_key
import requests
import sys
import json


load_dotenv()
# app = Flask(__name__)

class Hotel:

    def __init__(self):
        self.headers = {
            "x-rapidapi-key": "a7c8bee607msha31b012731c92aap15e779jsna543d630309f",
            "x-rapidapi-host": "hotels-com-provider.p.rapidapi.com"
        }
        self.region_response = None
        self.iata = None

    def get_region(self, city, num):
        url = "https://hotels-com-provider.p.rapidapi.com/v2/regions"
        params = {
            "query": city,
            "domain":"US",
            "locale":"es_US"
        }

        info = requests.get(url, headers=self.headers, params=params).json()['data'][num]
        self.region_response = info['gaiaId']
        try:
            iata_info = json.loads(info['hierarchyInfo']['airport'].replace("'", '"'))
        except:
            try:
                iata_info = json.loads(info['hierarchyInfo']['airport'])
            except:
                iata_info = info['hierarchyInfo']['airport']
        self.iata = iata_info['airportCode']
        

        return self.region_response

    def get_hotels(self, params_dict):
        url = "https://hotels-com-provider.p.rapidapi.com/v3/hotels/search"

        params = {
            "checkout_date": params_dict['checkout_date'], #required
            "price_min":"10",
            "available_filter":"SHOW_AVAILABLE_ONLY",
            "amenities": params_dict['amenities'],
            "price_max": params_dict['price_max'],
            "adults_number": params_dict['adults_number'], #required
            "checkin_date": params_dict['checkin_date'], #required
            "page_number":"1",
            "region_id": self.region_response, #required
            "star_rating_ids": params_dict['star_rating_ids'],
            "sort_order": params_dict['sort_order'], #required
            "locale":"en_US",
            "domain":"US",
            "lodging_type":"HOTEL"
        }

        if params['star_rating_ids'] == '':
            del params['star_rating_ids']
        if params['price_max'] == '':
            del params['price_max']
        if params['amenities'] == '':
            del params['amenities']
        if params['sort_order'] == '':
            params['sort_order'] = "REVIEW"

        response = requests.get(url, headers=self.headers, params=params)

        
        hotel_stats = response.json()
        
        hotel_info = []
        if "detail" in hotel_stats.keys():
            print("Experiencing issues please try again in 10 minutes")
            sys.exit()

        try:
            iteration_amt = len(hotel_stats['data']['properties'])
        except:
            
            iteration_amt = len(hotel_stats['properties'])
        
        
        if iteration_amt > 10:
            iteration_amt = 10
        for i in range(iteration_amt):
            hotels_available_dict = {
                'hotel_name': hotel_stats['data']['properties'][i]['name'],
                'hotel_id': hotel_stats['data']['properties'][i]['id'],
                'extra_amenities': hotel_stats['data']['properties'][i]['short_amenities'],
                'rating': hotel_stats['data']['properties'][i]['guestRating'],
                'location': hotel_stats['data']['properties'][i]['messages'],
                'price_per_night': hotel_stats['data']['properties'][i]['price']['priceSummary']['displayPrices'][0]['price']
            }
            hotel_info.append(hotels_available_dict)

        if hotel_info == '':
            return "List is empty"

        return hotel_info

            
    def hotel_offers(self, hotel_param):
        url = "https://hotels-com-provider.p.rapidapi.com/v3/hotels/offers"

        try:
            params = {
                "hotel_id": hotel_param['hotel_id'],
                "checkin_date": hotel_param['checkin_date'],
                "checkout_date": hotel_param['checkout_date'],
                "adults_number": hotel_param['adults'],
                "locale": "en_US",
                "domain": "US"
            }
        except TypeError:
            params = hotel_param
        response = requests.get(url, headers=self.headers, params=params)
        
        rooms = response.json()['data']['rooms'][0]

        return rooms


