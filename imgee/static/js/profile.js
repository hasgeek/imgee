$(function() {
  var uploaded = $('#uploaded-files');
  var sampleUpload = uploaded.find('.sample').html();
  var thumbs = $('.js-gallery');


  if(window.Imgee.popup) {
    var sendUploadImageUrl = function(imgUrl) {
      window.parent.postMessage(JSON.stringify({
        context: "imgee.upload",
        embed_url: imgUrl,
        }), '*');
    }

    $('.js-img-thumb').click(function (){
      var imgUrl = $(this).attr('data-url');
      sendUploadImageUrl(imgUrl);
    });
  }

  var addThumb = function(thumbData) {
    var thumb_sample = thumbs
      .find('li.gallery__image')
      .first()
      .html();
    if (!thumb_sample) location.reload();
    else {
      thumbs.prepend('<li class="gallery__image">' + thumb_sample + '</li>');
      var new_thumb = thumbs.find('li.gallery__image').first();
      new_thumb
        .find('.gallery__image__thumb__wrapper img')
        .attr('src', window.Imgee.spinnerFile);
      new_thumb.find('a').attr('href', thumbData.url);
      new_thumb.find('a').attr('title', thumbData.title);
      new_thumb.find('.title').html(thumbData.title);
      new_thumb.find('.uploaded').html(thumbData.uploaded);
      new_thumb.find('.filesize').html(thumbData.filesize);
      new_thumb.find('.imgsize').html(thumbData.imgsize);
      if(window.Imgee.popup) {
        sendUploadImageUrl(thumbData.embed_url);
      }
    }
  };
  var uploadFormSubmit = function(current, response) {
    current.find('.form').html(response.form);
    current.find('.form form').submit(function() {
      d = current.find('.form form').serializeArray();
      $.ajax({
        url: response.update_url,
        type: 'POST',
        data: d,
        dataType: 'json',
        success: function(data) {
          if (data.status) {
            current.slideUp(function() {
              $(this).remove();
              var success_alert = addAlert();
              success_alert.find('.heading').html(data.message);
              success_alert.addClass('alert--success');
              success_alert.slideDown();
              addThumb(data.image_data);
            });
          } else {
            uploadFormSubmit(current, data);
          }
        },
      });
    });
  };
  var addAlert = function() {
    uploaded.append(sampleUpload);
    var last = uploaded.find('.alert').last();
    last.find('.close').click(function() {
      $(this)
        .parent()
        .parent()
        .children('.alert--success, .alert--error')
        .slideUp(function() {
          $(this).remove();
        });
    });
    return last;
  };
  Dropzone.options.uploadimage = {
    paramName: 'upload_file',
    acceptedFiles: window.Imgee.acceptedFile,
    init: function() {
      this.on('complete', function(file) {
        var response = $.parseJSON(file.xhr.response);
        var img = $(file.previewElement)
          .find('img')
          .first();
        var title = $(file.previewElement)
          .find('.dz-filename>span')
          .first()
          .html();
        this.removeFile(file);
        var current = addAlert();
        img.load(function() {
          var src = $(this).attr('src');
          var thumb = current.find('.thumb');
          thumb.attr('src', src);
          if (src) {
            thumb.addClass('has-data');
          }
        });
        if (response.status) {
          current.find('.heading').html(response.message);
          uploadFormSubmit(current, response);
          current.addClass('alert--info');
          current.find('.close').click(function() {
            addThumb(response.image_data);
          });
        } else {
          current.find('.heading').html('Error uploading ' + title);
          current.find('.form').html(response.message);
          current.addClass('alert--error');
        }
        current.slideDown();
      });
    },
  };

  $('a.js-switch-layout').bind('click', function(e) {
    e.preventDefault();
    var selectedOptionId = $(this).attr('id');
    var showcase = $('#showcase');
    var classNames = $(this)
      .attr('class')
      .split(' ');

    if ($(this).hasClass('active')) {
      //if currently active option do nothing
      return false;
    } else {
      if (selectedOptionId == 'listview') {
        $(this).addClass('active');
        $('#gridview').removeClass('active');

        showcase.removeClass('grid');
        showcase.addClass('list');
        $('.left').addClass('span1');
        $('#row-ctrl').addClass('row');
      } else if (selectedOptionId == 'gridview') {
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
