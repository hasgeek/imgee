$(function() {
  var imgWidth = Math.floor($('.js-gallery').width()/3);
  var nextPage = 2;

  var resizeThumbImg = function() {
    $('.gallery__image').width(imgWidth).height(imgWidth);
  }

  resizeThumbImg();

  $('#loadmore').appear().on('appear', function (event) {
    $.ajax({
      url: window.Imgee.paginateUrl + '?page=' + nextPage,
      type: 'GET',
      success: function(data) {
        nextPage = data.current_page + 1;
        console.log('nextPage', nextPage);
        $('.js-gallery').find('#loadmore').before(data.files);
        resizeThumbImg();
      },
    });
  });

  $.force_appear();

  var sendUploadImageUrl = function(imgUrl) {
    window.parent.postMessage(JSON.stringify({
      context: "imgee.upload",
      embed_url: imgUrl,
      }), '*');
  }

  var removeSelected = function() {
    $('.gallery__image__wrapper__thumb').removeClass('gallery__image__thumb--selected');
  };

  $('body').on('click', '.js-img-thumb', function () {
    var imgUrl = $(this).attr('data-url');
    removeSelected();
    $(this).addClass('gallery__image__wrapper__thumb--selected');
    sendUploadImageUrl(imgUrl);
  });

  var addNewThumb = function() {
    var innerThumb = $('.js-gallery')
      .find('li.gallery__image.img')
      .first()
      .html();
    var newThumb = $(
        '<li class="gallery__image img"></li>'
      )
        .html(innerThumb);
    $('.js-gallery').find('li.gallery__image--dropzone').after(newThumb);
    newThumb
      .find('.gallery__image__wrapper__thumb img')
      .addClass('spinner')
      .attr('src', window.Imgee.spinnerFile);
    var newThumbDom = $('.js-gallery').find('li.gallery__image.img').first();
    resizeThumbImg();
    return newThumbDom;
  }

  var addThumb = function(thumbData, thumbDom) {
    thumbDom
      .find('.gallery__image__wrapper__thumb img')
      .removeClass('spinner')
      .attr('src', thumbData.image_data.embed_url);
    removeSelected();
    thumbDom.find('.gallery__image__wrapper__thumb')
      .addClass('gallery__image__wrapper__thumb-selected');
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
