$(function() {
  var uploaded = $('#uploaded-files');
  var sample_upload = uploaded.find('.sample').html();
  var thumbs = $('.gallery');

  var valign_thumb = function(thumb, loaded, img_onload) {
    var t = thumb.find('.gallery__image__wrapper__thumbnail img');
    var m = (75 - t.height()) / 2;
    if (m < 0) m = 0;
    t.css({ 'margin-top': m });
    if (
      typeof loaded == 'undefined' ||
      (typeof loaded == 'boolean' && !loaded)
    ) {
      thumb.find('.gallery__image__wrapper__thumbnail img').load(function() {
        if (typeof img_onload == 'string') $(this).attr('src', img_onload);
        valign_thumb(thumb, true, img_onload);
      });
    }
  };

  var align_all = function(loaded) {
    thumbs.find('li.gallery__image').each(function() {
      valign_thumb($(this), loaded);
    });
  };

  align_all();
  $('#gridview').click(function() {
    align_all(true);
  });

  var add_thumb = function(thumb_data) {
    var thumb_sample = thumbs
      .find('li.gallery__image')
      .first()
      .html();
    if (!thumb_sample) location.reload();
    else {
      thumbs.prepend('<li class="gallery__image">' + thumb_sample + '</li>');
      var new_thumb = thumbs.find('li.gallery__image').first();
      valign_thumb(new_thumb, false, thumb_data.thumb_url);
      new_thumb
        .find('.gallery__image__wrapper__thumbnail img')
        .attr('src', window.Imgee.spinnerFile);
      new_thumb.find('a').attr('href', thumb_data.url);
      new_thumb.find('a').attr('title', thumb_data.title);
      new_thumb.find('.title').html(thumb_data.title);
      new_thumb.find('.uploaded').html(thumb_data.uploaded);
      new_thumb.find('.filesize').html(thumb_data.filesize);
      new_thumb.find('.imgsize').html(thumb_data.imgsize);
    }
  };
  var upload_form_submit = function(current, response) {
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
              var success_alert = add_alert();
              success_alert.find('.heading').html(data.message);
              success_alert.addClass('alert--success');
              success_alert.slideDown();
              add_thumb(data.image_data);
            });
          } else {
            upload_form_submit(current, data);
          }
        },
      });
    });
  };
  var add_alert = function() {
    uploaded.append(sample_upload);
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
        var current = add_alert();
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
          upload_form_submit(current, response);
          current.addClass('alert--info');
          current.find('.close').click(function() {
            add_thumb(response.image_data);
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
