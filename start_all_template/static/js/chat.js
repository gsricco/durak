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
const UserBalanceMob = document.querySelector('.header__balance>span')
const online = document.querySelector('#onlineChat')
const onlineMob = document.querySelector('#onlineChatMob')
const is_user_staff = JSON.parse(document.getElementById('staffed').textContent);
const current_user_id = JSON.parse(document.getElementById("current_user_id").textContent);
// WS Connection

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/go/'
);

//вставка онлайн чата только на главную страницу
if (window.location.pathname === '/') {
    let mobileChat = document.querySelector('#mobile-online-chat')
    let tempElem = document.querySelector('.profil-main')
    let divMobChat = document.createElement('div')
    divMobChat.className = 'chat-open-btn'
    divMobChat.innerHTML = `    
                <svg>
                    <use xlink:href="/static/img/icons/sprite.svg#chat-btn"></use>
                   
                </svg>
    `
    mobileChat.insertBefore(divMobChat, tempElem);
}


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
function update_balance(current_balance){
    UserBalancer = Number(current_balance)
            // // Отображать надо уже преобразованное число, а использовать пришедшее
            if ( UserBalancer/ 1000 > 9 && UserBalancer / 1000 < 1000) {
                UserBalancerShow = `${UserBalancer / 1000}K`
            } else {
                if (UserBalancer / 1000000 > 0) {
                    UserBalancerShow = `${UserBalancer / 1000000}M`
                } else
                    UserBalancerShow = `${UserBalancer}`
            }
            if (UserBalancer / 1000 > 0 && UserBalancer / 1000 < 10) {
                UserBalancerShow = `${UserBalancer}`
            }
            UserBalance.innerHTML = `${UserBalancerShow}`
            UserBalanceMob.innerHTML = `${UserBalancerShow}`
}
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.get_online > 0) {
        online.innerHTML = `${data.get_online}`
        onlineMob.innerHTML = `${data.get_online}`
    }

