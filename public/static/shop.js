$(document).on('click', '.buy', function(event) {
    var item = items[event.target.id];
    console.log("Spending " + item['price'] + " gold");

    $.post('/buy', {
        name: item['name'],
        price: item['price']
    });
})