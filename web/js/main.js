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

    var jqxhr = $.post(_config.api.invokeUrl + '/order', order)
        .done(function (data) {
            alert("Order successful! Waiterbot is on the way!");
        })
        .fail(function (data) {
            console.log("Error submitting order");
        });
}
