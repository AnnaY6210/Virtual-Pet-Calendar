$(document).on('click', ".claimtasks",function(e){
    e.preventDefault()
    $.getJSON('/claim_tasks',
        function(data) {
            document.getElementsByClassName("claimtasks")[0].innerHTML = "Claim 0G [Last Claimed: " + data["prev_claim"] + "]";
            document.getElementsByClassName("currency-counter")[0].innerHTML = "<img src='/static/img/money_bag.png'/>" + data["balance"];
    });
    
    return false;
    
  }); 