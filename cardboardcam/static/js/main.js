
Dropzone.options.uploadDropzone = {
    maxFilesize: 16,

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
        window.location = response.redirect;
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