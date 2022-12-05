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
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/go/'
);


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
    if (data.init) {
        if (data.init.state === 'countdown') {
            let timeNow = Date.now()
            let remainTime = (20 * 1000 - (timeNow - data.init.t)) / 1000
            timerCounter(remainTime)
        }
        if (data.init.state === 'rolling') {
            console.log(data)

            startRoll(data.init.winner)

        }
    }
    if (data.current_balance) {
        console.log(data.current_balance, 'CURRENT BALANCE')
        UserBalance.innerHTML = `${data.current_balance}`
    }

    if (data.bid) {
        console.log(data.bid, 'eto data bid!!!!!!!!!!!!!!!')
        createBidItemRow(data.bid)
    }
    if (data.roll) {
        startRoll(data.winner)
    }
    if (data.stop) {
        let winnerCard = data.w
        //winnerCard from backend
        // let winnerCard = `coin` //    !!!!!!!!!!!!!!!!!! data.winner - undefined !!!!!!!!!!!!!!!!!!!!!!!!
        // console.log(winnerCard)
        let bidsNumber = document.querySelectorAll('.roulette__item-money')
        const bidsButtons = document.querySelectorAll('.roulette__radio-item')
        bidsNumber.forEach(el => {
            el.style.color = 'red'
        })
        if (winnerCard === 'hearts') {
            let bidsNumber = document.querySelectorAll('.hearts .roulette__item-money')
            bidsNumber.forEach(el => {
                //обновление баланса user////
                let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
                console.log(balanceUser)
                // /////////////////////
                el.style.color = 'green'
                document.querySelector('.hearts').style.opacity = '1'
                bidsButtons[0].style.opacity = '1'
            })
        } else if (winnerCard === 'coin') {
            let bidsNumber = document.querySelectorAll('.coin .roulette__item-money')
            bidsNumber.forEach(el => {
                //обновление баланса user////
                let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
                console.log(balanceUser)
                // /////////////////////
                el.style.color = 'green'
                document.querySelector('.coin').style.opacity = '1'
                bidsButtons[1].style.opacity = '1'
            })
        } else if (winnerCard === 'spades') {
            let bidsNumber = document.querySelectorAll('.spades .roulette__item-money')
            bidsNumber.forEach(el => {
                //обновление баланса user////
                let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
                console.log(balanceUser)
                // /////////////////////
                el.style.color = 'green'
                document.querySelector('.spades').style.opacity = '1'
                bidsButtons[2].style.opacity = '1'
            })
        }


    }
    if (data.back) {
        //winnerCard from backend
        returnToStartPosition()
    }

    if (data.roulette) {
        timerCounter(data.roulette)
        // код для теста функциональности начисления опыта
        // {#toSend = {#}
        // {#    "bet": {#}
        // {#        "credits": 1000000,#}
        // {#        "placed": "black"#}
        // {#    }#}
        // {##}
        // {#strToSend = JSON.stringify(toSend)#}
        // {#chatSocket.send(strToSend)#}
        // {#console.log(strToSend, 'TOSEND IN 370 stroka')#}
        ////////////////////////////
    }
        if (data.lvlup) {
            console.log("You have a new level: " + data.lvlup.new_lvl)
            level_data_next = document.querySelector('.level_data_next')
            level_data_back = document.querySelector('.level_data_back')
            level_data_back.innerHTML = data.lvlup.levels + 'ур.'
            level_data_next.innerHTML = data.lvlup.new_lvl + 'ур.'
            }
    if (data.expr){
        level_line = document.querySelector('.header__profile-line_span')
        level_line.style.width = data.expr.percent + '%'
    }
    if (data.get_online > 0) {
        online.innerHTML = `${data.get_online}`
    }

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


    if (data.message && data.chat_type === 'all_chat') {
        const li = document.createElement('li')
        li.className = 'online-chat__li'
        messageBlock.appendChild(li)

        const divWrap = document.createElement('div')
        divWrap.className = 'online-chat__li-wrapper'
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
        spanName.innerHTML = `${data.user} </br>`
        p.appendChild(spanName)

        const spanMessage = document.createElement('span')
        spanMessage.className = 'online-chat__li-sms'
        spanMessage.innerHTML = `${data.message}`

        p.appendChild(spanMessage)
    }
    if (data.chat_type === 'all_chat_list') {
        const set = new Set(data.list);
        console.log("list_50")
        for (let count of set) {
            const data = count

            const li = document.createElement('li')
            li.className = 'online-chat__li'
            messageBlock.appendChild(li)

            const divWrap = document.createElement('div')
            divWrap.className = 'online-chat__li-wrapper'
            li.appendChild(divWrap)

            const divRub = document.createElement('div')
            divRub.className = 'online-chat__li-rubin'
            divWrap.appendChild(divRub)
            console.log(data.rubin, 'ETO RUBIN')
            console.log(data.avatar, 'ETO AVATAR')
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
            spanName.innerHTML = `${data.user} </br>`
            p.appendChild(spanName)

            const spanMessage = document.createElement('span')
            spanMessage.className = 'online-chat__li-sms'
            spanMessage.innerHTML = `${data.message}`

            p.appendChild(spanMessage)
        }
    }
    scrollBlock.scrollTop = scrollBlock.scrollHeight

};

//    chatSocket.onclose = function(e) {
//        console.error('Chat socket closed unexpectedly');
//    };

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
