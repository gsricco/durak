let refillAmount = 0;
let userBalance = 0;
let refillSocket = null;
let botNameR = '';
let btnTimerInstructin = document.querySelector("#modalManualBtn");
hideForm();

// создание заявки по нажатию на кнопку
// пополнение
btnTimerInstructin.addEventListener("click", function(e) {
    if(is_auth && btnTimerInstructin.textContent == "Начать") {
        // кнопка ожидайте
        btnTimerInstructin.innerHTML = "<span>Ожидайте..</span>";
        btnTimerInstructin.classList.add("btn_white");

        refillSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/refill_payment/create/'
        );

        refillSocket.onmessage = refillSocketOnMessage;

        let request = {
            "amount": refillAmount
        }
        refillSocket.addEventListener("open", function (e) {
            refillSocket.send(JSON.stringify({
                'create': request
            }));
        });
    }});
// обновление формы
function hideForm() {
    let query = document.querySelector("#manual_queries_r");
    query.style.visibility =  "hidden";
    query.textContent = "Заявка #";
    let span = document.querySelector("#bot-nickname-r");
    span.innerHTML = "(отобразится после начала)";
    let li1 = document.querySelector("#li-p2-less-2M");
    li1.style.visibility = "visible";
    let li2 = document.querySelector("#li-p2-ge-2M");
    li2.style.display = "none";
    let spanNumber = document.querySelector("#number-of-games");
    spanNumber.textContent = "X";
    btnTimerInstructin.classList.remove("btn_white");
    btnTimerInstructin.innerHTML = "Начать";
    if (refillSocket !== null && refillSocket.readyState == "OPEN") {
        refillSocket.close(1000);
    }
};
// отсчёт на кнопке
function setCountdown(timerContainerId, startTime) {
    let timerContainer = document.querySelector(timerContainerId);
    timerContainer.innerHTML = `<div class="timer"></div>`;
    let timerBlock = timerContainer.firstChild;
    timerBlock.textContent = startTime.trim();
    let valueTimer = timerBlock.textContent.split(":");
    let [minuteTime, secTime] = valueTimer;

    let timer = setInterval(function () {
        if (secTime < 60) {
            secTime -= 1;
        }

        if (secTime < 0) {
            minuteTime -= 1;
            secTime = 59;
        }

        if (minuteTime < 1 && secTime < 1) {
            clearInterval(timer);
            // setTimeout(functionTimer, 0);
        }

        if (secTime >= 10) {
            timerBlock.innerHTML = `${minuteTime}:${secTime}`;
        }

        if (secTime < 10 && secTime >= 0) {
            timerBlock.innerHTML = `${minuteTime}:0${secTime}`;
        }
    }, 1000);
};
// обработка ответов сервера в заявке на пополнение
let lastServerMessage = '';
let requestOpened = false;
function refillSocketOnMessage(e) {
    const data = JSON.parse(e.data);

    if (data.hasOwnProperty('request_id') && data.status === 'open') {
        // {"id": 4, "user": {"id": 1}, "request_id": 4, "status": "open", "amount": 1000, "balance": 0, "date_opened": "2022-12-22T21:16:20.118312Z", "date_closed": null, "note": null, "close_reason": null, "game_id": null}
        requestOpened = true;
        // let divModalQueries = modalRefill.querySelector("div.modal-manual__queries");
        // divModalQueries.innerHTML = `Заявка #${data.request_id}`;
        // let divModalTextul = modalRefill.querySelector("div.modal-manual__text>ul");
        // divModalTextul.innerHTML = '';
        // let li = document.createElement('li')
        // li.innerHTML = `Создана заявка на пополнение кредитами из игры. Сумма пополнения равна ${data.amount}.`;
        // divModalTextul.appendChild(li);
    } else if (data.hasOwnProperty('status')) {

        let dataStatus = data['status'];

        if (dataStatus === 'error') {
            // let divModalTextul = modalRefill.querySelector("div.modal-manual__text>ul");
            // let li = document.createElement('li')
            // li.innerHTML = `${data.detail}`;
            // divModalTextul.appendChild(li);
            hideForm();
            refillSocket.close(1000);
        } else if (dataStatus === 'process') {

        } else if (dataStatus === 'continue') {
            // {"status": "continue", "detail": 4}
        } else if (dataStatus === 'get_name') {
            // {"status": "get_name", "detail": "\u041c\u0430\u0440\u0438\u043d\u0430 \u0412\u043e\u043b\u043a\u043e\u0432\u0430"}
            botNameR = data['detail'];
            setTimeout(setCountdown, 0, "#modalManualBtn", "6:00");
            let span = document.querySelector("#bot-nickname-r");
            span.innerHTML = `<b>${botNameR}</b>`;
        }
    } else if (data.hasOwnProperty('message')) {
        // {"closed":false,"done":false,"progress":"None","close_reason":"None","message":"","note":"","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // {"closed":true,"done":true,"progress":"WaitingMessage","close_reason":"NoMessage","message":"ÐÑ Ð½Ðµ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»Ð¸ Ð±Ð¾ÑÑ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ Ð·Ð°Ð´Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð²ÑÐµÐ¼ÐµÐ½Ð¸, Ð¿Ð¾Ð¿ÑÐ¾Ð±ÑÐ¹ÑÐµ ÐµÑÑ ÑÐ°Ð·.","note":"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ Ð¾Ñ Ð¸Ð³ÑÐ¾ÐºÐ° Ð½Ðµ Ð¿ÑÐ¸ÑÐ»Ð¾ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ 331 ÑÐµÐºÑÐ½Ð´","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        let serverMessage = data.message;
        // let divModalTextul = modalRefill.querySelector("div.modal-manual__text>ul");
        if (serverMessage != lastServerMessage) {
            lastServerMessage = serverMessage;
        //     let li = document.createElement('li')
        //     li.innerHTML = `${serverMessage}.`;
        //     divModalTextul.appendChild(li);
        };
        if (data.done) {
            // let li = document.createElement('li');
            // li.innerHTML = `Заявка закрыта. Статус: ${data.close_reason === 'Success' ? 'успешно' : 'не успешно'}. Сумма пополнения: ${data.refiil}`;
            // divModalTextul.appendChild(li);
            requestOpened = false;
        };
    };
};




const withdrawSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/withdraw_payment/create/'
);
// вывод
let lastServerMessageW = '';
let requestOpenedW = false;
withdrawSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    let modalWithdraw = document.getElementById('modalWithdraw');

    if (data.hasOwnProperty('request_id') && data.status === 'open') {
        // {"id": 4, "user": {"id": 1}, "request_id": 4, "status": "open", "amount": 1000, "balance": 0, "date_opened": "2022-12-22T21:16:20.118312Z", "date_closed": null, "note": null, "close_reason": null, "game_id": null}
        requestOpenedW = true;
        let divModalQueries = modalWithdraw.querySelector("div.modal-manual__queries");
        divModalQueries.innerHTML = `Заявка #${data.request_id}`;
        let divModalTextul = modalWithdraw.querySelector("div.modal-manual__text>ul");
        divModalTextul.innerHTML = '';
        let li = document.createElement('li')
        li.innerHTML = `Создана заявка на вывод кредитов из игры. Сумма вывода равна ${data.amount}.`;
        divModalTextul.appendChild(li);
    } else if (data.hasOwnProperty('status')) {

        let dataStatus = data['status'];

        if (dataStatus === 'error') {
            let divModalTextul = modalWithdraw.querySelector("div.modal-manual__text>ul");
            let li = document.createElement('li')
            li.innerHTML = `${data.detail}`;
            divModalTextul.appendChild(li);
        } else if (dataStatus === 'process') {

        } else if (dataStatus === 'continue') {
            // {"status": "continue", "detail": 4}
        } else if (dataStatus === 'get_name') {
            // {"status": "get_name", "detail": "\u041c\u0430\u0440\u0438\u043d\u0430 \u0412\u043e\u043b\u043a\u043e\u0432\u0430"}
        }
    } else if (data.hasOwnProperty('message')) {
        // {"closed":false,"done":false,"progress":"None","close_reason":"None","message":"","note":"","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // {"closed":true,"done":true,"progress":"WaitingMessage","close_reason":"NoMessage","message":"ÐÑ Ð½Ðµ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»Ð¸ Ð±Ð¾ÑÑ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ Ð·Ð°Ð´Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð²ÑÐµÐ¼ÐµÐ½Ð¸, Ð¿Ð¾Ð¿ÑÐ¾Ð±ÑÐ¹ÑÐµ ÐµÑÑ ÑÐ°Ð·.","note":"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ Ð¾Ñ Ð¸Ð³ÑÐ¾ÐºÐ° Ð½Ðµ Ð¿ÑÐ¸ÑÐ»Ð¾ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ 331 ÑÐµÐºÑÐ½Ð´","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        let serverMessage = data.message;
        let divModalTextul = modalWithdraw.querySelector("div.modal-manual__text>ul");
        if (serverMessage != lastServerMessageW) {
            lastServerMessageW = serverMessage;
            let li = document.createElement('li')
            li.innerHTML = `${serverMessage}.`;
            divModalTextul.appendChild(li);
        };
        if (data.done) {
            let li = document.createElement('li');
            li.innerHTML = `Заявка закрыта. Статус: ${data.close_reason === 'Success' ? 'успешно' : 'не успешно'}. Сумма вывода: ${data.withdraw}`;
            divModalTextul.appendChild(li);
            requestOpenedW = false;
        };
    };
};

