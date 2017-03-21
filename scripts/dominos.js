// Description
//        A script to find the best dominos coupons
//
// Commands:
//        !dominos -n <number of coupons to list> -f <only find coupons with this/ these word(s) in it> -e (to view expiry dates)
//        if -n isn't specified the number of coupons listed is 10 or as many as can be found up to 10
//


var cheerio = require("cheerio");

module.exports = function (robot) {

    function printItems(res, item) {
        var noOfCoupons = 10;
        var specialWords = false;
        var response = "";
	var expiry = false;
	
        if (item.match(/-n/g) !== null) {
            noOfCoupons = item.match(/-n\s+\d{0,3}/g)[0].match(/\d+/)[0];
        }

        if (item.match(/-f/g) !== null) {
            specialWords = item.match(/-f\s+[^\-]+/g)[0].match(/[^\-f]+/g)[0].trim();
            specialWords = new RegExp(specialWords, "gi");
        }

	if (item.match(/-e/g) !== null) {
	    response += "Coupon\tExpiry\t\tDescription\n";
	    expiry = true;
	} else {
	    response += "Coupon\tDescription\n";
	}


        var URL = "https://www.couponese.com/store/dominos.com.au/";
        robot.http(URL).get()(function (err, resp, body) {
            $ = cheerio.load(body);
            $(".ov-coupon:not(.ov-expired)").each(function (i, elem) {
                if (noOfCoupons > 0) {
                    var code = $(this).find(".ov-code").find("strong").text();
                    var message = $(this).find(".ov-title").find("a").text();
		    var expDate = $(this).find(".ov-expiry").text().trim();
		    
		    if (expiry) {
			message = expDate + "\t" + message;
	 	    }		

                    if (!!specialWords) {
                        if (message.match(specialWords) !== null) {;
                            response += code + "\t" + message + "\n";
                            noOfCoupons--;
                        } else {
                            noOfCoupons--;
                        }
                    } else {
                        response += code + "\t" + message + "\n";
                        noOfCoupons--;
                    }
                }
            });
            res.send(response);
        });
    }

    // Response if no args given
    robot.respond(/!?dominos(.*)$/, function (res) {
	res.send("Fetching the latest dominos coupons");
        printItems(res, res.match[1]);
    });

};

