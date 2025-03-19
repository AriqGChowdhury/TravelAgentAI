from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
from llama import Llama
import json

app = Flask(__name__)
secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key
app.config['SERVER_NAME'] = '127.0.0.1:5000'
socketio = SocketIO(app=app)
llm_obj = Llama()
@app.route("/")
def introduction():
    intro = llm_obj.get_regionID()
    return render_template('index.html', intro=intro)


@socketio.on('get_region')
def destination_city(message):
    user_input = message['data']
    llm_obj.get_regionID_user(user_response=user_input)
    socketio.emit('region_received', {"message": "received"})
    

@socketio.on('get_hotels')
def questions(hotel_qs):
    hotel_questions = hotel_qs['hotel_questions']
    hotel_summary = json.loads(llm_obj.hotel_details(restart=False, hotelQs=hotel_questions))
    
    socketio.emit('hotel_summary', {"response": hotel_summary, "lengthh": len(hotel_summary)})

@socketio.on("choose_room")
def choose(message):
    hotel_id = message['data']
    hotel_info = message['hotel_info']
    response = json.loads(llm_obj.get_offer(hotel_id_html=hotel_id))
    lengthOfPics = len(response['propertyUnit']['gallery'])
    lengthOfAmenities = len(response['propertyUnit']['roomAmenities'])
    socketio.emit('room_summary', {"response": response, "length_of_pics":lengthOfPics, "length_of_amenities": lengthOfAmenities, "hotel_info": hotel_info})
    

@socketio.on("hotel_conv")
def cont_hotel(message):
    user_input = message['data']
    hotel_info = message['hotel_info']
    room_info = message['room_info']
    
    response, done = llm_obj.hotel_continued(userInput=user_input, hotelInfo=hotel_info, roomInfo=room_info)
    if done:
        print("done in main")
        socketio.emit('hotel_done', {"message": "Hotel conversation completed!"})
    else:
        socketio.emit('assistant_response2', {"response": response, "socket_name": "hotel_conv"})

@socketio.on("get_flights")
def flight_questions(flight_Qs):
    flight_Qs = flight_Qs['flight_questions']
    flight_options = llm_obj.get_flight_details(flight_Qs)
    socketio.emit('flight_summary', {"response": flight_options, "lengthh": len(flight_options)})

@socketio.on("cont_flight_convo")
def flight_convo(message):
    user_input = message['data']
    if "flight_info" in message:
        flightInfo = message['flight_info']
    else:
        flightInfo = ""
    print("message: ", message)
    response, done = llm_obj.cont_flight_convo(user_input=user_input, flight_info=flightInfo, firstTime=message['firstTime'])
    socketio.emit('assistant_response', {"response": response})
    if done:
        print("flight done in main")
        socketio.emit('flight_done', {"response": "Flight convo done"})
    else:
        socketio.emit('assistant_response2', {"response": response, "socket_name": "cont_flight_convo"})

@socketio.on("activities_conv")
def act_conv(message):
    user_input = message['data']
    response, done = llm_obj.activities_to_do(userInput=user_input, firstTime=message['firstTime'])

    if done:
        socketio.emit('act_response', {"response": response})
    else:
        socketio.emit('act_response', {"response": response, "socket_name": "activities_conv"})


if __name__ == "__main__":  
    socketio.run(app,debug=True)
