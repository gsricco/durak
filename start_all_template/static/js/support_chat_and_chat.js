import newUserMessage from './admin_chat.js'
const ava = document.getElementById('ava').getAttribute('src');
const list = document.querySelector('.list');
const rubin = JSON.parse(document.getElementById('kamen').textContent);
const is_auth = JSON.parse(document.getElementById('auth-user').textContent);
const username = JSON.parse(document.getElementById('username').textContent);
const messageBlock = document.querySelector('.online-chat__list')
const buttonSend = document.querySelector('.online-chat__icon-arrow')
const messageInput = document.querySelector('.online-chat__input');
const scrollBlock = document.querySelector('.online-chat__body')
const UserBalance = document.querySelector('.header__profile-sum>span')
const online = document.querySelector('.online-chat__current')

// WS Connection
// const chatSocket = new WebSocket(
//     'ws://'
//     + window.location.host
//     + '/ws/chat/go/'
// );
if (document.querySelector(".scrollbar-overflow")) {
    let blockArrow = document.querySelectorAll(".scrollbar-overflow");

    blockArrow.forEach(function (item) {
        item.addEventListener("touchmove", function () {
            item.classList.add("scrollbar-overflow_active");
        });

        item.addEventListener("touchend", function () {
            setTimeout(function () {
                item.classList.remove("scrollbar-overflow_active");
            }, 1000);
        });
    });
}
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.chat_type === 'support' && document.title === 'Помощь') {
        if (data.list_message) {
            data.list_message.forEach((mess) => {
                if (mess.file_message) {
                    newUserMessage(mess.message, mess.user_posted.username, mess.file_message)
                } else {
                    newUserMessage(mess.message, mess.user_posted.username)
                }
            })
        } else {
            if (data.file_path !== '/') {
                newUserMessage(`${data.message}`, data.user, data.file_path)
            } else {
                newUserMessage(`${data.message}`, data.user)
            }
        }
    }
    scrollBlock.scrollTop = scrollBlock.scrollHeight
};
messageInput.focus();
messageInput.onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        buttonSend.click();
    }
};
buttonSend.onclick = function (e) {
    const message = messageInput.value;
    if (is_auth === true) {
        chatSocket.send(JSON.stringify({
            "chat_type": "all_chat",
            'message': message,
            'user': username,
            'avatar': ava,
            'rubin': rubin
        }));
    } else {
        ///////////вывод модалки НЕ_АВТОРИЗОВАН///////////////////
        let modalAuth = document.querySelector('#authorization')
        modalAuth.classList.add("open");
        // document.querySelector('.modal__balance').innerHTML = ` Ваш баланс: ${balanceUser}`
        modalAuth.addEventListener("click", function (e) {
            if (!e.target.closest(".popup__content")) {
                document.querySelector('.popup.open').classList.remove("open");
            }
        });
///////////////////////////////////////////////////////////////////////////////////
    }
    messageInput.value = '';

}
chatSocket.onopen = function (e) {
    chatSocket.send(JSON.stringify({
        'online': 'online'
    }));

};