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

                showcase.removeClass('grid');
                showcase.addClass('list');
                $('.left').addClass('span1');
                $('#row-ctrl').addClass('row');
            }

            else if(selectedOptionId == 'gridview') {
                $(this).addClass('active');
                $('#listview').removeClass('active');

                showcase.removeClass('list');
                showcase.addClass('grid');
                $('.left').removeClass('span1');
                $('#row-ctrl').removeClass('row');
            }

        }
    });
});
