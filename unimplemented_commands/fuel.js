// Description:
//   Finds the cheapest local place to get fuel
//
// Commands:
//   `!fuel <POSTCODE>` - Finds the cheapest local place to get fuel and how fair the price is

var request = require('request');
var cheerio = require("cheerio");

module.exports = function(robot) {
  robot.respond(/!?fuel ?(\d{4})/i, function(res) {
    var location = res.match[1];
    robot.getFuelPrice(location, res);
  });

  robot.getFuelPrice = function(location, res) {
    request.post(
      'http://www.racq.com.au/AjaxPages/FuelFinderResultsPage.aspx', {
        form: { 'location': location, 'fuel-type': 'Unleaded' }
      },
      function(error, response, body) {
        var $ = cheerio.load(body);
        var response = '';
        if ((!error) && !($('div.ajax-content p').hasClass('intro'))) {

          //bop it, push it, twist it, scrape it
          var avg_price = $('.price strong').html();
          var good_bad = $('.price span').attr('class').split(' ')[1];
          var commentary = $('.commentary p').html();
          var best_price = $('.fair-fuel-results tbody tr th').html();
          var best_place = $('.fair-fuel-results tbody tr:nth-child(1) td:nth-child(2)').text();
          var best_address = $('.fair-fuel-results tbody tr:nth-child(1) td:nth-child(3)').first().contents().filter(function() {
              return this.type === 'text';
          }).text();

          if (good_bad == 'is-bad') {
            response += '>:x::fuelpump: Average price in ' + location
                     + ' is bad at: ' + avg_price + ' cents p/L\r\n';
          } else {
            response += '>:white_check_mark::fuelpump: Average price in ' + location
                     + ' is good/fair at ' + avg_price + ' cents p/L\r\n';
          }
          response += '>:bulb: ' + commentary + '\r\n';

          if ( !($('.fair-fuel-results').hasClass('regional')) || !(best_price == null) ) {
            response += '>For ' + best_price + ' cents, ' + best_place + ' at ' + best_address + ' has the best price in your area\r\n';
          } else {
            response += ">Unable to provide specific fuel station price data for your postcode\r\n"
          }
        } else {
          response += ">No fuel data for this postcode and fueltype, or an error occured.\r\n";
        }
        res.send(response);
      }
    )}
}
