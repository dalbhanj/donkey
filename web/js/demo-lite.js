
function sendDestination(payload) {
    var jqxhr = $.post(_config.api.invokeUrl + '/waiterbot-demo-lite-api', payload)
        .done(function (data) {
            alert("Rover moving");
        })
        .fail(function () {
            console.log("Error moving rover");
        });
}

/**
 * Tell the rover that the order is ready to go.
 */
function left() {
    var payload = JSON.stringify({ "path": 1 });
    console.log("Taking left path");
    sendDestination(payload)
}

function right() {
    var payload = JSON.stringify({ "path": 2 });
    console.log("Taking right path");
    sendDestination(payload)
}