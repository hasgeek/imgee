$(function() {
  $('input#img_width').width(30);
  $('input#img_height').width(30);
  $('input#img_link').width(420);

  function set_resize_url(a) {
    var file_url = a.attr('href');
    var url_with_size =
      file_url +
      '?size=' +
      $('input#img_width').val() +
      'x' +
      ($('input#img_height').val() || '0');
    $("input:text[name='direct-link']").val(url_with_size);
    $("input:text[name='html-code']").val(
      '<a href="' + url_with_size + '"><img src="' + url_with_size + '" />'
    );
  }

  $('a#img_link').click(function(event) {
    event.preventDefault();
    set_resize_url($(this));
  });

  $('#resize li button').click(function() {
    var text = $(this).text();
    var current_direct_link = $("input:text[name='direct-link']").val();

    if (current_direct_link.search('size') != '-1') {
      current_direct_link = current_direct_link.split('?size=')[0];
    }
    var new_link = current_direct_link + '?size=' + text;

    $("input:text[name='direct-link']").val(new_link);
    $("input:text[name='html-code']").val(
      '<a href="' + new_link + '"><img src="' + new_link + '" />'
    );
  });

  $('#resize li#img-size-original button').click(function() {
    var current_direct_link = $("input:text[name='direct-link']").val();

    if (current_direct_link.search('size') != '-1') {
      current_direct_link = current_direct_link.split('?size=')[0];
    }
    var new_link = current_direct_link;

    $("input:text[name='direct-link']").val(new_link);
    $("input:text[name='html-code']").val('<img src="' + new_link + '" />');
  });
});
