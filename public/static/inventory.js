// Used for equippable items (pets only right now)
function equip(item, button) {
    // Change current "displayed" button to "display"
    for (let i = 0; i < items.length; i++) {
        elem = document.getElementById(i)
        if (elem.innerText == "Displayed") {
            elem.innerHTML = "Display";
            elem.disabled = false;
            elem.classList.remove("is-success");
            elem.classList.add("is-primary");
        }
    }
    
    // Create new "displayed" button and show new pet
    button.classList.remove("is-primary");
    button.classList.add("is-success");
    button.disabled = true;
    button.innerHTML = "Displayed";
    // Display pet if not dead, grave otherwise
    pet = document.getElementById("pet");
    if (item["health"] > 0) {
        pet.src = item["spritesheet"];
        pet.classList.add("pet_spritesheet");
        pet.alt = "pet";
    } else {
        pet.src = "static/img/grave.png";
        pet.classList.remove("pet_spritesheet");
        pet.alt = "grave";
    }
    
    document.getElementById("health").value = item["health"];
}

// Used for consumable items
function consume(item, button, amount) {
    // Fail if at full health
    if (document.getElementById("health").value >= 100) {
        alert("This won't have any effect");
        return false;
    } else if (document.getElementById("health").value <= 0) {
        alert("You can't feed a deat pet!");
        return false;
    }
    // Add health and remove item
    document.getElementById("health").value += 10;
    item["count"] -= 1;
    amount.innerHTML = item["count"];
    // Change button if now out of that item
    if (item["count"] <= 0) {
        button.classList.remove("is-primary");
        button.classList.add("is-danger");
        button.innerHTML = "None left";
        button.disabled = true;
    }
    
    return true;
}

$(document).on("click", ".button", function(event) {
    var button = event.currentTarget;
    var item = items[Number(button.id)];
    var item_type = "None";

    if (button.classList.contains("equipable")) {
        equip(item, button);
        item_type = "equip";
    } else if (button.classList.contains("consumable")) {
        var amount = document.getElementById("Count " + button.id);
        if (consume(item, button, amount)) {
            item_type = "consume";
        }
    }

    if (item_type != "None") {
        $.post("/use_item", {
            type: item_type,
            id: item["id"],
        });
    }
});