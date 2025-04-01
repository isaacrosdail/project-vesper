
// Variable for tether text input
let tether;

document.getElementById("tether-submit").onclick = function(){
    // Get tether text from input using element id
    tether = document.getElementById("tether-text").value;
    // Now want to display said text instead of input box
    document.getElementById("tether-result").textContent = tether;
}

