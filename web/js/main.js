function sendOrder() {
    var t = document.getElementById("tables");
    var tableSelection = t.options[t.selectedIndex].value;
    t = document.getElementById("menu");
    var menuSelection = t.options[t.selectedIndex].value;
    var payload = { "table": tableSelection, "menu_item": menuSelection };

    order = JSON.stringify({
        "table": tableSelection,
        "menu_item": menuSelection
    })
    console.log(order)

    // Send to API gateway->Lambda->IoT
    // TODO: Success/error is not firing correctly but the data is moving through system
/*     $.ajax({
        method: 'POST',
        url: _config.api.invokeUrl + '/order',
        data: order,
        contentType: 'application/json',
        success: completeRequest
    }); */
    var jqxhr = $.post(_config.api.invokeUrl + '/order', order)
        .done(function () {
            alert("Order successful! Waiterbot is on the way!");
        })
        .fail(function () {
            console.log("Error submitting order");
        });
}