// вывод
document.querySelector('#modalManualBtn2').addEventListener("click", function(e) {
    if(is_auth) {
        let request = {
            "amount": refillAmount,
            "balance": userBalance
        }
        withdrawSocket.send(JSON.stringify({
            'create': request,
            'user': username,
        }));
    }});

// проверка баланса в дураке
document.querySelector('#selectAmountInput').addEventListener('click', function (e) {
    userBalance = parseInt(document.querySelector('input.s-am-input__input').value);
    if (userBalance >= 100) {
        let repeateOneW = 0;
        
        if (repeateOneW < 1) {
            timerSecond("#timerPay", function () {
                let btnTimerInstructin =
                    document.querySelector("#modalManualBtn2");
                btnTimerInstructin.classList.remove("btn_white");
                btnTimerInstructin.innerHTML = "Начать";
            });
            repeateOneW++;
        }
    } else {
        const curentPopup = document.getElementById("selectAmountInput");
        popupOpen(curentPopup);
    }
});

// возобновление показа окна с заявкой при его закрытии
let unlockR = true;
const timeoutR = 800;

function bodyUnLock() {
    setTimeout(function () {
        if (lockPadding.length > 0) {
            for (let index = 0; index < lockPadding.length; index++) {
                const el = lockPadding[index];
                el.style.paddingRight = "0px";
            }
        }
        body.style.paddingRight = "0px";
        body.classList.remove("lock");
    }, timeoutR);

    unlockR = false;
    setTimeout(function () {
        unlockR = true;
    }, timeoutR);
}

function bodyLock() {
    const lockPaddingValue =
        window.innerWidth - document.querySelector(".wrapper").offsetWidth + "px";
    if (lockPaddingValue.length > 0) {
        for (let index = 0; index < lockPadding.length; index++) {
            const el = lockPadding[index];
            el.style.paddingRight = lockPaddingValue;
        }
    }
    body.style.paddingRight = lockPaddingValue;
    body.classList.add("lock");

    unlockR = false;
    setTimeout(function () {
        unlockR = true;
    }, timeoutR);
}

function popupClose(popupActive, doUnLock = true) {
    if (unlockR) {
        popupActive.classList.remove("open");
        if (doUnLock) {
            bodyUnLock();
        }
    }
}

function popupOpen(curentPopup) {
    const popupActive = document.querySelector(".popup.open");
    if (popupActive) {
        popupClose(popupActive, false);
    } else {
        bodyLock();
    }
    curentPopup.classList.add("open");
    curentPopup.addEventListener("click", function (e) {
        if (!e.target.closest(".popup__content")) {
            popupClose(e.target.closest(".popup"));
        }
    });
}

document.querySelectorAll('a.modal-payment__block.popup-link')[1].addEventListener("click", function(e) {
    if (requestOpened) {
        const curentPopup = document.getElementById("modalRefill");
        popupOpen(curentPopup);
        e.preventDefault();
        e.stopImmediatePropagation();
    }
});

window.addEventListener('load', function(e) {
    let divs = this.document.querySelectorAll("div.select-amount__value");
    for (let div of divs) {
        let inner_text = div.textContent;
        let credits = '0';
        if (inner_text.includes('K') || inner_text.includes('К') || inner_text.includes('k') || inner_text.includes('к')) {
            credits = inner_text.trim().slice(0, -1) + '000';
        } else if (inner_text.includes('m') || inner_text.includes('M') || inner_text.includes('М') || inner_text.includes('м')) {
            credits = inner_text.trim().slice(0, -1) + '000000';
        }
        div.parentElement.setAttribute('credits', credits);
    }

    let links = document.querySelectorAll("a.select-amount__item.popup-link");
    for (let a of links) {
        a.addEventListener("click", function (e) {
            if (a.hasAttribute("credits")) {
                refillAmount = a.getAttribute("credits");
            };
            e.preventDefault();
        });
    }
});
