let avatarSocial;
let avatarka;
let count;
chatSocket.onmessage = super_new(chatSocket.onmessage);
const userAvatar = JSON.parse(document.getElementById('user_avatar_url').textContent);
const headerAvatar = document.getElementById('ava');
const profileAvatar = document.querySelector(".profil__avatar");
const headerName = document.querySelector(".header__profile-name");
const profileName = document.querySelector(".profil__name-text");
let usernameError = document.getElementById('username_error')
if (document.querySelector(".profile-settings")) {
    const avaBtnHide = document.getElementById("avaBtnHide");
    const avaBtnShow = document.getElementById("avaBtnShow");
    const profileImage = document.getElementById("profileImage");
    if (avaBtnHide) {
        avaBtnHide.addEventListener("click", () => {
            usernameError.style.display = "none";
            if (is_auth === true) {
                if (count) {
                    message = {
                        "get_avatar": "all",
                        "user": username,
                        "c": count,
                    }
                } else {
                    message = {
                        "get_avatar": "all",
                        "user": username,
                    }
                }
                chatSocket.send(JSON.stringify(message))
            }
            avaBtnHide.style.display = "none";
            avaBtnShow.style.display = "block";
        });
    }
    avaBtnShow.addEventListener("click", () => {
        chatSocket.send(JSON.stringify({
            "get_avatar": "useravatar",
            "user": username,
        }))
        usernameError.style.display = "none";
        avaBtnShow.style.display = "none";
        avaBtnHide.style.display = "block";
    });
}
let btnSaveAvatar = document.querySelector('#btnSaveImgAvatar');
if (btnSaveAvatar) {
    btnSaveAvatar.addEventListener('click', () => {
        let save_ava = profileImage.getAttribute("src");
        let new_username = document.getElementById("new_username").value;
        let message = {
            "set_avatar": `${save_ava}`,
            "user": username,
            "new_username": new_username,
        }
        if (save_ava === userAvatar) {
            message.set_avatar = userAvatar
            message.basic = false
        }
        if (count) {
            message.avatarId = count
        }
        chatSocket.send(JSON.stringify(
            message
        ))
    })
}

function super_new(f) {
    return function () {
        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data);
        if (data.b_avatar) {
            count = data.c
            avatarka = data.b_avatar
            avatarSocial = ''
            profileImage.setAttribute("src", `${avatarka}`);
        }
        if (data.u_avatar) {
            avatarSocial = data.u_avatar
            avatarka = ''
            profileImage.setAttribute("src", `${avatarSocial}`);
        }
        if (data.set_avatar) {
            if (data.new_username !== profileName.querySelector('span').innerHTML){
                profileName.querySelector('span').innerText = data.new_username
            headerName.querySelector('span').innerText = data.new_username
            }
            headerAvatar.srcset = data.set_avatar
            profileAvatar.querySelector('img').setAttribute('src', data.set_avatar)
        }
        if (data.error){

            usernameError.style.display = 'block';
        }
    }
}