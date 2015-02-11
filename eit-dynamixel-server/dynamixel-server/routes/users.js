var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res) {
    console.log('Someone requested a get');
    res.send('Hello World!');
});

router.post('/', function(req, res){
    console.log('Someone requested a post');
    console.log(req.body.move);
    res.send(req.body.move);

});
module.exports = router;
