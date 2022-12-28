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
const freeSpan = document.querySelector('#free_amount');

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
            if (UserBalancer < 1000000) {
    let nal = UserBalancer / 1000
    if (UserBalancer % 1000 === 0){
        UserBalancerShow = nal+'K'
    }else{
        let strList = String(nal).split('.')
        UserBalancerShow = `${strList[0]}.${strList[1].slice(0,1)}K`
}}else {
    //если больше 1млн
    let nal = UserBalancer / 1000000
    let strList = String(nal).split('.')
    if (UserBalancer % 1000000 === 0) {
        UserBalancerShow = nal+'М'
    }else if(UserBalancer < 10000000){
        UserBalancerShow = `${strList[0]}.${strList[1].slice(0,2)}M`
    }else if(UserBalancer >= 10000000 && UserBalancer < 100000000){
        UserBalancerShow = `${strList[0]}.${strList[1].slice(0,1)}M`
    }else if(UserBalancer > 100000000 ) {
        UserBalancerShow = `${strList[0]}M`
}}
            UserBalance.innerHTML = `${UserBalancerShow}`
            UserBalanceMob.innerHTML = `${UserBalancerShow}`
}
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if(data.modal_lvl_data){
        open_modal_lvl(data.modal_lvl_data)
    }
    if (data.get_online > 0) {
        online.innerHTML = `${data.get_online}`
        onlineMob.innerHTML = `${data.get_online}`
    }

if (data.message && data.chat_type === 'all_chat') {
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
    if (data.hasOwnProperty('free_balance')) {
        if (freeSpan) {
            freeSpan.innerText = Math.floor(parseInt(data.free_balance) / 1000)
        }
    }
    if (data.hasOwnProperty('credits')) {
        credits = data.credits;
        let sumCurrent = document.querySelector(".num-game-currency__span-curent");
        sumCurrent.value = `${parseFloat(
            credits / 1000,
        ).toFixed(0)}`;
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
    modalLvlText.innerHTML = `Уровень повышен! <br> Вам доступно ${data.case_count} шт. “${data.case_name}”</div>`
    modalLvlImg.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.lvl_img}"></use>`
    let dd = document.querySelector('#lvl-up')
    setTimeout(()=>{popupOpen(dd)},300)
}

const freeButton = document.querySelector(".conclusion__btn");

if (freeButton) {
    freeButton.addEventListener("click", function () {
        freeButton.disabled = true;
        chatSocket.send('{"free_balance":"get"}');
        freeButton.disabled = false;
    });
}

    //! Формула перевода рублей в валюту и обратно
window.addEventListener('load', function (e) {
    if (document.querySelector(".amount-selection__form")) {
        // достаём инпуты и вешаем на них события
        var inputForm = document.querySelector(".amount-selection__input");
        var sumCurrent = document.querySelector(".num-game-currency__span-curent");
        var btnForm = document.querySelector(".amount-selection__btn");
        inputForm.addEventListener("input", sumScore);
        sumCurrent.addEventListener("input", sumValute);
    
        function sumScore() {
            let inputValueDinamic = inputForm.value.split(/[^0-9]/g);
            if (inputValueDinamic.length > 1 || inputForm.value.length == 0) {
                inputForm.value = "";
            } else {
                chatSocket.send(JSON.stringify({
                    "rub": inputForm.value,
                }));
                if (inputForm.value < 69) {
                    sumCurrent.value = `${inputForm.value * 0}`;
                    btnForm.classList.add("btn-disable-sum");
                } else if (inputForm.value >= 69) {
                    btnForm.classList.remove("btn-disable-sum");
                }
            }
        }
    
        function sumValute() {
            let inputValueDinamic = sumCurrent.value.split(/[^0-9]/g);
            if (inputValueDinamic.length > 1) {
                sumCurrent.value = "";
            } else {
                let currentCredint = (sumCurrent.value / 50000) * 1000;
    
                if (currentCredint >= 1) {
                    btnForm.classList.remove("btn-disable-sum");
                } else {
                    btnForm.classList.add("btn-disable-sum");
                }
    
                if (currentCredint < 1) {
                    inputForm.value = "";
                }
                if (currentCredint <= 2 && currentCredint >= 1) {
                    inputForm.value = `${(currentCredint * 69).toFixed(1)}`;
                }
    
                if (currentCredint <= 5 && currentCredint >= 2) {
                    inputForm.value = `${(currentCredint * 55).toFixed(1)}`;
                }
    
                if (currentCredint <= 10 && currentCredint >= 5) {
                    inputForm.value = `${(currentCredint * 36).toFixed(1)}`;
                }
    
                if (currentCredint <= 20 && currentCredint >= 10) {
                    inputForm.value = `${(currentCredint * 27.5).toFixed(1)}`;
                }
    
                if (currentCredint <= 40 && currentCredint >= 20) {
                    inputForm.value = `${(currentCredint * 23).toFixed(1)}`;
                }
    
                if (currentCredint <= 60 && currentCredint >= 40) {
                    inputForm.value = `${(currentCredint * 21.25).toFixed(1)}`;
                }
    
                if (currentCredint >= 60) {
                    inputForm.value = `${(currentCredint * 20).toFixed(1)}`;
                }
    
                if (sumCurrent.value == "" && sumCurrent.value == 0) {
                    inputForm.value = "";
                }
            }
        }
    }
    
    // ===============================================================
    // Расчёт по кол-ву руб:
    // от 69 до 109р кол-во кредов = (введенное число руб.)*725
    // от 110 до 179р кол-во кредов = (введенное число руб.)*910
    // от 180 до 239р кол-во кредов = (введенное число руб.)*1389
    // от 240 до 459р кол-во кредов = (введенное число руб.)*2084
    // от 460 до 1274р кол-во кредов = (введенное число руб.)*2174
    // от 1275 кол-во кредов = (введенное число руб.)*2353
});
