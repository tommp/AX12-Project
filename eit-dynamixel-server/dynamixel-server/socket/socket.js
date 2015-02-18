var net = require('net');
var app = require("./../app");


var server = net.createServer(function(connection){
    console.log("client connected");
    connection.write("Hello client\n");
    var connections = app.get("deviceConnections");
    //connections[app.newID()] = connection;
    //console.log(connections);
    app.set("deviceConnection", connection);

    connection.on('end', function(){
        app.set("deviceConnection", undefined);
        console.log("Device disconnected")
    });

    connection.on('data', function(data){
        console.log(data.toString());
    })
});



module.exports = server;
