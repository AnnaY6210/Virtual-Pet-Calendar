// List of item names, images, and descriptions
var items = [];

// Test items
for (let i = 0; i < 24; i++) {
    items.push(["Item " + String(i), "https://bulma.io/images/placeholders/640x320.png", "Description " + String(i)]);
}

const baseItem = document.getElementById("item");
const baseRow = document.getElementById("row");

// Add items to HTML
for (let i = 0; i < items.length; i++) {
    // Create new row every 6 items
    if (i % 6 == 0) {
        var row = baseRow.cloneNode();
        document.getElementById("start").appendChild(row);
    }

    // Add next item and its info
    var item = baseItem.cloneNode(true);
    row.appendChild(item);
    item.id = items[i][0];
    item.getElementsByClassName("title")[0].innerHTML = items[i][0];
    item.getElementsByTagName("img")[0].src = items[i][1];
    item.getElementsByClassName("content")[0].innerHTML = items[i][2];
}