if (data.message && data.chat_type === 'all_chat') {
    console.log(data,'ETO DATA')
        const li = document.createElement('li')
        li.className = 'online-chat__li'
        messageBlock.appendChild(li)

        const divWrap = document.createElement('div')
        divWrap.className = 'online-chat__li-wrapper'
        li.id = data.t
        li.appendChild(divWrap)

        const divRub = document.createElement('div')
        divRub.className = 'online-chat__li-rubin'
        divWrap.appendChild(divRub)

        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
        svg.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.rubin}"></use>`
        // stone.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.bet.userStone}"></use>`

        divRub.appendChild(svg)
        const divAva = document.createElement('div')
        divAva.className = 'online-chat__li-avatar'
        divAva.innerHTML = `<img src="${data.avatar}" alt="">`
        divWrap.appendChild(divAva)

        const p = document.createElement('p')
        p.className = 'online-chat__li-text'
        li.appendChild(p)

        const spanName = document.createElement('span')
        spanName.className = 'online-chat__li-name'
        spanName.innerHTML = `${data.user} `
        p.appendChild(spanName)

        const spanMessage = document.createElement('span')
        spanMessage.className = 'online-chat__li-sms'
        spanMessage.innerHTML = `${data.message}`

        p.appendChild(spanMessage)
        if(is_user_staff) {
            const divButtons = document.createElement('div')
            divButtons.className = 'online-chat-buttons'
            li.appendChild(divButtons)

            const btnDelete = document.createElement('button')
            btnDelete.type = 'submit'
            btnDelete.onclick = () => onClickDeleteHandler(li.id, data.message)
            btnDelete.className = 'online__chat-img'
            divButtons.appendChild(btnDelete)

            const svgDel = document.createElementNS("http://www.w3.org/2000/svg", "svg")
            svgDel.innerHTML = `<use xlink:href="${static_prefix}img/icons/sprite.svg#delete_msg"></use>`
            btnDelete.appendChild(svgDel)

            const btnBan = document.createElement('button')
            btnBan.type = 'submit'
            btnBan.id = data.id
            btnBan.onclick = () => onClickBanHandler(btnBan.id)
            btnBan.className = 'online__chat-img'
            divButtons.appendChild(btnBan)

            const svgBan = document.createElementNS("http://www.w3.org/2000/svg", "svg")
            svgBan.innerHTML = `<use xlink:href="${static_prefix}img/icons/sprite.svg#ban_user"></use>`
            btnBan.appendChild(svgBan)
        }
    }
    if (data.chat_type === 'all_chat_list') {
        console.log(data,'ETO DATA')
        messageBlock.innerHTML = ''
        const set = new Set(data.list);
        for (let count of set) {
            const data = count

            const li = document.createElement('li')
            li.className = 'online-chat__li'
            li.id = data.t
            messageBlock.appendChild(li)

            const divWrap = document.createElement('div')
            divWrap.className = 'online-chat__li-wrapper'
            li.appendChild(divWrap)

            const divRub = document.createElement('div')
            divRub.className = 'online-chat__li-rubin'
            divWrap.appendChild(divRub)
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
            svg.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.rubin}"></use>`
            divRub.appendChild(svg)
            const divAva = document.createElement('div')
            divAva.className = 'online-chat__li-avatar'
            divAva.innerHTML = `<img src="${data.avatar}" alt="">`
            divWrap.appendChild(divAva)

            const p = document.createElement('p')
            p.className = 'online-chat__li-text'
            li.appendChild(p)

            const spanName = document.createElement('span')
            spanName.className = 'online-chat__li-name'
            spanName.innerHTML = `${data.user}  `
            p.appendChild(spanName)

            const spanMessage = document.createElement('span')
            spanMessage.className = 'online-chat__li-sms'
            spanMessage.innerHTML = `${data.message}`

            p.appendChild(spanMessage)
            if(is_user_staff) {
                const divButtons = document.createElement('div')
                divButtons.className = 'online-chat-buttons'
                li.appendChild(divButtons)

                const btnDelete = document.createElement('button')
                btnDelete.type = 'submit'
                btnDelete.onclick = () => onClickDeleteHandler(li.id, data.message)
                btnDelete.className = 'online__chat-img'
                divButtons.appendChild(btnDelete)

                const svgDel = document.createElementNS("http://www.w3.org/2000/svg", "svg")
                svgDel.innerHTML = `<use xlink:href="${static_prefix}img/icons/sprite.svg#delete_msg"></use>`
                btnDelete.appendChild(svgDel)

                const btnBan = document.createElement('button')
                btnBan.type = 'submit'
                btnBan.id = data.id
                btnBan.onclick = () => onClickBanHandler(btnBan.id)
                btnBan.className = 'online__chat-img'
                divButtons.appendChild(btnBan)

                const svgBan = document.createElementNS("http://www.w3.org/2000/svg", "svg")
                svgBan.innerHTML = `<use xlink:href="${static_prefix}img/icons/sprite.svg#ban_user"></use>`
                btnBan.appendChild(svgBan)
            }
        }
    }
    if (data.lvlup) {
            level_data_next = document.querySelector('.level_data_next')
            level_data_back = document.querySelector('.level_data_back')
            level_data_back.innerHTML = data.lvlup.levels + 'ур.'
            level_data_next.innerHTML = data.lvlup.new_lvl + 'ур.'
            }
    if (data.expr){
        level_line = document.querySelector('.header__profile-line_span')
        level_line.style.width = data.expr.percent + '%'
    }
    if (data.current_balance) {
            update_balance(data.current_balance)
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
            'rubin': rubin,
            't': Date.now(),
            'id': current_user_id
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
const onClickDeleteHandler=(li)=>{
           chatSocket.send(JSON.stringify({
            'delete_message': li,
        }));
}
const onClickBanHandler=(id)=>{
    chatSocket.send(JSON.stringify({
            'ban_user_all_chat': id,
        }));
}

function open_modal_lvl(data) {
    let modalLvlText = document.querySelector('.modal_lvl_text')
    let modalLvlImg = document.querySelector('.icon-lvl-up')
    modalLvlText.innerHTML = `Уровень повышен! <br> Вам доступно “${data.case_name} ”${data.case_count}шт.</div>`
    modalLvlImg.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.lvl_img}"></use>`
    let dd = document.querySelector('#lvl-up')
    setTimeout(()=>{popupOpen(dd)},300)
}