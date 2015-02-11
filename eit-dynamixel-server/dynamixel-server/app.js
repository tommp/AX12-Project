var express = require('express');
var app = module.exports = express();
var bodyParser = require('body-parser');
var net = require('net');
var port = process.env.PORT || 8080;
//var socketServer = require('./socket/socket');

app.use(bodyParser.json());

app.use(bodyParser.urlencoded({ extended: false }));

/*require('net').createServer(function (socket){
    console.log('connected');

    socket.on('data', function(data){
        console.log(data.toString());
        socket.write("Start")
    });

}).listen(9001); */

socketServer.listen(9001, function(){
    console.log("I am listening on the socket, I think...");
});


var router = require('./routes/users');
app.use('/', router);

app.listen(port);

console.log("Listening on http://localhost:" + port);

module.exports = app;
