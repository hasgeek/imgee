window.Imgee = {};

$(document).ready(function() {
  $('.js-expandable-control').on('click', function() {
    $(this)
      .parent('.js-expandable-wrapper')
      .find('.js-expandable')
      .toggleClass('expandable__content--full-height ');
    $(this)
      .find('.js-collapsible-icon')
      .toggleClass('mui--hide');
  });

  $('#js-sidebar-control').on('click', function(e) {
    e.stopPropagation();
    $('#js-sidebar-menu').addClass('sidebar-menu--open');
  });

  $('body').on('click', function(e) {
    if (
      $('#js-sidebar-menu').hasClass('sidebar-menu--open') &&
      !$(e.target).is('#js-sidebar-control') &&
      !$.contains($('#js-sidebar-menu')[0], e.target)
    ) {
      $('#js-sidebar-menu').removeClass('sidebar-menu--open');
    }
  });

  if (document.getElementById('js-sidebar-menu')) {
    var start = {},
      end = {};

    document.body.addEventListener(
      'touchstart',
      function(e) {
        start.x = e.changedTouches[0].clientX;
        start.y = e.changedTouches[0].clientY;
      },
      { passive: true }
    );

    document.body.addEventListener(
      'touchend',
      function(e) {
        end.y = e.changedTouches[0].clientY;
        end.x = e.changedTouches[0].clientX;

        var xDiff = end.x - start.x;
        var yDiff = end.y - start.y;
        var sideBarElem = document.getElementById('js-sidebar-menu');

        if (Math.abs(xDiff) > Math.abs(yDiff) && sideBarElem) {
          if (xDiff > 0 && start.x <= 80) {
            sideBarElem.classList.add('sidebar-menu--open');
          } else {
            sideBarElem.classList.remove('sidebar-menu--open');
          }
        }
      },
      { passive: true }
    );
  }

  $('.js-open-form').on('click', function(event) {
    event.preventDefault();
    $('#newlabel-form').modal('show');
  });

  var make_title_editable = function(title) {
    title.editable('/' + window.Imgee.profile + '/edit_title', {
      indicator: 'Saving...',
      submitdata: {
        _method: 'POST',
        csrf_token: $('#csrf_token').attr('value'),
      },
      submit: 'OK',
      cancel: 'Cancel',
      tooltip: 'Click to edit',
      id: 'file_name',
      name: 'file_title',
      onerror: function(settings, title_div, error) {
        if (error['responseText']) {
          alert(error['responseText']);
        }
        $('.editable_text').resetForm();
      },
    });
  };

  $('.editable_title').each(function() {
    make_title_editable($(this));
  });

  $('.gallery').on('DOMNodeInserted', 'li.gallery__image', function() {
    make_title_editable($(this).find('.editable_title'));
  });

  $('.editable_label').each(function() {
    $(this).editable(
      '/' + window.Imgee.profile + '/' + $(this).text() + '/edit',
      {
        indicator: 'Saving...',
        submitdata: {
          _method: 'POST',
          csrf_token: $('#csrf_token').attr('value'),
        },
        submit: 'OK',
        cancel: 'Cancel',
        tooltip: 'Click to edit',
        id: 'label_id',
        name: 'label_name',
        callback: function(newlabel) {
          var oldlabel = this.revert;
          window.history.replaceState(
            {},
            document.title,
            window.location.href.replace(oldlabel, newlabel)
          );
        },
        onerror: function(settings, label_div, error) {
          if (error['responseText']) {
            alert(error['responseText']);
          }
          $(this).resetForm();
        },
      }
    );
  });
});
