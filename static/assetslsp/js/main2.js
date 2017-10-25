$(function() {
    $("#test").on('submit', function(event){
    event.preventDefault();
    //alert("form submitted....!");  // sanity check
    send_form();

    });

function send_form() 
{
	 console.log("create post is working!") // sanity check
     console.log($('#id_searchTerm').val())
     var checkbox_value = [];
     $('#clients-sec').html("<div class="col-md-3">Searching...</div>");
	 // add the error to the dom
    
    $(":checkbox").each(function () {
        var ischecked = $(this).is(":checked");
        if (ischecked) {
           // checkbox_value += $(this).val() + ",";
           //console.log($(this).val());
           checkbox_value.push($(this).val());
        }
        
    });
    //checkbox_value+="]"
	console.log(checkbox_value)
	things = JSON.stringify(checkbox_value)
	console.log(things)
	$.ajax({
        url : "create_post/", // the endpoint
        type : "POST", // http method
        data : { search : $('#id_searchTerm').val(),
        		source : $('#id_source').val() ,
        		target:  $('#id_target').val() ,
        		selectedtermbases: checkbox_value  }, // data sent with the post request
		
        // handle a successful response
        success : function(json) {
            var serach = $('#id_searchTerm').val(); // remove the value from the input
            console.log(json); // log the returned json to the console
            console.log("success"); // another sanity check
            $('#clients-sec').html(json);
        },

        // handle a non-successful response
        error : function(xhr,errmsg,err) {
            $('#clients-sec').html("<div class='alert-box alert radius' data-alert>Oops!!! We have encountered an error: "+errmsg+
                " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
            console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
        }
    });

};






    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});