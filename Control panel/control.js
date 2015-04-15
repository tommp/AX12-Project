
var URL = "http://78.91.50.234:9002";
//var URL = "http://vsop.online.ntnu.no:9002";
var deviceName = "ruls";
var carActuators = [2,4,1,3];

var speedSlider = 0;
var directionSlider = 0;
var deviceID = -1;
var carID = -1;
var informationInterval;


var setDeviceId = function(){
	$("#status").html("Getting device id...");
	$.ajax({url: URL + "/devicename/" + deviceName, success: function(result){
    	if(result["status"] == "success"){
    		deviceID = result["message"];
    		$("#status").html("Device id set: " + deviceID);
    		createCar();
    	}
    	else{
    		console.error(result["message"]);
    		$("#status").html("Error: " + result["message"]);
    	}
    }});
}

var createCar = function(){

	$("#status").html("Creating car...");

	var message = new Object();

	message.action = "createCar";
	message.actuators = carActuators;

	console.log(JSON.stringify(message));

	$.ajax({url: URL + "/device/" + deviceID, type: "POST", data: JSON.stringify(message), contentType: 'application/json; charset=utf-8', dataType: "json", success: function(result){

        if(result["status"] == "success"){
        	carID = result["message"];
        	$("#status").html("Car created: " + carID);
        }
        else{
        	console.log(result);
        	$("#status").html("Error getting car id: " + result["message"]);
        }
    }});
}


$(document).foundation({
  slider: {
    on_change: function(){

    	var newSliderValue = $('#slider1').attr('data-slider');

    	if(newSliderValue != speedSlider){
    		speedSlider = newSliderValue;

    		speedometerValue = speedSlider;
    		if (speedometerValue < 0)
    			speedometerValue *= -1;

    		$('#speedometer').speedometer({ percentage: speedometerValue || 0 });

    		var message = new Object();

    		message.action = "moveDevice"
    		message.id = carID
    		message.speed = speedSlider
    		message.direction = directionSlider;

    		console.log(JSON.stringify(message))

    		$.ajax({url: URL + "/device/" + deviceID, type: "POST", data: JSON.stringify(message), contentType: 'application/json; charset=utf-8', dataType: "json", success: function(result){
		        console.log(result["message"]);
		    }});
    	}


    	var newSliderValue = $('#slider2').attr('data-slider');

    	if(newSliderValue != directionSlider && speedSlider != 0){
    		directionSlider = newSliderValue;

    		var message = new Object();

    		message.action = "moveDevice"
    		message.id = carID
    		message.speed = speedSlider
    		message.direction = directionSlider;

    		console.log(JSON.stringify(message))

    		$.ajax({url: URL + "/device/" + deviceID, type: "POST", data: JSON.stringify(message), contentType: 'application/json; charset=utf-8', dataType: "json", success: function(result){
		        console.log(result["message"]);
		    }});
    	}
    }
  }
});

var updateTable = function(data){
	$("#tableBody tr").remove();

	var keys = Object.keys(data)

	for(var i = 0; i < keys.length; i++){
		$("#tableBody").append("<tr><td>" + keys[i] + "</td><td>" + data[keys[i]] + "</td></tr>");
	}
}

var updateInformation = function(){
	$.ajax({url: URL + "/device/" + deviceID + "/actuator/" + 2 , dataType: "json", success: function(result){
    	if(result["status"] == "success"){
    		message = result["message"];

			updateTable(message);

    		$("#information").html(JSON.stringify(message));
    	}
    	else{
    		console.error(JSON.stringify(result));
    		$("#information").html("Error: " + result["message"]);
    	}
    }});
}

$( document ).ready(function() {
	$(document).foundation();
	$('#speedometer').speedometer();
  	setDeviceId();
  	informationInterval = setInterval(updateInformation, 1000);

  	$("#stopButton").click(function(){
		$('#slider2').foundation('slider', 'set_value', 0);
		$('#slider1').foundation('slider', 'set_value', 0);

	clearInterval(informationInterval);
});
});




