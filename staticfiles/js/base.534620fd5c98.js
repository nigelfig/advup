function disable_on_click() {
    var x = document.getElementsByClassName('btn');
    var i;
    for (i = 0; i < x.length; i++) {
      x[i].setAttribute("disabled", "disabled")
    }
    
  }