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
    console.log(responseData);
});

router.get('/device/:name', function(req, res){
    console.log('Someone requested a device id');
    var responseData = {
        status: "success",
        message: socket.get_device_id(req.params.name).toString()
    };
    res.send(responseData);
    console.log(responseData);
    res.status(200);
});

router.post('/device/:id', function(req, res){
    var connection = socket.get_connection(req.params.id);
    if(connection == undefined){
        res.status(400);
        res.send("Device is not connected")
    }
    else{
        res.status(202);
        connection.write(JSON.stringify(req.body));
        connection.on('data', function(data){
            res.end(data);
        });
        setTimeout(function(){
            res.end("No data from device");
        }, 2000);
    }
});

module.exports = router;