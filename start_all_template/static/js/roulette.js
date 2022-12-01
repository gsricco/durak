///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//! Прокрутка рулетки
// 113 - coin
//111 - red7
//109 - black6
//107 - red5
//105 - black4
//103 - red3
//101 - black2

const ava = document.getElementById('ava').getAttribute('src');
const rubin = JSON.parse(document.querySelector('.rubin'));
const list = document.querySelector('.list');

function generateItems(winnerCard) {

    let cells;
    const heartsArray = [103, 107, 111, 115]
    const spadesArray = [101, 105, 109, 117]


    switch (winnerCard) {
        case'hearts':
            winnerCard = heartsArray[Math.round(Math.random() * (2 + 1))]
            break
        case'spades':
            winnerCard = spadesArray[Math.round(Math.random() * (2 + 1))]
            break
        case'coin':
            winnerCard = 113
            break
    }

    let numbersCards = Math.round(100 + Math.random() * (121 - 100 + 1))
    if (winnerCard) {
        cells = winnerCard
    } else {
        cells = (numbersCards % 2 === 0) ? numbersCards + 1 : numbersCards
    }
    console.log(cells)

    let h = 8;
    // четные элементы красные, нечетные черные, каждая 8 карта coin
    for (let i = 0; i < cells; i++) {

        let item;
        if (i % 2) {
            item = `<svg>
                            <use xlink:href="/static/img/icons/sprite.svg#hearts_stroke_white"></use>
                        </svg>`;
        } else {
            item = `<svg>
                            <use xlink:href="/static/img/icons/sprite.svg#spades_stroke_white"></use>
                        </svg>`;
        }
        // каждый 8-я карта coin
        if (i === h) {

            item = `<svg>
                            <use xlink:href="/static/img/icons/sprite.svg#coin_stroke_white"></use>
                        </svg>`;
            h = h + 8;
        }

        const div = document.createElement('div')
        div.classList.add('roulette__rull-img')
        div.innerHTML = item

        list.append(div)

    }
}

generateItems();

// анимация прокрутки
function startRoll(winnerCard) {
    items[0].style.pointerEvents = 'none';
    items[1].style.pointerEvents = 'none';
    items[2].style.pointerEvents = 'none';

    bidsButtons.forEach(el => {
        el.style.opacity = '0.3'
    })
    bidsBlock.forEach(el => {
        el.style.opacity = '0.3'
    })

    //докрутка от -49.6% до -50.4%
    wrapperItems.classList.remove("roulette__rull-wrapper_blur");
    timerWrapper.style.display = "none";
    rull_line.style.display = "block";


    function randomInteger(min, max) {
        // получить случайное число от (min-0.5) до (max+0.5)
        let rand = min + Math.random() * (max - min + 1);
        return Math.round(rand);
    }

    let swingFinish = `translate3d(${randomInteger(-496, -504) / 10}%, 0, 0)`
    console.log('sss ' + swingFinish)

    list.style.left = '50%'
    list.style.transform = swingFinish
    list.style.transition = '5s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
}

// анимация возврата после прокрутки
const returnToStartPosition = () => {
    list.style.left = '0%'
    list.style.transform = 'translate3d(-380px, 0, 0)'
    list.style.transition = '1s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
    wrapperItems.classList.add("roulette__rull-wrapper_blur");
    timerWrapper.style.display = "flex";

    rull_line.style.display = "inline-block";
}

//! Таймер рулетка
let timerText = document.querySelector(".roulette__rull-timer-text")
let timerWrapper = document.querySelector(".roulette__rull-timer-wrapper");
let timerNums = document.querySelector(".roulette__rull-timer");
let wrapperItems = document.querySelector(".roulette__rull-wrapper");
let rull_line = document.querySelector(".roulette__rull-line");

//добавляет стили для отображения отсчета
let blurForTimer = () => {
    wrapperItems.classList.add("roulette__rull-wrapper_blur");
    timerWrapper.style.display = "flex";
    rull_line.style.display = "inline-block";
}

