var net = require('net');
var app = require("./../app");
var socket = {};
var conn_id = 0;
var connections = {};
var devices = {};

socket.server = net.createServer(function(connection){
    console.log("client connected");
    connection.on('end', function(){
        console.log("Device disconnected");
    });

    connection.on('data', function(data){
        console.log("hey");
        var device_data = JSON.parse(data.toString());
        if(Object.keys(device_data)[0] == 'name'){
            var new_id = String(socket.gen_new_id());
            connections[new_id] = connection;
            devices[device_data.name] = new_id;
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
    return connections;
};

socket.get_connection = function(id){
    return connections[id];
};

socket.get_all_devices = function(){
    return devices;
};

socket.get_device_id = function(name){
    return devices[name];
}

module.exports = socket;
