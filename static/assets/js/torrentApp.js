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
    var modal = document.getElementById("myModal");
  modal.style.display = "block";
}
function createInvite() {
    var modal = document.getElementById("createInviteModal");
    modal.style.display = "block";
}
function generateInvite(groupName) {
    var inviteTextArea = document.getElementById("invite");
    $.ajax({
                data: {group:groupName}
                , type: 'post'
                , url: '/generateInvite'
                , success: function (response) {
                    inviteTextArea.value=response;
                }
            });

}
function joinGroup() {
    alert("JS join group");
    var modal = document.getElementById("myModal");
    modal.style.display = "block";
}
function createGroup() {
    var private = document.getElementById("private").value;
    var name = document.getElementById("name").value;
    $.ajax({
                data: {private: private,name:name}/*keys you need to post (sweet: newsweet)*/
                , type: 'post'
                , url: '/createGroup'
                , success: function (response) {
//                TODO redirect succsess to group
                }
            });

}