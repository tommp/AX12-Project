var express = require('express');
var app = module.exports = express();
var bodyParser = require('body-parser');
var net = require('net');
var socketServer = require('./socket/socket').server;
var router = require('./routes/users');
var httpPort = 9002;
var socketPort = 9001;

app.use(bodyParser.json());

app.use(bodyParser.urlencoded({ extended: false }));

app.use('/', router);

app.listen(httpPort, function(){
    console.log("Http server listening on Port: " + httpPort);
});

socketServer.listen(socketPort, function(){
    console.log("Socket server listening on Port: " + socketPort);
});

module.exports = app;
