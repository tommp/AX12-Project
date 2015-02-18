var express = require('express');
var app = module.exports = express();
var bodyParser = require('body-parser');
var net = require('net');
var socketServer = require('./socket/socket');
var router = require('./routes/users');
var httpPort = 8080;
var socketPort = 9001;
var deviceConnection;
var deviceConnections = {};
var connection_id = 0;

app.use(bodyParser.json());

app.use(bodyParser.urlencoded({ extended: false }));

app.use('/', router);

app.listen(httpPort, function(){
    console.log("Http server listening on http://localhost:" + httpPort);
});

socketServer.listen(socketPort, function(){
    console.log("Socket server listening on http://localhost:" + socketPort);
});

function newID(){
    connection_id += 1;
    return connection_id;
}

module.exports = app;
