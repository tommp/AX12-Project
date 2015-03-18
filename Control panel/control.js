
//var URL = "http://78.91.49.219:9002/devices";
var URL = "http://vsop.online.ntnu.no:9002";
var deviceName = "ruls";
var carActuators = [1, 2, 3, 4];

var speedSlider = 0;
var directionSlider = 0;
var deviceID = -1;
var carID = -1;



var sendGetMessage = function(param){
	$.ajax({url: URL + "/" + param, success: function(result){
        console.log(result["message"]);
    }});
}

var sendPostMessage = function(param, message){
	$.ajax({url: URL + "/" + param, type: "POST", data: message, success: function(result){
        return result;
    }});
}


var setDeviceId = function(){
	$.ajax({url: URL + "/device/" + deviceName, success: function(result){
    	if(result["status"] == "success"){
    		deviceID = result["message"];
    	}
    	else{
    		console.error(result["message"]);
    	}
    }});
}

var createCar = function(){

	var message = '{"action": "createCar", "actuators": ' + carActuators + '}'

	console.log(message);

	$.ajax({url: URL + "/device/" + deviceID, type: "POST", data: message, success: function(result){
        console.log(result);
    }});
}


$(document).foundation({
  slider: {
    on_change: function(){

    	var newSliderValue = $('#slider1').attr('data-slider');

    	if(newSliderValue != speedSlider){
    		speedSlider = newSliderValue;

    		$.ajax({url: URL + "/" + param, success: function(result){
		        console.log(result["message"]);
		    }});
    		console.log(speedSlider);
    	}


    	var newSliderValue = $('#slider2').attr('data-slider');

    	if(newSliderValue != directionSlider){
    		directionSlider = newSliderValue;

    		//send ajax
    		console.log(directionSlider);
    	}
    }
  }
});

$("#stopButton").click(function(){
	$('#slider1').foundation('slider', 'set_value', 0);
	setDeviceId();
});
