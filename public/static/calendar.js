$(document).on('click', ".claimtasks",function(e){
    e.preventDefault()
    $.getJSON('/claim_tasks',
        function(data) {
            document.getElementsByClassName("claimtasks")[0].innerHTML = "Claim 0G [Last Claimed: " + data["prev_claim"] + "]";
            document.getElementById("balance").innerHTML = String(data["balance"]);
    });
    
    return false;
    
  });

$(document).on('click', ".tutorial-button",function(e){
    document.getElementsByClassName("tutorial")[0].classList.add('is-active');
});

$(document).on('click', ".modal-close",function(e){
    document.getElementsByClassName("tutorial")[0].classList.remove('is-active');
});

$(document).on('click', ".modal-background",function(e){
    document.getElementsByClassName("tutorial")[0].classList.remove('is-active');
}); 