$(".editable_text").editable("/edit_title", {
      indicator : 'Saving...',
      submitdata: { _method: "POST" },
      select : true,
      submit : 'OK',
      cancel : 'Cancel',
      tooltip   : 'Click to edit',
      id: 'img_name',
      name: 'img_title'
});
