window.onload = consolelogs()
function consolelogs() {
    console.log(`%cYou should NOT BE HERE`, `font-size: 35px; color: red;`);
    console.log(`%cThis is a browser feature intended for developers. If someone told you to copy and paste something here to enable a Ploopit feature or "hack" someone else's account, it is most likely a scam and will give them access to your account, or any other data.`, `font-size: 20px;`);
    console.log(`%cIf you ignore this message and the script does work, PLEASE contact a ploopit developer immediately, these hacks effect trading and the economy of ploopit.`, `font-size: 20px;`);
    console.log(`%c Ploopit is Running v0.52 {beta}`,  `font-size: 35px; color: rgb(3, 116, 116);`);
  }

  window.addEventListener('load', function() {
    //this.alert("LOADED")
    const loadingScreen = document.querySelector('#loading-screen');
    loadingScreen.style.display = 'none';
  });

document.getElementById("action").addEventListener('click', function() {
    this.alert("Clicked")
    const loadingScreen = document.querySelector('#loading-screen');
    loadingScreen.style.display = 'none';
  });

  window.onload = error404()
  error404()
    //this.alert("LOADED")
    const loadingScreen = document.querySelector('#error404');
    loadingScreen.style.display = 'none';
