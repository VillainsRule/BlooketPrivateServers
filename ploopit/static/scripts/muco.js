function muco() {
    var muco = document.getElementById("muco").value;
    if (muco === "theme") {
      var snd = new Audio('../static/audio/theme.mp3');
      snd.play();
      var msg = ""
      document.getElementById("errortxtmuco").innerHTML = msg;
      codes1form();
    } else {
      if (muco === "bsod") {
      var snd = new Audio('../static/audio/BSOD.mp3');
      snd.play();
      var msg = ""
      document.getElementById("errortxtmuco").innerHTML = msg;
      codes1form();
    } else {
    }if (muco === "404") {
        var snd = new Audio('../static/audio/404_error.mp3');
        snd.play();
        var msg = ""
        var musicon = "yes"
        document.getElementById("errortxtmuco").innerHTML = msg;
        codes1form();
      } else {
    }if (muco === "popping") {
        var snd = new Audio('https://youtu.be/vihbGaK0oK0');
        snd.play();
        var msg = ""
        document.getElementById("errortxtmuco").innerHTML = msg;
        bgchange();
      } else {
        var msg = "please try again!"
       document.getElementById("errortxtmuco").innerHTML = msg;
      }
    }
  }