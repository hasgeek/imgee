
var make_title_editable = function(title) {
  title.editable('/'+profile+'/edit_title', {
        indicator : 'Saving...',
        submitdata: { _method: "POST", 'csrf_token': $('#csrf_token').attr('value') },
        submit : 'OK',
        cancel : 'Cancel',
        tooltip   : 'Click to edit',
        id: 'file_name',
        name: 'file_title',
        onerror: function (settings, title_div, error){
            if (error['responseText']){
                alert(error['responseText']);
            }
            $('.editable_text').resetForm();
        }
  });
};

$(".editable_title").each(function() {
  make_title_editable($(this));
});

$('.thumbs').on('DOMNodeInserted', 'li.image', function() {
  make_title_editable($(this).find('.editable_title'));
});

$(".editable_label").each(function (){
    $(this).editable('/'+ profile + '/' + $(this).text() + '/edit', {
          indicator : 'Saving...',
          submitdata: { _method: "POST", 'csrf_token': $('#csrf_token').attr('value') },
          submit : 'OK',
          cancel : 'Cancel',
          tooltip   : 'Click to edit',
          id: 'label_id',
          name: 'label_name',
          callback: function(newlabel){
              var oldlabel = this.revert;
              History.replaceState({}, document.title, window.location.href.replace(oldlabel, newlabel));
          },
          onerror: function (settings, label_div, error){
              if (error['responseText']){
                  alert(error['responseText']);
              }
              $(this).resetForm();
          }
    });
});

