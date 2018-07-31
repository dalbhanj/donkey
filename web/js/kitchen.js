var orders = [];
var dynatable = new Object();

$(document).ready(function () {
    dynatable = $('#orders').dynatable({
        dataset: {
            records: orders
        }
    }).data('dynatable');

    $(function () {
        getData();
        $.ajaxSetup({
            cache: false
        });
        setInterval(getData, 5000);
    });
});

/*
 * Get orders currently in flight from the kitchen API
 */
function getData() {
    orders = [];
    var jqxhr = $.get(_config.api.invokeUrl + '/waiterbot-fulfillment-api')
        .done(function (data) {
            for (var i in data) {
                var order = getOrderInfo(data[i]);
                orders.push(order);
            }
            orders.sort(function (a, b) {
                return a.OrderId.localeCompare(b.OrderId);
            });
            dynatable.settings.dataset.originalRecords = orders;
            dynatable.process();
        })
        .fail(function () {
            console.log("scan error");
        });
}

/**
 * The JSON that DynamoDB returns cannot be used directly by dynatable so we
 * need to pull out the relevant info.
 */
function getOrderInfo(item) {
    var order = {};
    order.OrderId = item.order_id.S;
    order.Table = item.table.N;
    order.MenuItem = item.menu_item.S;
    order.Fulfill = "<button type=\"button\" id=" + order.OrderId + " onclick=\"fulfillOrder(this.id)\">Order Up!</button>"
    return order;
}

/**
 * Tell the rover that the order is ready to go.
 */
function fulfillOrder(orderId) {
    payload = JSON.stringify({ "order_id": orderId });
    console.log("Fulfilling order #" + orderId);
    var jqxhr = $.post(_config.api.invokeUrl + '/waiterbot-fulfillment-api', payload)
        .done(function (data) {
            alert("Order fulfilled!");
        })
        .fail(function () {
            console.log("Error fulfilling order");
        });
}

function confirmOrder() {
    var jqxhr = $.post(_config.api.invokeUrl + '/waiterbot-order')
        .done(function (data) {
            console.log("Waiterbot is returning to the kitchen.");
        })
        .fail(function (data) {
            console.log("Error submitting order");
        });
}