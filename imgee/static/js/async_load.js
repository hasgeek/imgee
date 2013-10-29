var load_interval = 5000; // 5 secs
function asyncload(){
    $('img.toload').each(function (){
        var img = $(this);
        var img_src = img.attr('data-src');

        $.ajax({
            url: img_src,
            type: 'GET',
            // status 200
            success: function(data){
                img.attr('src', '/static/img/spinner.gif');
            },
            // 301 is captured by "error" callback, weirdly :|
            // "... if it results in an error (including 3xx redirect)..."
            // source: http://api.jquery.com/jQuery.ajax/ 
            error: function(xhr, status, error){
                console.log(xhr);
                img.removeClass('toload');
                img.attr('src', img_src);
            }
        });
    });
    setTimeout(asyncload, load_interval);
}

asyncload();