"use strict";

$(function () { // shorthand for $( document ).ready()

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

function showInputPanel() {
    var delay = 0;
    if ($('#result_panel').is(':visible')) {
        $('#result_panel').fadeOut(800);
        delay = 800;
    }
    $('#input_panel').delay(delay).fadeIn(800);
}

function showResultPanel(result_fragment) {
    var delay = 0;
    if ($('#input_panel').is(':visible')) {
        $('#input_panel').fadeOut(800);
        delay = 800;
    }
    $('#result_panel').html(result_fragment);
    $('#result_panel').delay(delay).fadeIn(800);
}

Dropzone.options.uploadDropzone = {
    maxFilesize: 20,

    // these options limit the dropzone to a single file
    maxFiles: 1,
    uploadMultiple: false,
    parallelUploads: 1,

    autoProcessQueue: true,
    addRemoveLinks: true,
    dictDefaultMessage: 'Drop your photo here',
    dictResponseError: 'Server not Configured',
    acceptedFiles: ".jpg,.jpeg,image/jpeg",
    init:function(){
      var self = this;
      // config
      self.options.addRemoveLinks = true;
      self.options.dictRemoveFile = "Delete";
      //New file added
      self.on("addedfile", function (file) {
        console.log('new file added ', file);
      });
      // Send file starts
      self.on("sending", function (file) {
        console.log('upload started ', file);
        var csrftoken = $('meta[name=csrf-token]').attr('content');
        // console.log('csrftoken ', csrftoken);
        file.xhr.setRequestHeader("X-CSRFToken", csrftoken);
        $('.meter').show();
      });

      // File upload Progress
      self.on('totaluploadprogress', function (progress) {
        console.log("progress ", progress);
        $('.roller').width(progress + '%');
      });

      self.on("success", function (file, response) {
        console.log('successfully uploaded ', file);
        self.processQueue();
        console.log('response', response);
        // window.location = response.redirect;
        showResultPanel(response.result_fragment);

        navToHash(response.img_id);

      });

      self.on("error", function (file, errorMessage, xhr) {
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
      });

      self.on("removedfile", function (file) {
        var error_panel = $('.error_panel');
        error_panel.fadeOut(800);
      });

      self.on("complete", function (file) {
        console.log('complete ', file);
      });

      self.on("queuecomplete", function (progress) {
        $('.meter').delay(999).slideUp(999);
      });

      // On removing file
      self.on("removedfile", function (file) {
        console.log(file);
      });
    }
}

}); // close wrapper function