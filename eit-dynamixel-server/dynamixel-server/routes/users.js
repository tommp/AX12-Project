var express = require('express');
var router = express.Router();
var app = require("./../app");


/* GET users listing. */
router.get('/', function(req, res) {
    console.log('Someone requested a get');
    res.send('Hello World!');
});

router.post('/', function(req, res){
    var connection = app.get("deviceConnection");
    if(connection == undefined){
        res.status(400);
        res.send("Device is not connected")
    }
    else{
        res.status(202);
        connection.write("Hello from http\n");
        res.send("Message sent to device")
    }
});
module.exports = router;
