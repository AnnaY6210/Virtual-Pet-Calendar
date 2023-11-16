$(document).on('click', '.buy', function(event) {
    var item = items[Number(event.currentTarget.id)];
    var price = item["price"];

    if (balance >= price) {
        // Ask for confirmation if expensive
        if (price <= 50 || confirm("Buy " + item["name"] + "?")) {
            balance -= price;
            document.getElementById("balance").innerHTML = String(balance);
            if (!item["rebuyable"]) {
                // Remove buy button
                event.currentTarget.classList.remove("buy");
                event.currentTarget.classList.remove("is-primary");
                event.currentTarget.classList.add("is-success");
                event.currentTarget.innerHTML = "Owned";
            } else {
                // Increment amount owned
                item["count"] += 1;
                event.currentTarget.children[1].innerHTML = ") (Owned: " + item["count"];
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