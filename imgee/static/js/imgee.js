$(function() {
  var imgWidth = Math.floor($('.js-gallery').width()/4);
  var nextPage = 1;

  var resizeThumbImg = function() {
    $('.gallery__image').width(imgWidth).height(imgWidth);
  }

  resizeThumbImg();

  $('#loadmore').appear().on('appear', function (event) {
    if(nextPage) {
      $.ajax({
        url: window.Imgee.paginateUrl + '?page=' + nextPage,
        type: 'GET',
        success: function(data) {
          nextPage = data.next_page;
          if(!nextPage) {
            $('.js-gallery').find('#loadmore').addClass('mui--hide');
          }
          $('.js-gallery').find('#loadmore').before(data.files);
          resizeThumbImg();
          if( $('#loadmore').is(':appeared')) {
            $.force_appear()
          }
        },
      });
    }
  });

  // Initial load of images
  $.force_appear();

  var sendUploadImageUrl = function(imgUrl) {
    window.parent.postMessage(JSON.stringify({
      context: "imgee.upload",
      embed_url: imgUrl,
      }), '*');
  }

  $('body').on('click', '.js-img-thumb', function () {
    var imgUrl = $(this).attr('data-url');
    $(this).find('.gallery__image__wrapper__thumb__icon').attr('checked', true);
    sendUploadImageUrl(imgUrl);
  });

  var addNewThumb = function() {
    var innerThumb = $('.js-gallery')
      .find('li.gallery__image.image')
      .first()
      .html();
    var newThumb = $(
        '<li class="gallery__image image"></li>'
      )
        .html(innerThumb);
    $('.js-gallery').find('li.gallery__image--dropzone').after(newThumb);
    newThumb
      .find('.gallery__image__wrapper__thumb__img')
      .addClass('spinner')
      .attr('src', window.Imgee.spinnerFile);
    resizeThumbImg();
    return newThumb;
  }

  var addThumb = function(thumbData, thumbDom) {
    thumbDom
      .find('.gallery__image__wrapper__thumb__img')
      .removeClass('spinner')
      .attr('src', thumbData.image_data.embed_url);
    thumbDom.find('.gallery__image__wrapper__thumb__icon').attr('checked', true);
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
