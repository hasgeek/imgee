$(".editable_title").editable('/edit_title', {
      indicator : 'Saving...',
      submitdata: { _method: "POST" },
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
