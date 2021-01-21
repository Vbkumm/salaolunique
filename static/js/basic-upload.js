$(function () {

  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });

  $("#fileupload").fileupload({
    dataType: 'json',
    sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */
    submit: function (e, data) {
        var fileType = data.files[0].name.split('.').pop(), allowdtypes = 'svg, gif, jpeg, jpg, png, heic, mp4';
        if (allowdtypes.indexOf(fileType) < 0) {
            alert('Arquivo invalido, extenções validas:svg, gif, jpeg, jpg, png, heic, mp4');
            return false;
        }
    },
    start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
      $("#modal-progress").modal("show");
    },
    stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINALIZE, HIDE THE MODAL */
      $("#modal-progress").modal("hide");
      setTimeout(function(){ window.location.reload() }, 1000);
    },
    progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
      var progress = parseInt(data.loaded / data.total * 100, 10);
      var strProgress = progress + "%";
      $(".progress-bar").css({"width": strProgress});
      $(".progress-bar").text(strProgress);
    },
    done: function (e, data) {
      if (data.result.is_valid) {
        $("#gallery tbody").prepend(
          "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
        )
      }
    },
  });

});

