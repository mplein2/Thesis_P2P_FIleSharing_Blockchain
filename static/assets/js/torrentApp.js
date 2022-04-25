function start() {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if (this.responseText == "1"){
        alert("Download Manager Active");
        }
        else{
        alert("Download Manager Not Active");
        }

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

function ValidateIp(ipaddress){
 if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ipaddress))
  {
    return (true)
  }
return (false)
}

function generateInvite(groupName) {
    var ip = document.getElementById("ip").value;
    var inviteTextArea = document.getElementById("invite");
    if (ValidateIp(ip)==true){
     $.ajax({
                data: {group:groupName,ip:ip}
                , type: 'post'
                , url: '/generateInvite'
                , success: function (response) {
                    inviteTextArea.value=response;
                }
            });
    }
    else{
alert("You have entered an invalid IP address!")
    }
}

function deleteBundle(bundleId,groupId) {
    $.ajax({
                data: {bundleId:bundleId, groupId:groupId}
                , type: 'post'
                , url: '/deleteBundle'
                , success: function (response) {
 Swal.fire({
                          title: "Bundle Deleted!",
                            icon: 'success'
                        }).then(function() {
                        window.location.reload();
                    });
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

function openSettingsModal() {
    var modal = document.getElementById("settingsModal");
    modal.style.display = "block";
}

function closeSettingsModal() {
    var modal = document.getElementById("settingsModal");
    modal.style.display = "none";
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
                    if (response=="1"){
                    window.location.reload();
                    }else{
                    alert("No responses , try again later.")
                    }
                }
            });
}

function createGroup() {
    var name = document.getElementById("name").value;
    $.ajax({
                data: {name:name}
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
                    closeShareBundle();
                        Swal.fire({
                          title: "Bundle Shared!",
                            icon: 'success'
                        }).then(function() {
                        window.location.reload();
                    });

                    }else{
                    //TODO FAILED ALERT
                    alert("Failed to Create Group");
                    }
                }
            });

}

function getBundle(bundleId,groupId,userIp) {
alert("JS OK");
    $.ajax({
                data: {
                        bundleId:bundleId,
                        groupId:groupId,
                        userIp:userIp
                      }
                , type: 'post'
                , url: '/getBundle'
                , success: function (response) {
                    if (response==0){
                    alert("0");
                    }else{
                    //TODO FAILED ALERT
                  alert("not 0");
                    }
                }
            });

}

function selectDownloadLocation() {
    var downloadLocationElement = document.getElementById("downloadLocation");
    alert("Select Folder Window is opened.");
    $.ajax({
                data: {
                      }
                , type: 'post'
                , url: '/selectDownloadLocation'
                , success: function (response) {
                    if (response==0){
                    alert("0");
                    }else{
                        downloadLocationElement.value = response;
                    }
                }
            });

}

function banUser(groupId,userIp){
//alert("ban from group"+groupId+" ,user :"+userIp);
Swal.fire({
  title: 'Are you sure you want to ban '+userIp+' ?',
  showCancelButton: true,
  confirmButtonText: 'Confirm',
}).then((result) => {
  /* Read more about isConfirmed, isDenied below */
  if (result.isConfirmed) {
      $.ajax({
                data: {
                        group:groupId,
                        userip:userIp
                      }
                , type: 'post'
                , url: '/banUser'
                , success: function (response) {
                    if (response==0){
                        Swal.fire('Success!', 'Change will appear shortly.', 'success');
                    }else{
                    //TODO FAILED ALERT
                    alert("Failed");
                    }
                }
            });

  }
});
}

function unbanUser(groupId,userIp){
//alert("unban from group"+groupId+" ,user :"+userIp);
Swal.fire({
  title: 'Are you sure you want to unban '+userIp+' ?',
  showCancelButton: true,
  confirmButtonText: 'Confirm',
}).then((result) => {
  /* Read more about isConfirmed, isDenied below */
  if (result.isConfirmed) {
      $.ajax({
                data: {
                        group:groupId,
                        userip:userIp
                      }
                , type: 'post'
                , url: '/unbanUser'
                , success: function (response) {
                    if (response==0){
                        Swal.fire('Success!', 'Change will appear shortly.', 'success');
                    }else{
                    //TODO FAILED ALERT
                    alert("Failed");
                    }
                }
            });
  }
});
}

function addAdmin(groupId,userIp){
//alert("addAdmin from group"+groupId+" ,user :"+userIp);
Swal.fire({
  title: 'Are you sure you want to add  '+userIp+' as admin ?',
  showCancelButton: true,
  confirmButtonText: 'Confirm',
}).then((result) => {
  /* Read more about isConfirmed, isDenied below */
  if (result.isConfirmed) {
      $.ajax({
                data: {
                        group:groupId,
                        userip:userIp
                      }
                , type: 'post'
                , url: '/addAdmin'
                , success: function (response) {
                    if (response==0){
                        Swal.fire('Success!', 'Change will appear shortly.', 'success');
                    }else{
                    //TODO FAILED ALERT
                    alert("Failed");
                    }
                }
            });
  }
});
}

function removeAdmin(groupId,userIp){
//alert("removeAdmin from group"+groupId+" ,user :"+userIp);
Swal.fire({
  title: 'Are you sure you want to remove '+userIp+' from admins ?',
  showCancelButton: true,
  confirmButtonText: 'Confirm',
}).then((result) => {
  /* Read more about isConfirmed, isDenied below */
  if (result.isConfirmed) {
      $.ajax({
                data: {
                        group:groupId,
                        userip:userIp
                      }
                , type: 'post'
                , url: '/removeAdmin'
                , success: function (response) {
                    if (response==0){
                        Swal.fire('Success!', 'Change will appear shortly.', 'success');
                    }else{
                    //TODO FAILED ALERT
                    alert("Failed");
                    }
                }
            });
  }
});
}