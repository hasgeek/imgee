
$(".editable_title").editable('/'+profile+'/edit_title', {
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

$(".editable_label").editable('/'+profile+'/edit_label', {
      indicator : 'Saving...',
      submitdata: { _method: "POST", 'csrf_token': $('#csrf_token').attr('value') },
      submit : 'OK',
      cancel : 'Cancel',
      tooltip   : 'Click to edit',
      id: 'label_id',
      name: 'label',
      callback: function(newlabel){
          var oldlabel = this.revert;
          History.replaceState({}, document.title, window.location.href.replace(oldlabel, newlabel));
      },
      onerror: function (settings, label_div, error){
          if (error['responseText']){
              alert(error['responseText']);
          }
          $('.editable_label').resetForm();
      }
});

