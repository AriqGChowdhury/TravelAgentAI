from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from hotel import Hotel
from flight import Flight
import json
import os
from datetime import date
import time

torch.cuda.empty_cache()

class Llama:
    def __init__(self):
        self.model_id = "meta-llama/Llama-3.2-3B-Instruct"
        self.travel_agent_chat = []
        self.hotel_obj = Hotel()
        self.flight_obj = Flight()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.restart = False
        self.adults = None
        self.travel_to = None
        self.checkout_date = None
        self.checkin_date = None       
        self.iata = None
        self.itinerary = []

        self.pipe = pipeline(
            "text-generation", 
            model=self.model_id,
            tokenizer=self.tokenizer,
            device_map="auto",
            torch_dtype=torch.bfloat16
        )

        
    def llama_response(self, messages, max_toke):
        try:
            output = json.loads(self.pipe(
                messages,
                max_new_tokens=max_toke
                )[0]["generated_text"][-1]['content'])
        except:
            output = self.pipe(
                messages,
                max_new_tokens=max_toke
                )[0]["generated_text"][-1]['content']
            
        return output
    
    def activities_to_do(self, userInput, firstTime): 
        torch.cuda.empty_cache()
        
        if firstTime == True:
            self.travel_agent_chat.clear()
            travel_details = {
                "role": "user",
                "content": f"From {self.checkin_date} to {self.checkout_date}. Visiting {self.travel_to}"
            }
            self.travel_agent_chat.append(travel_details)
            system_role = {
                "role": "system",
                "content": 
                """
                    Ive provided you with a checkin and checkout date along with a destination the user is traveling to. 
                    create an a schedule consisting of activities to do in the city they are visiting.
                    *Do not ask them questions about checking in, checking out or the city they are traveling to since I've already provided that information to you.
                    *Don't recommend the same place twice.
                    *Pick popular attractions within a 25 mile radius from the city.
                    *All attractions dont have to be in the city chosen.

                """
            }
            self.travel_agent_chat.append(system_role)
        
        if userInput != "":
            self.travel_agent_chat.append({
                "role": "user",
                "content": userInput
            })

        llm_response = self.llama_response(self.travel_agent_chat, max_toke=2000)
        print("llm response", llm_response)
        self.travel_agent_chat.append({
            "role": "assistant",
            "content": llm_response
        })
        new_llm_response = ""
        for i in range(len(llm_response)):
            if llm_response[i] == "*" and llm_response[i + 1] == "*":
                new_llm_response += "<br><br>"
            if i >= 1:
                if llm_response[i] == "*" and llm_response[i - 1] != "*" and llm_response[i + 1] != "*":
                    new_llm_response += "<br>"
            if llm_response[i] != "*":
                new_llm_response += llm_response[i]
        

        if "done" in new_llm_response or "Done" in new_llm_response:
            new_llm = llm_response.lower().replace("done","")
            return new_llm, True
        return new_llm_response, False

        
    def get_flight_details(self, questions):
        torch.cuda.empty_cache()
        self.travel_agent_chat.clear()
        flight_role = {
            "role": "system",
            "content": 
            """
                *You are a travel agent acquiring information for flights, Do not greet the user.
                *We already have hotel information.
                *I've asked the user the following questions:
                  1. Where are you traveling from? (City and state)
                  2. Would you like to fly economy, premium, business or first?
                  3. Are you bringing any children? If so, how many?
                *Your job is to respond with a dictionary object ONLY.

                Example:
                {
                    "city_and_state_name": "name of city and state of origin" (make sure to write full state name),
                    "cabin_class": "economy",
                    "children": "1"
                }
                *Make sure to put double quotes in the dictionary no single.
                *If user says no to "children" then leave it blank.

                
            """
        }
        self.travel_agent_chat.append(flight_role)
        self.travel_agent_chat.append({
            "role": "user",
            "content": questions
        })
        flight_llama_response = self.llama_response(self.travel_agent_chat, max_toke=500)
        self.travel_agent_chat.append({
            "role": "assistant",
            "content": flight_llama_response
        })
        try:
            get_flights_dict = json.loads(flight_llama_response)
        except:
            get_flights_dict = flight_llama_response

        
        flight_data = self.flight_obj.get_flights(from_date=self.checkin_date, to_date=self.checkout_date, get_flights_dict=get_flights_dict, adults=self.adults, destination_iata=self.iata, num1=0)
        self.travel_agent_chat.clear()
        torch.cuda.empty_cache()
        return flight_data
       
    
    def cont_flight_convo(self, user_input, flight_info, firstTime):
        if firstTime == True:
            self.travel_agent_chat.append({
                "role": "system",
                "content": """When user mentions anything about activities or says next or implys they are done with the flights then respond with 'done'
                            I've also provided the flight details.
                            ** If the user mentions activities then only respond with "done".   
                                """
            })
             
            if flight_info != "":
                self.travel_agent_chat.append({
                    "role": "user",
                    "content": flight_info
                })
        self.travel_agent_chat.append({
                "role": "user",
                "content": user_input
            })
        flight_response = self.llama_response(self.travel_agent_chat, max_toke=500)
        print(flight_response)
        if "done" in flight_response or "Done" in flight_response:
            self.itinerary.append(flight_response.lower().replace("done",""))
            return flight_response.lower().replace("done",""), True
        else:
            return flight_response, False
            



    def get_regionID(self):

        system_role = {
            "role": "system",
            "content": 
            """
                1. You are a Travel Agent named Shadow.
                2. Greet the user, introduce yourself and ask where they will be traveling (city and state)
                3. Only respond with the city and state in a string format. Nothing Else!
            """
        }
        self.travel_agent_chat.append(system_role)

        response = self.llama_response(messages=self.travel_agent_chat, max_toke=2000)
        
        self.travel_agent_chat.append({
            "role": "assistant",
            "content": response
        })
        return response
    
    def get_regionID_user(self, user_response):
        self.travel_agent_chat.append({
            "role": "user",
            "content": user_response
        })
        
        region = self.llama_response(messages=self.travel_agent_chat, max_toke=2000)
        self.travel_to = region
        self.hotel_obj.get_region(region, 0)
        self.iata = self.hotel_obj.iata
        self.travel_agent_chat.append({
            "role": "assistant",
            "content": region
        })
        return 1


    def hotel_details(self, restart, hotelQs):
        restart = False
        print(hotelQs)
        if restart == False:
            for items in range(len(self.travel_agent_chat) - 2):
                if self.travel_agent_chat[items]['role'] == "system":
                    del self.travel_agent_chat[items]
            system_role2 = {
                "role": "system",
                "content": 
                """ ***I've already asked the following questions to the user***
                    1. When will you be checking in and checking out? (required)
                    2. How many adults? (required)
                    3. What is your max budget?
                    4. Are you looking for certain amenities?
                    5. How would you like to sort the results?
                    
                    *If the user does not provide the month, USE THE CURRENT MONTH. Don't ask the user if they would like to know the current month.
                    *Sorting options: REVIEW, RECOMMENDED, DISTANCE, PRICE_LOW_TO_HIGH, PROPERTY_CLASS, OR PRICE_RELEVANT.
                    *Amenities options: SPA_ON_SITE,WIFI,HOT_TUB,FREE_AIRPORT_TRANSPORTATION,POOL,GYM,OCEAN_VIEW,WATER_PARK,BALCONY_OR_TERRACE,KITCHEN_KITCHENETTE,ELECTRIC_CAR,PARKING,CRIB,RESTAURANT_IN_HOTEL,PETS,WASHER_DRYER,CASINO,AIR_CONDITIONING.
                    *Do not just respond with the city and state!!
                    *When showing the user the sorting options and amenities, don't include the underscores and capital letters.
                    *Give a human like response.
                """
            }
            self.travel_agent_chat.append(system_role2)

            self.travel_agent_chat.append({
                "role": "user", 
                "content": hotelQs
            })

        system_role3 = [{
            "role": "system",
            "content": f"The current date is {date.today()}, make sure the checkin_date is NOT before this date!!"
        },
        {
            "role": "system",
            "content": 
            """
                *Now your job is respond with a dictionary based on the user response.
                *If the user does not list a parameter that is optional then leave it blank!
                *This is an example of how the dictionary should be formatted.
                **Only respond with dictionary!
                *Do not include any other text it must be a json object.


                    {
                        "checkout_date":"yyyy-mm-dd", #required
                        "amenities":"WIFI,PARKING",
                        "price_max":"500",
                        "adults_number":"1", #required
                        "checkin_date":"yyyy-mm-dd", #required
                        "star_rating_ids":"3,4,5",
                        "sort_order":"REVIEW", #required
                    }
            """
        }]
        self.travel_agent_chat.append(system_role3[1])
        self.travel_agent_chat.append(system_role3[0])
        hotel_param_after = self.llama_response(messages=self.travel_agent_chat, max_toke=2000)
        

        self.travel_agent_chat.append({
            "role": "assistant",
            "content": hotel_param_after
        })
        try:
            hotel_param_after = json.loads(hotel_param_after)
        except:
            print()
        
        self.checkout_date = hotel_param_after['checkout_date']
        self.checkin_date = hotel_param_after['checkin_date']
        self.adults = hotel_param_after['adults_number']
        hotels_available = self.hotel_obj.get_hotels(hotel_param_after)
        ##FRom here
        hotel_name = hotels_available[0]['hotel_name']
        hotel_id = hotels_available[0]['hotel_id']
        ratingText = hotels_available[0]['rating']['ratingText']
        location = hotels_available[0]['location'][0]
        price_per_night = hotels_available[0]['price_per_night']['formatted']
        return json.dumps(hotels_available)

    
    def get_offer(self, hotel_id_html):
        self.travel_agent_chat.clear()
        new_dict = {
            "checkin_date": self.checkin_date,
            "checkout_date": self.checkout_date,
            "adults": self.adults,
            "hotel_id": hotel_id_html
        }
        response = self.hotel_obj.hotel_offers(new_dict)
        room_names = response['header']['name']
        room_desc = response['propertyUnit']['description']
        room_pics = response['propertyUnit']['gallery'][0]['url'] #loop
        roomAmentitiesName = response['propertyUnit']['roomAmenities'][0]['header'] #loop
        roomAmenitiesContent = response['propertyUnit']['roomAmenities'][0]['items'][0]['content'] #loop
        # if available
        cancellation = response['propertyUnit']['ratePlans'][0]['priceDetails'][0]['cancellationPolicy']['type']
        ratePlanPrice = response['propertyUnit']['ratePlans'][0]['priceDetails'][0]['price']['total']['amount']
        # print(response)
        return json.dumps(response)
        
        
    
        
            
    def hotel_continued(self, userInput, hotelInfo, roomInfo):
        print("in llama hotel_continued")
        system_role6 = {
            "role":"system",
            "content": """Answer any questions about the hotel and hotel room.
                When the user is done, respond with 'done'.
                if the user mentions *anything* about flights or enters 'next' that means they are *done* with the hotels so respond with 'done'.
            """
        }
        self.travel_agent_chat.append(system_role6)
        self.travel_agent_chat.append({
            "role": "user",
            "content": hotelInfo
        })
        self.travel_agent_chat.append({
            "role": "user",
            "content": roomInfo
        })
        self.travel_agent_chat.append({
            "role": "user",
            "content": userInput
        })
        
        
        llm_response_new = self.llama_response(self.travel_agent_chat, 500)
        print(llm_response_new)
        if "done" in llm_response_new or "Done" in llm_response_new:
            print("done")
            new_llm_response = llm_response_new.lower().replace("done","")
            self.itinerary.append(llm_response_new.lower().replace("done",""))
            self.travel_agent_chat.append({
                "role": "assistant",
                "content": new_llm_response
            })
            return new_llm_response, True
        else:
            print("not done")
            self.travel_agent_chat.append({
                "role": "assistant",
                "content": llm_response_new
            })
            return llm_response_new, False

            
            
        
        
    
    

    
    
    
    
    

