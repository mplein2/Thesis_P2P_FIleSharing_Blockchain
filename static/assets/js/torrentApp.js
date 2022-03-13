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

function closeGroup() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
}

function createInvite() {
    var modal = document.getElementById("createInviteModal");
    modal.style.display = "block";
}

function closeInvite() {
    var modal = document.getElementById("createInviteModal");
    modal.style.display = "none";
}

function generateInvite(groupName) {
    var ip = document.getElementById("ip").value;
    var inviteTextArea = document.getElementById("invite");
    $.ajax({
                data: {group:groupName,ip:ip}
                , type: 'post'
                , url: '/generateInvite'
                , success: function (response) {
                    inviteTextArea.value=response;
                }
            });

}
function quitGroup(groupName) {
    $.ajax({
                data: {group:groupName}
                , type: 'post'
                , url: '/quitGroup'
                , success: function (response) {
                    if (response==0){
                                    window.location.replace("/");
                                    }

                }
            });

}
function joinGroupModal() {
    var modal = document.getElementById("joinGroupModal");
    modal.style.display = "block";
}

function openShareModal() {
    var modal = document.getElementById("shareModal");
    modal.style.display = "block";
}

function closeGroupModal() {
    var modal = document.getElementById("joinGroupModal");
    modal.style.display = "none";
}
function closeShareBundle() {
    var modal = document.getElementById("shareModal");
    modal.style.display = "none";
}

function joinGroup() {
    var invite = document.getElementById("inviteHash").value;
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

function shareBundle(groupName) {
    var bundleName = document.getElementById("bundleName").value;
    var bundleDescription = document.getElementById("bundleDescription").value;
    alert("Select Folder Window is opened.");
    $.ajax({
                data: {
                        bundleName:bundleName,
                        bundleDescription:bundleDescription,
                        groupName:groupName
                      }
                , type: 'post'
                , url: '/shareBundle'
                , success: function (response) {
                    if (response==0){
                    alert("0");
                    }else{
                    //TODO FAILED ALERT
                    alert("Failed to Create Group");
                    }
                }
            });

}