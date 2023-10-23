var items = [];
var itemRows = [];

// GENERATE ITEMS FOR TESING ------------------------
for (let i = 0; i < 24; i++) {
  let x = {name:("Test Item " + i), img:"https://bulma.io/images/placeholders/256x256.png", equipped: false, consumable: false, amount: 0};
  items.push(x);
}
items[1].consumable = true;
items[1].name = "Consumable Test Item";
items[1].amount = 20;
// console.log(items)
// ----------------------------------------

// Seperate items into rows of 6
var temp = [];
for (let i = 0; i < items.length; i++) {
  temp.push(items[i]);
  if (temp.length == 6 || i === items.length-1){
    itemRows.push(temp);
    temp = [];
  }
}

// Generate Rows
var equipOffset = items.length;
var unequipOffset = equipOffset * 2;
$(itemRows).each(function(i, e){
  $(".items").append(
    '<div class="row' + i + ' tile is-parent"></div>'
  );
});

// Populate Rows
$(items).each(function(i, e) {
  // Item is a consumable
  if (e.consumable === true) {
    $(".row" + (Math.floor(i/6))).append(
    '<div class="tile is-parent is-2 "><article class="tile is-child notification is-dark">'
      + items[i].name +'<figure class="image itemImg is-128x128 center"><img src="'
      + items[i].img +'" + id= "'+ i + '"></figure><article class="consumeButton tile is-child notification is-warning" style="display: none;" id = "'  // Consumable Button
      + (i + equipOffset) + '" >Use</article></article></div>'
    );
  }
  else {
    // Item is equipable 
    $(".row" + (Math.floor(i/6))).append(
    '<div class="tile is-parent is-2 "><article class="tile is-child notification is-dark">'
      + items[i].name +'<figure class="image itemImg is-128x128 center"><img src="'
      + items[i].img +'" + id= "'+ i + '"></figure><article class="equipButton tile is-child notification is-success" style="display: none;" id = "'  // Equip Button
      + (i + equipOffset) + '" >Equip</article><article class="unequipButton tile is-child notification is-light" style="display: none;" id = "'
      + (i + unequipOffset) + '" >Unequip</article></article></div>'  // Unequip Button
    );
  }
});

// Click on item to display equip/unequip button
$(".itemImg").click(function(event){
  if (items[event.target.id].equipped === false){
    let equipButton = Number(event.target.id) + equipOffset;
    $("#" + equipButton).toggle();
  }
  else{
    let unequipButton = Number(event.target.id) + unequipOffset;
    $("#" + unequipButton).toggle();
  }
}); 

// Click on equip button to equip (WIP)
$(".equipButton").click(function(event){
  let id = Number(event.target.id) - equipOffset;
  console.log("EQUIPPING: " + id);   // TEST LINE REPLACE WITH API CALL
  $("#" + event.target.id).toggle();
  $("#" + (id + unequipOffset)).toggle();
  items[id].equipped = true;
}); 

// Click on unequip button to unequip (WIP)
$(".unequipButton").click(function(event){
  let id = Number(event.target.id) - unequipOffset;
  console.log("UNEQUIPPING: " + id);   // TEST LINE REPLACE WITH API CALL
  $("#" + event.target.id).toggle();
  $("#" + (id + equipOffset)).toggle();
  items[id].equipped = false;
}); 

// Click on use button to consume an item (WIP)
$(".consumeButton").click(function(event){
  let id = Number(event.target.id) - equipOffset;
  console.log("CONSUMING: " + id);   // TEST LINE REPLACE WITH API CALL
  $("#" + event.target.id).toggle();
  items[id].amount -= 1;
  console.log("REMAINING:" + items[id].amount)
});