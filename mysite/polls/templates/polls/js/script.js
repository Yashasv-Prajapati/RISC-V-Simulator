var action = 'fetch';
var id = 4552;

$.ajax({
    type: "POST",
    url: "support/fetch_data.php",
    data: { action:action, id:id},
    
    success:function(data){
        window.scrollTo(0, 0);
        console.log(data);
        if(data=="error")
        {
            console.log("error");
        }
        else 
        {
            $('#sneha').html(data);
        }
    }
  });
