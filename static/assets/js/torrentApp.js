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
function joinGroupModal() {
    var modal = document.getElementById("joinGroupModal");
    modal.style.display = "block";
}
function joinGroup() {
    var invite = document.getElementById("inviteHash").value;
//    eJyLjlYyNDfTMzIyB2ITPUMDc6XYWAAzNASo
    $.ajax({
                data: {invite: invite}
                , type: 'post'
                , url: '/joinGroup'
                , success: function (response) {
                    if (response==0){
                    window.location.replace("/groups?group="+name);
                    }else{
                    //TODO FAILED ALERT
                    alert("Failed to Join Group")
                    }
                }
            });
}
function createGroup() {
    var private = document.getElementById("private").value;
    var name = document.getElementById("name").value;
    $.ajax({
                data: {private: private,name:name}
                , type: 'post'
                , url: '/createGroup'
                , success: function (response) {
                    if (response==0){
                    window.location.replace("/groups?group="+name);
                    }else{
                    //TODO FAILED ALERT
                    alert("Failed to Create Group")
                    }
                }
            });

}