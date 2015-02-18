var net = require('net');
var app = require("./../app");

var server = net.createServer(function(connection){
    console.log("client connected");
    connection.write("Hello client\n");
    app.set("deviceConnection", connection);
});



module.exports = server;