// логика счетчика таймера
let timerCounter = (back_counter) => {
    items[0].style.pointerEvents = '';
    items[1].style.pointerEvents = '';
    items[2].style.pointerEvents = '';

    bidsButtons.forEach(el => {
        el.style.opacity = '1'
    })
    bidsBlock.forEach(el => {
        el.style.opacity = '1'
    })

    document.querySelector('.hearts').innerHTML = ''
    document.querySelector('.coin').innerHTML = ''
    document.querySelector('.spades').innerHTML = ''
    document.querySelector('.roulette__radio-wrapper').style.opacity = '1'
    document.querySelector('.roulette__items').style.opacity = '1'

    timerText.innerHTML = `<p class="roulette__rull-timer-text">ПРОКРУТКА</p>`
    const rafStart = Date.now();

    let timerCounter1 = () => {
        {
            // blurForTimer()
        }
        // стартовое значение таймера
        let rafSeconds = back_counter * 10;
        let num = back_counter

        const seconds = (rafSeconds - (Date.now() - rafStart) / 100) | 0;
        let timerShow = seconds / 10
        if (seconds < 1) {

            timerNums.innerHTML = ``;
            timerText.innerHTML = ``;

        } else {

            timerNums.innerHTML = `${timerShow.toFixed(1)}`
            window.requestAnimationFrame(timerCounter1);

        }

        // происходит отсчет и его отрисовка
        // let intervalTimerRull = setInterval(() => {
        //     if (num.toFixed(1) <= 0.1) {
        //         clearInterval(intervalTimerRull);
        //         // удаляем счетчик после отсчета
        //         wrapperItems.classList.remove("roulette__rull-wrapper_blur");
        //         timerWrapper.style.display = "none";
        //         rull_line.style.display = "block";
        //     } else {
        //         num -= 0.1;
        //         timerNums.innerHTML = num.toFixed(1);
        //     }
        // }, 100);

        //добавляем стили счетчика для его отображения при новой прокрутке


        // setTimeout(() => {
        //     // тут стартует анимация прокрута с задержкой в 20 секунд
        //     startRoll()
        //     setTimeout(() => {
        //         // тут происходит возврат после прокрутки на исходное положение через 8 секунд после начала прокрутки
        //         returnToStartPosition()
        //     }, 8000);
        // }, back_counter*1000)
    }
    // blurForTimer()
    timerCounter1()
}

//дергаем ф-цию что бы все сработало 1 раз при загрузке, дальше по сет интервалу в 29сек
// timerCounter()

//ставим функцию на каждые 29сек
// setInterval(timerCounter, 29000)


//! Плавные скроллбары
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

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const is_auth = JSON.parse(document.getElementById('auth-user').textContent);
const username = JSON.parse(document.getElementById('username').textContent);
const messageBlock = document.querySelector('.online-chat__list')
const buttonSend = document.querySelector('.online-chat__icon-arrow')
const messageInput = document.querySelector('.online-chat__input');
const scrollBlock = document.querySelector('.online-chat__body')
const UserBalance = document.querySelector('.header__profile-sum>span')
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/go/'
);
const online = document.querySelector('.online-chat__current')
const newUserMessage = (message, user, file_path) => {

    const li = document.createElement('li')
    li.className = 'support__chat-message support__chat-message_your'
    const div = document.createElement('div')
    div.className = 'support__chat-message-text'
    const spanUser = document.createElement('span')
    const span = document.createElement('span')
    const fullDiv = document.createElement('div')
    fullDiv.style.display = 'flex'
    fullDiv.style.flexDirection = 'column'
    spanUser.style.textAlign = 'right'
    if (user !== username) {
        li.style.justifyContent = 'flex-start'
        li.style.paddingLeft = '0%'
        li.style.paddingRight = '16%'
        div.style.background = 'orange'
        div.style.borderRadius = '15px 15px 15px 0px'
        spanUser.style.textAlign = 'left'
    }
    chatBlock.appendChild(li)
    li.appendChild(div)

    spanUser.innerHTML = user
    span.innerHTML = message
    div.appendChild(span)
    fullDiv.appendChild(spanUser)
    fullDiv.appendChild(div)
    if (file_path) {
        const file_url = document.createElement('div')
        file_url.innerHTML = 'Файл'
        file_url.className = 'file_name'
        file_url.addEventListener('click', () => {
            window.open(`http://127.0.0.1:8000${file_path}`)
        })
        if (user !== username) {
            li.appendChild(fullDiv)
            li.appendChild(file_url)
        } else {
            li.appendChild(file_url)
            li.appendChild(fullDiv)
        }
    } else {
        li.appendChild(fullDiv)
    }


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
        // createBidItemRow(data.bid)
    }
    if (data.roll) {
        generateItems(data.winner)
        startRoll()
    }
    if (data.stop) {

        //winnerCard from backend
        let winnerCard = `${data.winner}`
        let bidsNumber = document.querySelectorAll('.roulette__item-money')
        const bidsButtons = document.querySelectorAll('.roulette__radio-item')
        bidsNumber.forEach(el => {
            el.style.color = 'red'
        })
        if (winnerCard === 'hearts') {
            let bidsNumber = document.querySelectorAll('.hearts .roulette__item-money')
            bidsNumber.forEach(el => {
                el.style.color = 'green'
                document.querySelector('.hearts').style.opacity = '1'
                bidsButtons[0].style.opacity = '1'
            })
        } else if (winnerCard === 'coin') {
            let bidsNumber = document.querySelectorAll('.coin .roulette__item-money')
            bidsNumber.forEach(el => {
                el.style.color = 'green'
                document.querySelector('.coin').style.opacity = '1'
                bidsButtons[1].style.opacity = '1'
            })
        } else if (winnerCard === 'spades') {
            let bidsNumber = document.querySelectorAll('.spades .roulette__item-money')
            bidsNumber.forEach(el => {
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
        svg.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.rubin}#rubin_red"></use>`
        // stone.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.bet.userStone}"></use>`

        divRub.appendChild(svg)
        console.log(data.rubin)
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
