// ==UserScript==
// @name         Skyscanner
// @match        https://*.skyscanner.nl/*
// @run-at       document-end
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==

function postResults(start_airport, end_airport, fly_date, price, stops, start_time, end_time) {
    console.log("Enter postResults");
    console.log(start_airport, end_airport, fly_date, price, stops, start_time, end_time);
    GM_xmlhttpRequest ({
        method: "GET",
url: `http://localhost:8000/legoption_submit?start_airport=${start_airport}&end_airport=${end_airport}&fly_date=${fly_date}&price=${price}&stops=${stops}&start_time=${start_time}&end_time=${end_time}`,
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        onload: function(response) {
            console.log("Data sent successfully");
        },
        onerror: function(error) {
            console.log("An error occurred while sending data: " + error);
        }
    });
    console.log("Exit postResults");
}

function gatherAndSubmitResults() {
    console.log("Enter gatherAndSubmitResults");
    let intervalId = setInterval(function() {
        let loadingBar = document.querySelector('div[class*="ProgressBar_container"]');
        if (loadingBar && loadingBar.children.length > 0) {
            return;
        }

        clearInterval(intervalId); // Stop checking
        let results = document.querySelectorAll('div[class*="FlightsResults_dayViewItems"]');
        let start_time, end_time, layovers, price;
        if (results.length > 0) {
            // Extracting parameters "from_" and "to_" from the URL
            let urlParams = window.location.href.split('/');
            let from_ = urlParams[urlParams.length - 4].toUpperCase();
            let to_ = urlParams[urlParams.length - 3].toUpperCase();
            let input = urlParams[urlParams.length - 2];
            let [year, month, day] = [Math.floor(input / 10000) + 2000, Math.floor((input % 10000) / 100), input % 100];
            let fly_date = new Date(Date.UTC(year, month - 1, day));
            fly_date = fly_date.toISOString();

            let ticket = results[0].querySelector('div[class*="FlightsTicket_container"]');
            let times = ticket.querySelectorAll('span[class*="LegInfo_routePartialTime"]');
            if (times.length > 0) {
                let startTimeString = times[0].querySelector('span[class*="BpkText_bpk-text--subheading"]').textContent;
                let endTimeString = times[1].querySelector('span[class*="BpkText_bpk-text--subheading"]').textContent;

                let startTime = new Date(Date.UTC(year, month - 1, day, startTimeString.split(':')[0], startTimeString.split(':')[1]));
                let endTime = new Date(Date.UTC(year, month - 1, day, endTimeString.split(':')[0], endTimeString.split(':')[1]));

                let offset = ticket.querySelector('div[class*="TimeWithOffsetTooltip_offsetTooltipContainer"]');
                if (offset != null && offset.textContent == "+1") {
                    endTime.setDate(endTime.getDate() + 1);
                }
                if (offset != null && offset.textContent == "+2") {
                    endTime.setDate(endTime.getDate() + 2);
                }
                if (offset != null && offset.textContent == "+3") {
                    endTime.setDate(endTime.getDate() + 3);
                }
                start_time = startTime.toISOString();
                end_time = endTime.toISOString();
            }

            let layovers = ticket.querySelectorAll('span[class*="LegInfo_stopsLabelRed"]');
            if (layovers.length === 0) {
                layovers = 0;
            } else {
                layovers = parseInt(layovers[0].textContent[0]);
            }
            let priceElement = ticket.querySelector('div[class*="Price_mainPriceContainer"]');
            if (priceElement) {
                price = parseFloat(priceElement.textContent.replace("€", "").trim());
            }

            postResults(from_, to_, fly_date, price, layovers, start_time, end_time);
        }
    }, 2000);
    console.log("Exit gatherAndSubmitResults");
}

function navigateToNextPage() {
    console.log("Enter navigateToNextPage");
    GM_xmlhttpRequest ({
        method: "GET",
        url: "http://localhost:8000/legoption/",
        headers: {
            "Accept": "application/json"
        },
        onload: function(response) {
            console.log("Got response from GET request");
            let leg = JSON.parse(response.responseText);
            let fly_date = leg.fly_date.split('T')[0].replaceAll('-', '').substring(2);
            let from_ = leg.start_airport.toLowerCase();
            let to_ = leg.end_airport.toLowerCase();
            console.log(`Navigating to: https://www.skyscanner.nl/transport/vluchten/${from_}/${to_}/${fly_date}/?adults=2&adultsv2=2&cabinclass=economy&children=0&childrenv2=&inboundaltsenabled=false&infants=0&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0`);
            window.location.href = `https://www.skyscanner.nl/transport/vluchten/${from_}/${to_}/${fly_date}/?adults=2&adultsv2=2&cabinclass=economy&children=0&childrenv2=&inboundaltsenabled=false&infants=0&outboundaltsenabled=false&preferdirects=false&ref=home&rtn=0`;
        }
    });
    console.log("Exit navigateToNextPage");
}

// Run the function immediately when script is started
console.log("Start script");
gatherAndSubmitResults();

// Set an interval to run the function every 5 minutes
console.log("Set interval to run every 5 minutes");
setTimeout(navigateToNextPage, 30000); // 300000ms equals 5 minutes
console.log("End script");
