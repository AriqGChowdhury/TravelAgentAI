import requests
from hotel import Hotel

class Flight:
    def __init__(self):
        self.flight_search_url = "https://priceline-com-provider.p.rapidapi.com/v2/flight/roundTrip"
        self.header =  {
            "x-rapidapi-key": "a7c8bee607msha31b012731c92aap15e779jsna543d630309f",
            "x-rapidapi-host": "priceline-com-provider.p.rapidapi.com"
        }

    def get_flights(self, from_date, to_date, get_flights_dict, adults, destination_iata, num1):
        hotel_obj = Hotel()
        hotel_obj.get_region(get_flights_dict['city_and_state_name'], num1)
        origin_airport_code = hotel_obj.iata
        print(origin_airport_code)
        params = {
            "sid": "DDabcdefgXX",
            "origin_airport_code": f"{origin_airport_code},{destination_iata}",
            "departure_date": f"{from_date},{to_date}",
            "destination_airport_code": f"{destination_iata},{origin_airport_code}",
            "cabin_class": get_flights_dict['cabin_class'],
            "adults": adults,
            "children": get_flights_dict['children']
        }

        if params['children'] == "":
            del params['children']



        flight_results = requests.get(self.flight_search_url, headers=self.header, params=params).json()
        if 'error' in flight_results['getAirFlightRoundTrip']:
            print("reroute to llm")
            return 0
        num = len(flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'])

        status = flight_results['getAirFlightRoundTrip']['results']['status']
        
       
       

        all_flights_list = []
        print("status: ", status)
        print("num : ", num)
        if num > 15:
            num = 15
        for i in range(num):
            duration_from_origin_to_stop = "" 
            stop_airport_name = ""
            arrival_time_to_stop = ""
            duration_from_stop_to_dest = ""     
            arrival_time_to_dest = ""
            duration_origin_to_stop_endOfTrip = ""
            stop_airport_name_endOfTrip = ""
            arrival_time_to_stop_endOfTrip = ""
            arrival_time_to_dest_endOfTrip = ""
            duration_from_stop_to_dest_endOfTrip = ""
            departure_from_stop_to_dest = ""
            departure_from_stop_to_dest_endOfTrip = ""


            departure_info = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['departure']['datetime']
            arrival_info = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['arrival']['datetime']
            arrival_info1 = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['arrival']['datetime']
            departure_info1 = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['departure']['datetime']
            if flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['info']['connection_count'] != 0:
                duration_from_origin_to_stop = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']['flight_0']['info']['duration']
                stop_airport_name = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']['flight_0']['arrival']['airport']['name']
                arrival_time_to_stop = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']['flight_0']['arrival']['datetime']['time_12h']
                if "flight_1" in flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']:
                    duration_from_stop_to_dest = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']['flight_1']['info']['duration']
                    arrival_time_to_dest = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']['flight_1']['arrival']['datetime']['time_12h']
                    departure_from_stop_to_dest =  flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']['flight_1']['departure']['datetime']['time_12h']
            
            if flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['info']['connection_count'] != 0:
                duration_origin_to_stop_endOfTrip = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']['flight_0']['info']['duration']
                stop_airport_name_endOfTrip = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']['flight_0']['arrival']['airport']['name']
                arrival_time_to_stop_endOfTrip = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']['flight_0']['arrival']['datetime']['time_12h']
                if "flight_1" in flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']:
                    duration_from_stop_to_dest_endOfTrip = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']['flight_1']['info']['duration']
                    arrival_time_to_dest_endOfTrip = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']['flight_1']['arrival']['datetime']['time_12h']
                    departure_from_stop_to_dest_endOfTrip = flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']['flight_1']['departure']['datetime']['time_12h']
            
            flight_iter_dict = {
                "number": i + 1,
                "price_per_ticket": flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['price_details']['display_total_fare_per_ticket'],
                "price_for_all_tickets: $": flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['price_details']['display_total_fare'],
                "departure_from_origin_airport": f"{departure_info['date_display']} at {departure_info['time_12h']}",
                "arrival_to_dest": f"{arrival_info['date_display']} at {arrival_info['time_12h']}",
                "departure_from_origin_endOfTrip": f"{departure_info1['date_display']} at {departure_info1['time_12h']}",
                "arrival_to_dest_endOfTrip": f"{arrival_info1['date_display']} at {arrival_info1['time_12h']}",
                "origin_airline_name": flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['airline']['name'],
                "airline_name_endOfTrip": flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['airline']['name'],
                "origin_airport_name": flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['departure']['airport']['code'],
                "destination_airport_name": flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['arrival']['airport']['code'],
                "flight_duration_from_origin_to_stop": duration_from_origin_to_stop,
                "stop_airport_name": stop_airport_name,
                "arrival_time_to_stop": arrival_time_to_stop,
                "departure_from_stop_to_dest": departure_from_stop_to_dest,
                "flight_duration_from_stop_to_dest": duration_from_stop_to_dest,
                "arrival_from_stop_to_dest": arrival_time_to_dest,
                "flight_duration_from_origin_to_stop_endOfTrip": duration_origin_to_stop_endOfTrip,
                "stop_airport_name_endOfTrip": stop_airport_name_endOfTrip,
                "arrival_time_to_stop_endOfTrip": arrival_time_to_stop_endOfTrip,
                "departure_from_stop_to_dest_endOfTrip": departure_from_stop_to_dest_endOfTrip,
                "flight_duration_from_stop_to_dest_endOfTrip": duration_from_stop_to_dest_endOfTrip,
                "arrival_time_to_dest_endOfTrip": arrival_time_to_dest_endOfTrip
            }

            
            
            if "flight_1" not in flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_0']['flight_data']:
                print("Any stops: No\n")
                del flight_iter_dict['flight_duration_from_origin_to_stop']
                del flight_iter_dict['stop_airport_name']
                del flight_iter_dict['arrival_time_to_stop']
                del flight_iter_dict['flight_duration_from_stop_to_dest']
                del flight_iter_dict['arrival_from_stop_to_dest']
                del flight_iter_dict['departure_from_stop_to_dest']
                
            
            
            if "flight_1" not in flight_results['getAirFlightRoundTrip']['results']['result']['itinerary_data'][f'itinerary_{i}']['slice_data']['slice_1']['flight_data']:
                print("Any stops: No\n")
                del flight_iter_dict['flight_duration_from_origin_to_stop_endOfTrip']
                del flight_iter_dict['stop_airport_name_endOfTrip']
                del flight_iter_dict['arrival_time_to_stop_endOfTrip']
                del flight_iter_dict['flight_duration_from_stop_to_dest_endOfTrip']
                del flight_iter_dict['arrival_time_to_dest_endOfTrip']
                del flight_iter_dict['departure_from_stop_to_dest_endOfTrip']
          
            all_flights_list.append(flight_iter_dict)

        return all_flights_list