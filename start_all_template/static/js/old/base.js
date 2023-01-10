const chatSocket = new WebSocket('wss://' + window.location.host + '/ws/chat/go/')
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
const profilLine = document.querySelector('.profil_profil__progressbar-line')
// let balanceUser = document.querySelector('.header__profile-sum>span').innerText

//обработка всех входящих сообщений
chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    // 1) отображение онлайна , все страницы +
    if (data.get_online >= 0) {
        online.innerHTML = `${data.get_online}`
    }

    // 2) общий чат , все страницы
    if (data.message && data.chat_type === 'all_chat') {
        newAllChatMessage(data)
    }

    // 3) обработка списка из 50 сообщений
    if (data.chat_type === 'all_chat_list') {
        const set_mess = new Set(data.list);
        for (let user_mess of set_mess) {
            newAllChatMessage(user_mess)
        }
    }
    // scrollBlock.scrollTop = scrollBlock.scrollHeight

    // 4) обработка сообщений из суппорт чата на странице помощь
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


    // 5) отображение уровней на всех страницах
    if (data.lvlup) {
        level_data_next = document.querySelector('.level_data_next')
        level_data_back = document.querySelector('.level_data_back')
        level_data_back.innerHTML = data.lvlup.levels + ' ур.'
        level_data_next.innerHTML = data.lvlup.new_lvl + ' ур.'
    }

    // 6) отображение процентов уровня на всех странцах
    if (data.expr) {
        level_line = document.querySelector('.header__profile-line_span')
        level_line.style.width = data.expr.percent + '%'
        if (document.title === 'Профиль') {
            profilLine.style.width = data.expr.percent + '%'
        }
    }

    // 7) ЛОГИКА РУЛЕТКА ВСЯ
    if (document.title === 'Рулетка') {
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
                    // let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
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
                    // let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
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
                    // let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
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
    }

    // 8) КЕЙСЫ

    if (data.cases) {
        console.log('прилетели кейсы')
        setModalConst(data.cases)
    }
    if (data.lvl_info && document.title ==='Профиль'){
        set_lvl_info(data.lvl_info)
    }
    if (data.user_items){
        newUserItem(data.user_items)
        newModalUserItem(data.user_items)
    }
}

//--------------------------onmessage end------------------------------
//-----------------------------------------------------------------------


//отработка события при нажатии на стрелочку общего чата
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

//отправка сообщений в общий чат по enter
messageInput.focus();
messageInput.onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        buttonSend.click();
    }
};

if (document.title === 'Профиль') {
    chatSocket.onopen = function (e) {
        chatSocket.send(JSON.stringify({
                    'item': 'get_item'
                }
            )
        )
    }
}