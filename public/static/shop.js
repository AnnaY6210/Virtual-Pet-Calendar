$(document).on('click', '.buy', function(event) {
    var button = event.currentTarget;
    var item = items[Number(button.id)];
    var price = item["price"];

    if (balance >= price) {
        // Ask for confirmation if expensive
        if (price <= 50 || confirm("Buy " + item["name"] + "?")) {
            balance -= price;
            document.getElementById("balance").innerHTML = String(balance);
            if (!item["rebuyable"]) {
                // Remove buy button
                button.classList.remove("buy");
                button.classList.remove("is-primary");
                button.classList.add("is-success");
                button.innerHTML = "Owned";
            } else {
                // Increment amount owned
                item["count"] += 1;
                document.getElementById("Owned " + button.id).innerHTML = item["count"];
            }

            $.post('/buy', {
                id: item['id'],
                price: item['price']
            });
        }
    } else {
        alert("You can't afford this");
    }
    
})