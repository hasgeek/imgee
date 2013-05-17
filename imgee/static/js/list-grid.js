$(document).ready(function(){
    $('a.switcher').bind('click', function(e){
        e.preventDefault();

        var selectedOptionId = $(this).attr('id');
        var showcase = $('ul#showcase');
        var classNames = $(this).attr('class').split(' ');

        if($(this).hasClass('active')) {
            //if currently active option do nothing
            return false;
        } else {
            
            if(selectedOptionId == 'listview') {
                $(this).addClass('active');
                $('#gridview').removeClass('active');
                $('#showcase').addClass('row');
                $('.image').addClass('span8');

                showcase.removeClass('grid');
                showcase.addClass('list');
            }

            else if(selectedOptionId == 'gridview') {
                $(this).addClass('active');
                $('#listview').removeClass('active');
                $('#showcase').removeClass('row');
                $('.image').removeClass('span8');

                showcase.removeClass('list');
                showcase.addClass('grid');
            }

        } 
    });
});