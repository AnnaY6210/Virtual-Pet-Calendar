$(document).on('click', ".claimtasks",function(e){
    e.preventDefault()
    $.getJSON('/claim_tasks',
        function(data) {
            window.location.reload()
    });
    
    return false;
    
  }); 