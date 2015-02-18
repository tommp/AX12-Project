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