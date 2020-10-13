$(function() {
  var imgGallery = $('.js-gallery');
  var imgWidth = imgGallery.width()/4;

  $('.gallery__image').width(imgWidth).height(imgWidth);

  var sendUploadImageUrl = function(imgUrl) {
    window.parent.postMessage(JSON.stringify({
      context: "imgee.upload",
      embed_url: imgUrl,
      }), '*');
  }

  var removeSelected = function() {
    $('.gallery__image__thumb').removeClass('gallery__image__thumb--selected');
  };

  $('body').on('click', '.js-img-thumb', function () {
    var imgUrl = $(this).attr('data-url');
    removeSelected();
    $(this).addClass('gallery__image__thumb--selected');
    $(this).parents('.gallery__image--popup')
      .addClass('gallery__image--highlight');
    sendUploadImageUrl(imgUrl);
  });

  var addNewThumb = function() {
    var innerThumb = imgGallery
      .find('li.gallery__image--popup')
      .first()
      .html();
    var newThumb = $(
        '<li class="gallery__image gallery__image--popup gallery__image--highlight"></li>'
      )
        .html(innerThumb);
    imgGallery.find('li.gallery__image--dropzone').after(newThumb);
    newThumb
      .find('.gallery__image__thumb__wrapper img')
      .addClass('spinner')
      .attr('src', window.Imgee.spinnerFile);
    var newThumbDom = imgGallery.find('li.gallery__image--highlight').first();
    newThumbDom.width(imgWidth).height(imgWidth);
    return newThumbDom;
  }

  var addThumb = function(thumbData, thumbDom) {
    thumbDom
      .find('.gallery__image__thumb__wrapper img')
      .removeClass('spinner')
      .attr('src', thumbData.image_data.embed_url);
    removeSelected();
    thumbDom.find('.gallery__image__thumb')
      .addClass('gallery__image__thumb--selected');
    sendUploadImageUrl(thumbData.image_data.embed_url);
  };

  Dropzone.options.uploadimage = {
    paramName: 'upload_file',
    acceptedFiles: window.Imgee.acceptedFile,
    init: function() {
      var sampleThumb;
      this.on('addedfile', function() {
        sampleThumb = addNewThumb();
      });
      this.on('complete', function(file) {
        var response = $.parseJSON(file.xhr.response);
        this.removeFile(file);
        if (response.status) {
          addThumb(response, sampleThumb);
        }
      });
    },
  };
});
