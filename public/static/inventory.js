// Click on equip button to equip (WIP)
$(document).on('click', ".test", function(event){
  var item = items[Number(event.currentTarget.id)];
  console.log(item["name"]);

  event.currentTarget.classList.remove('is-primary');
  event.currentTarget.classList.remove('test');
  event.currentTarget.classList.add('is-success');
  event.currentTarget.innerHTML = "Used";

  // Post method here
  
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