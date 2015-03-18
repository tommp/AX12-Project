var net = require('net');
var app = require("./../app");
var socket = {};
var conn_id = 0;
var devices = {};

socket.server = net.createServer(function(connection){
    console.log("client connected");
    connection.on('end', function(){
        console.log("Device disconnected");
        var ObjectKeys = Object.keys(devices);
        var i;
        for(i = 0; i < Object.keys(devices).length; i++){
            if(devices[parseInt(ObjectKeys[i])][1] == connection){
                delete devices[ObjectKeys[i]];
            }
        }

    });

    connection.on('data', function(data){
        var device_data = JSON.parse(data.toString());
        if(Object.keys(device_data)[0] == 'name'){
            var new_id = String(socket.gen_new_id());
            devices[new_id] = [device_data.name, connection];
            console.log(devices);
        }

    })
});

socket.gen_new_id = function(){
    var old_val = conn_id;
    conn_id++;
    return old_val;
};

socket.get_all_connections = function(){
    var arr = [];
    var ObjectKeys = Object.keys(devices);
    var i;
    for(i = 0; i < Object.keys(devices).length; i++){
        arr.push(devices[parseInt(ObjectKeys[i])][1]);
    }
    return arr;
};

socket.get_connection = function(id){
    return (devices[id])[1];
};

socket.get_all_device_names = function(){
    var arr = [];
    var ObjectKeys = Object.keys(devices);
    var i;
    for(i = 0; i < ObjectKeys.length; i++){
        arr.push(devices[parseInt(ObjectKeys[i])][0]);
    }
    return arr;
};

socket.get_device_id = function(name){
    var ObjectKeys = Object.keys(devices);
    var i;
    for(i = 0; i < Object.keys(devices).length; i++){
        if(devices[parseInt(ObjectKeys[i])][0] == name){
            return ObjectKeys[i];
        }
    }
    return -1;
};

module.exports = socket;
