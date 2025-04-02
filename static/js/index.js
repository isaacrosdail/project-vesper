
// Variable for tether text input
let tether;

// Constant for tether-submit button
const tetherSubmitBtn = document.getElementById("tether-submit");
// Variables for tether-text and tether-result
let tetherText = document.getElementById("tether-text");
let tetherResult = document.getElementById("tether-result");

tetherSubmitBtn.onclick = () => {
    // Get tether text from input using element id
    tether = document.getElementById("tether-text").value;
    // Now want to display said text instead of input box
    document.getElementById("tether-result").textContent = tether;
    // And hide the input text box and submit button
    tetherText.classList.add("hidden");
    tetherSubmitBtn.classList.add("hidden");
}

tetherResult.onclick = () => {
    tetherResult.classList.remove("hidden");
    tetherText.classList.remove("hidden");
    tetherSubmitBtn.classList.remove("hidden");
}