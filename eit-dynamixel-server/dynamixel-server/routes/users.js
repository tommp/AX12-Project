var express = require('express');
var router = express.Router();
var app = require("./../app");
var socket = require("./../socket/socket");


router.get('/', function(req, res){
   res.send("Hello World!");
});

router.get('/devices/', function(req, res) {
    console.log('Someone requested get all devices');
    var responseData = {
        status: "success",
        message: {
            devices: socket.get_all_device_names()
        }
    };
    res.send(responseData);
});

router.get('/device/:name', function(req, res){
    console.log('Someone requested a device id');
    var responseData;
    if(socket.get_device_id(req.params.name) == undefined){
        responseData = {
            status: "error",
            message: "Unknown Name"
        };
    }
    else{
        responseData = {
            status: "success",
            message: socket.get_device_id(req.params.name).toString()
        };
    }
    res.send(responseData);
    res.status(200);
});

router.get('/device/:id/actuators', function(req,res){
    var connection = socket.get_connection(req.params.id);
    if(connection == undefined){
        res.send({status: "error", message: "Unknown ID"})
    }
    else{
        connection.write(JSON.stringify({action: "listActuators"}));
        connection.on('data', function(data){
            var inData = JSON.parse(data.toString());
            var actuator_ids = inData['ids'];
            res.end(JSON.stringify({
                status: "success",
                message: {
                    actuators: actuator_ids
                }
            }));
        });
        setTimeout(function(){
            res.end(JSON.stringify({status: "error", message: "Device timed out"}));
        }, 2000);
    }
});

router.post('/device/:id', function(req, res){
    var connection = socket.get_connection(req.params.id);
    if(connection == undefined){
        res.send({status: "error", message: "Unknown ID"})
    }
    else{
        res.status(202);
        connection.write(JSON.stringify(req.body));
        connection.on('data', function(data){
            res.end(data);
        });
        setTimeout(function(){
            res.end(JSON.stringify({status: "error", message: "Device timed out"}));
        }, 2000);
    }
});

module.exports = router;