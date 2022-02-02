function start() {
    alert("JS RECEIVED START");
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        alert("AJAX COMPLETED, RESPONSE:"+this.responseText);

        }
    xhttp.open("POST", "/start", true);
    xhttp.send();

}
function addGroup() {
    alert("JS add group");
    var modal = document.getElementById("myModal");
  modal.style.display = "block";

}
function joinGroup() {
    alert("JS add group");
    var modal = document.getElementById("myModal");
  modal.style.display = "block";
}
function createGroup() {
    var private = document.getElementById("private").value;
    var name = document.getElementById("name").value;
    alert(private);
    alert(name);
    $.ajax({
                data: {private: private,name:name}/*keys you need to post (sweet: newsweet)*/
                , type: 'post'
                , url: '/createGroup'
                , success: function (response) {
                  alert(response);
                }
            });

}