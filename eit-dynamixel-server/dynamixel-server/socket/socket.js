var net = require('net');

var server = net.createServer(function(connection){
    console.log("client connected");
    connection.write("Hello client1")
});



module.exports = server;
