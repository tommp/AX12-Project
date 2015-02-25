var express = require('express');
var router = express.Router();
var app = require("./../app");
var socket = require("./../socket/socket");


router.get('/', function(req, res){
   res.send([socket.get_all_connections(), socket.get_all_devices()]);
});

router.get('/devices/', function(req, res) {
    console.log('Someone requested get all devices');
    res.send(socket.get_all_devices());
    console.log(socket.get_all_devices());
});

router.get('/device/:name', function(req, res){
    console.log('Someone requested a device id');
    res.send(socket.get_device_id(req.params.name));
    console.log(socket.get_device_id(req.params.name));
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