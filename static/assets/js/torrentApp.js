function start() {
    alert("JS RECEIVED START");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        alert("AJAX COMPLETED, RESPONSE:"+this.responseText);

        }
    xhttp.open("POST", "/start", true);
    xhttp.send();

}