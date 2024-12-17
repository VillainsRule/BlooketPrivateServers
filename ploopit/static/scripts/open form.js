//alert("START OF THE SCRIPT")
window.onload = Closeform()
function Openform(){
    //alert("INSIDE OPENFORM FUNCTION")
    document.getElementById('buy').style.visibility = 'visible';
  }

  function Closeform(){
    //alert("INSIDE OPENFORM FUNCTION")
    document.getElementById('buy').style.visibility = 'hidden';
  }

function Openform2(){
    //alert("INSIDE OPENFORM2 FUNCTION")
    document.getElementById('news5').style.visibility = 'visible';
    opacity1();
  }

  function Closeform2(){
    //alert("INSIDE CLOSEFORM2 UNCTION")
    document.getElementById('news').style.visibility = 'hidden';
    opacity0();
  }

  function opacity0(){
    //alert("INSIDE OPACITY0 FUNCTION")
    document.getElementById('closenews').style.visibility = 'hidden';
    Closeform2();
  }

  function opacity1(){
    //alert("INSIDE OPENFORM2 FUNCTION")
    document.getElementById('closenews').style.visibility = 'visible';
    Openform2();
  }