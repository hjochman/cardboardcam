"use strict";

$(function () { // open wrapper function

$(window).on('hashchange', function(){
    // Called every time the window.location #hash changes.

    var hash = window.location.hash;
    if (hash && hash != "") {
        renderResult(hash);
    } else {
        showInputPanel();
    }
});

// we trigger hashchange explicitly on initial page load
// to set panels to the correct state
$(window).trigger('hashchange');

// tab toggle event
$('a[data-toggle="tab"]').on('shown.bs.tab', function (event) {
    console.log($(event.target).attr('aria-controls'));
    navToHash('');
    Dropzone.forElement("#split-upload-dropzone").removeAllFiles(true);
    Dropzone.forElement("#join-upload-dropzone").removeAllFiles(true)
    showInputPanel();
});

function renderResult(hash) {
    // Trim initial hash symbol #
    var img_id = hash.substring(1, hash.length);
    $.ajax({
      method: "GET",
      dataType: "html",
      url: location_no_hash() + img_id,
      success: function (data, textStatus, jqXHR) {
          showResultPanel(data);
      }
    });
}

// gets the full window.location without the #hash part
function location_no_hash() {
    var url = location.protocol+'//'+location.host+location.pathname+(location.search?location.search:"")
    return url;
}

function navToHash(hash) {
    if (history.pushState) {
      history.pushState(null, null, '#'+hash);
    }
    else {
       window.location.hash = '#'+hash;
    }
}

function activeTabName() {
    if ($("ul#split_tab_buton li.active")) { console.log('split'); return 'split'; }
    if ($("ul#join_tab_buton li.active")) { console.log('join'); return 'join'; }
}

function showInputPanel() {
    var delay = 0;
    //var tabname = activeTabName();
    var result_panel = $('#result_panel');
    if (result_panel.is(':visible')) {
        // result_panel.fadeOut(800);
        result_panel.slideUp(400);
        delay = 0;
    }
    $('#split_input_panel').delay(delay).fadeIn(800);
    $('#join_input_panel').delay(delay).fadeIn(800);
}

function showResultPanel(result_fragment) {
    var delay = 0;
    if ($('#split_input_panel').is(':visible')) {
        $('#split_input_panel').fadeOut(800);
        delay = 800;
    }
    if ($('#join_input_panel').is(':visible')) {
        $('#join_input_panel').fadeOut(800);
        delay = 800;
    }
    // var tabname = activeTabName();
    var result_panel = $('#result_panel');
    result_panel.html(result_fragment);
    result_panel.delay(delay).fadeIn(800);
}

function _dzSend (file) {
    console.log('upload started ', file);
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    // console.log('csrftoken ', csrftoken);
    file.xhr.setRequestHeader("X-CSRFToken", csrftoken);
    $('.meter').show();
}

function _dzSuccess (file, response) {
    console.log('successfully uploaded ', file);
    self.processQueue();
    console.log('response', response);
    // window.location = response.redirect;
    showResultPanel(response.result_fragment);
    navToHash(response.img_id);
}

function _dzError (file, errorMessage, xhr) {
    if (xhr && xhr.status != 200) {
      console.log('error message: ', xhr.statusText);
      console.log('error status: ', xhr.status);
      showResultPanel(errorMessage);
      // navToHash(xhr.status)
    } else {
      if (file.status == 'error') {
        console.log('complete status: ', file.status);
        var error_panel = $('.error_panel');
        error_panel.find('#error_message').html(errorMessage);
        error_panel.fadeIn(800);
      }
    }
}

function _dzRemovedFile (file) {
    var error_panel = $('.error_panel');
    error_panel.fadeOut(800);
}

function _countFiletypes(files) {
    var jpeg_count = 0;
    var mp4_count = 0;
    for (var f in files) {
      var fo = files[f];
      if (fo.type == 'image/jpeg') {
        jpeg_count++;
      }
      if (fo.type == 'video/mp4' || fo.type == 'audio/mp4') {
        mp4_count++;
      }
    }

    return { jpeg: jpeg_count,
             mp4: mp4_count };
}

Dropzone.options.splitUploadDropzone = {
    // thumbnailWidth: 600,
    // thumbnailHeight: 114,  // null,

    maxFilesize: 20,

    // these options limit the dropzone to a single file
    maxFiles: 1,
    uploadMultiple: false,
    parallelUploads: 1,

    autoProcessQueue: true,
    addRemoveLinks: true,
    dictDefaultMessage: 'Drop your photo here',
    dictResponseError: 'Server not Configured',
    acceptedFiles: ".jpg,.jpeg",
    init:function(){
      var self = this;
      // config
      self.options.addRemoveLinks = true;
      self.options.dictRemoveFile = "Delete";

      // Send file starts
      self.on("sending", _dzSend);

      self.on("success", _dzSuccess);

      self.on("error", _dzError);

      self.on("removedfile", _dzRemovedFile);
    }
}

Dropzone.options.joinUploadDropzone = {
    // thumbnailWidth: 600,
    // thumbnailHeight: 114,  // null,

    maxFilesize: 40,

    // these options limit the dropzone to a single file
    maxFiles: 3,
    uploadMultiple: true,
    parallelUploads: 100,

    autoProcessQueue: false,
    addRemoveLinks: true,
    dictDefaultMessage: 'Drop your photos (and audio) here',
    dictResponseError: 'Server not Configured',
    acceptedFiles: ".jpg,.jpeg,.mp4,.m4a",
    init:function(){
      var self = this;
      // config
      self.options.addRemoveLinks = true;
      self.options.dictRemoveFile = "Delete";

      var submitButton = $("#join-submit");
      submitButton.on("click", function() {
        self.processQueue();
      });

      function updateSubmitButtonVisibility() {
        var numberof = _countFiletypes(self.files);

        if (numberof.jpeg > 2 || numberof.mp4 > 1) {
          submitButton.fadeOut(400);
        }
        if (numberof.jpeg == 2 && numberof.mp4 <= 1) {
          submitButton.fadeIn(400);
        }
      }

      // only show the submit button only when there are the right files
      self.on("addedfile", function(file) {
        updateSubmitButtonVisibility();
      });
      self.on("removedfile", function(file) {
        updateSubmitButtonVisibility();
      });

      // Send file starts
      //self.on("sendingmultiple", _dzSend);

      self.on("successmultiple", _dzSuccess);

      self.on("errormultiple", _dzError);
    }
}

}); // close wrapper function