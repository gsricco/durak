    let avatarSocial;
    let avatarka;
    chatSocket.onmessage = super_new(chatSocket.onmessage);


    if (document.querySelector(".profile-settings")) {
        const avaBtnHide = document.getElementById("avaBtnHide");
        const avaBtnShow = document.getElementById("avaBtnShow");
        const profileImage = document.getElementById("profileImage");



        function getImage() {


//            fetch(' http://127.0.0.1:8000/api/v1/avatar_default/')
//                .then(response => response.json())
//                .then((data) => {
//                    let randomNum = Math.floor(Math.random() * (data.length));
//                    avatarka = data[randomNum]['avatar_default']
//                    profileImage.setAttribute("src", `${avatarka}`);
//                });


        }

        if (avaBtnHide) {
            avaBtnHide.addEventListener("click", () => {
//                getImage();
if (is_auth === true ) {
chatSocket.send(JSON.stringify({
        "get_avatar": "all",
        "user": username,
}))
}
                avaBtnHide.style.display = "none";
                console.log(avaBtnHide.style.display)
                avaBtnShow.style.display = "block";
            });
        }


        avaBtnShow.addEventListener("click", () => {
//            fetch('http://127.0.0.1:8000/api/v1/avatar/')
//                .then(response => response.json())
//                .then((data) => {
//                    let userNow = data.filter(el => el['username'] === username)
//                    avatarSocial = userNow[0]['avatar']
//                    profileImage.setAttribute("src", `${avatarSocial}`);
//                    // profileImage.setAttribute("src", `/media/img/avatar/user/image_1`);
//                });
            chatSocket.send(JSON.stringify({
        "get_avatar": "useravatar",
        "user": username,
}))
            avaBtnShow.style.display = "none";
            avaBtnHide.style.display = "block";
        });
    }
//    let btnSaveAvatar = document.querySelector('#btnSaveImgAvatar');
//    if (btnSaveAvatar) {
//        btnSaveAvatar.addEventListener('click', () => {
//
//            fetch('http://127.0.0.1:8000/api/v1/message/',
//                {
//                    method: "POST",
//                    headers: {
//                        'Content-Type': 'application/json',
//                        'X-CSRFToken': 'f2IQIW2uLUfxPuzHdfwKJyQKBc66wMGCSTdeQkTGc3AUUepZLMX11zloNK0mhDCv'
//                    },
//                    body: JSON.stringify({avatar: 'Фото', name: 'Имя'})
//                })
//                .then(resp => resp)
//                .then(data => console.log(data))
//        })
//    }
//}
    function super_new(f){
    return function (){
        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data);

        }
        };