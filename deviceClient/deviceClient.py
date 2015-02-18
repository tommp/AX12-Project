import socket
import json
from pprint import pprint


clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('78.91.5.36', 9001))

while(True):
    json_data = clientsocket.recv(4096)
    if len(json_data) > 0:
    	try:
        	data = json.loads(json_data)
        	if data["action"] == "move":
        		objects = data["objects"]
        		for dynamo in objects:
        			print dynamo["id"] + " - " + dynamo["speed"]
        			#TODO call method to set dynamo speed

        except ValueError:
        	print "Unable to parse json on string: " + json_data
        #pprint(json_data)
        #pprint(data)