var items = [];

// GENERATE ITEMS FOR TESING ------------------------
for (let i = 0; i < 24; i++) {
  let x = {name:("Test Item " + i), img:"https://bulma.io/images/placeholders/256x256.png", equipped: false, consumable: false, amount: 0, description:"DESCRIPTION"};
  items.push(x);
}
items[1].consumable = true;
items[1].name = "Consumable Test Item";
items[1].amount = 20;
items[2].equipped = true;
// console.log(items)
// ----------------------------------------


//  Item/Row Generation from @bbirnbau

const baseItem = document.getElementById("item");
const baseRow = document.getElementById("row");

for (let i = 0; i < items.length; i++) {
  // Create new row every 6 items
  if (i % 6 == 0) {
      var row = baseRow.cloneNode();
      document.getElementById("start").appendChild(row);
  }

  // Add next item and its info
  var item = baseItem.cloneNode(true);
  row.appendChild(item);
  item.getElementsByClassName("button")[0].id = i;
  if(items[i].consumable === true){
    document.getElementById(i).classList.add('consumeButton')
  }else if (items[i].equipped === false){
    document.getElementById(i).classList.add('equipButton');
    document.getElementById(i).innerHTML = "Equip";
  } else {
    document.getElementById(i).classList.add('unequipButton');
    document.getElementById(i).classList.add('is-warning');
    document.getElementById(i).innerHTML = "Unequip";
  }
  item.getElementsByClassName("title")[0].innerHTML = items[i].name;
  item.getElementsByTagName("img")[0].src = items[i].img;
  item.getElementsByClassName("content")[0].innerHTML = items[i].description;
}

// Click on equip button to equip (WIP)
$(document).on('click', ".equipButton",function(event){
  let id = Number(event.target.id);
  console.log("EQUIPPING: " + id);   // TEST LINE REPLACE WITH API CALL

  document.getElementById(id).classList.remove('equipButton')
  document.getElementById(id).classList.remove('is-primary')
  document.getElementById(id).classList.add('unequipButton')
  document.getElementById(id).classList.add('is-warning')
  document.getElementById(id).innerHTML = "Unequip";
  items[id].equipped = true;
}); 

// Click on unequip button to unequip (WIP)
$(document).on('click', ".unequipButton",function(event){
  let id = Number(event.target.id);
  console.log("UNEQUIPPING: " + id);   // TEST LINE REPLACE WITH API CALL
  
  document.getElementById(id).classList.remove('unequipButton')
  document.getElementById(id).classList.remove('is-warning')
  document.getElementById(id).classList.add('equipButton')
  document.getElementById(id).classList.add('is-primary')
  document.getElementById(id).innerHTML = "Equip";
  items[id].equipped = false;
}); 

// Click on use button to consume an item (WIP)
// $(".consumeButton").click(function(event){
//   let id = Number(event.target.id) - equipOffset;
//   console.log("CONSUMING: " + id);   // TEST LINE REPLACE WITH API CALL
//   $("#" + event.target.id).toggle();
//   items[id].amount -= 1;
//   console.log("REMAINING:" + items[id].amount)
// });