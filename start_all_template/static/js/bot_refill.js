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
        btnTimerInstructin.innerHTML = "<span>Ожидайте...</span>";
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
    li1.style.display = "block";
    let li2 = document.querySelector("#li-p2-ge-2M");
    li2.style.display = "none";
    let li = document.querySelector("#bot_message_refill");
    li.textContent = '';
    li.style.visibility = "hidden";
    let spanNumber = document.querySelector("#number-of-games");
    spanNumber.textContent = "X";
    btnTimerInstructin.classList.remove("btn_white");
    btnTimerInstructin.innerHTML = "Начать";
    if (refillSocket !== null && refillSocket.readyState === "OPEN") {
        refillSocket.close(1000);
    }
};
// отсчёт на кнопке
function setCountdown(timerContainerId, startTime, callAfter) {
    let timerContainer = document.querySelector(timerContainerId);
    if (!timerContainer.classList.contains("btn_white")) {
        return;
    };
    timerContainer.innerHTML = `<div class="timer"></div>`;
    let timerBlock = timerContainer.firstChild;
    timerBlock.textContent = startTime.trim();
    let valueTimer = timerBlock.textContent.split(":");
    let [minuteTime, secTime] = valueTimer;

    let timer = setInterval(function () {
        if (!timerContainer.classList.contains("btn_white")) {
            clearInterval(timer);
            timerContainer.innerHTML = "Начать";
        }
        if (secTime < 60) {
            secTime -= 1;
        }

        if (secTime < 0) {
            minuteTime -= 1;
            secTime = 59;
        }

        if (minuteTime < 1 && secTime < 1) {
            clearInterval(timer);
            setTimeout(callAfter, 0);
        }

        if (secTime >= 10) {
            timerBlock.innerHTML = `${minuteTime}:${secTime}`;
        }

        if (secTime < 10 && secTime >= 0) {
            timerBlock.innerHTML = `${minuteTime}:0${secTime}`;
        }
    }, 1000);
};

function closeAndOpenWindow(message) {
    const popupOk = document.getElementById("refillOk");
    let message_box = document.querySelector("#refill_message_ok");
    message_box.innerHTML = message;
    popupOpen(popupOk);
    hideForm();
    refillSocket.close(1000);
    requestOpened = false;
};
// обработка ответов сервера в заявке на пополнение
let lastServerMessage = '';
let requestOpened = false;
function refillSocketOnMessage(e) {
    const data = JSON.parse(e.data);

    if (data.hasOwnProperty('request_id') && data.status === 'open') {
        // {"id": 4, "user": {"id": 1}, "request_id": 4, "status": "open", "amount": 1000, "balance": 0, "date_opened": "2022-12-22T21:16:20.118312Z", "date_closed": null, "note": null, "close_reason": null, "game_id": null}
        // сервер прислал созданную заявку
        let query = document.querySelector("#manual_queries_r");
        query.style.visibility =  "visible";
        query.textContent = "Заявка #" + data.request_id;
        requestOpened = true;
        let span = document.querySelector("#bot-nickname-r");
        span.innerHTML = `<b>${botNameR}</b>`;
        setTimeout(setCountdown, 0, "#modalManualBtn", "6:00", function () {
            closeAndOpenWindow('Время заявки вышло.');
        });
    } else if (data.hasOwnProperty('status')) {

        let dataStatus = data['status'];

        if (dataStatus === 'error') {
            // {"status": "error", "detail": "\u041d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443 \u0432 \u0431\u0430\u0437\u0435 \u0434\u0430\u043d\u043d\u044b\u0445."}
            // ошибка сервера, заявка не обрабатывается
            let query = document.querySelector("#manual_queries_r");
            query.style.visibility =  "visible";
            query.textContent = "Произошла ошибка";
            setTimeout(hideForm, 3000);
            refillSocket.close(1000);
            requestOpened = false;
        } else if (dataStatus === 'process') {
            // на сервере ошибка, ничего серьёзного))

        } else if (dataStatus === 'continue') {
            // {"status": "continue", "detail": 4}
            // произошёл реконнект на обработку старой заявки
        } else if (dataStatus === 'get_name') {
            // {"status": "get_name", "detail": "\u041c\u0430\u0440\u0438\u043d\u0430 \u0412\u043e\u043b\u043a\u043e\u0432\u0430"}
            // стало известно имя бота
            botNameR = data['detail'];
        }
    } else if (data.hasOwnProperty('message')) {
        // {"closed":false,"done":false,"progress":"None","close_reason":"None","message":"","note":"","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // {"closed":true,"done":true,"progress":"WaitingMessage","close_reason":"NoMessage","message":"ÐÑ Ð½Ðµ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»Ð¸ Ð±Ð¾ÑÑ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ Ð·Ð°Ð´Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð²ÑÐµÐ¼ÐµÐ½Ð¸, Ð¿Ð¾Ð¿ÑÐ¾Ð±ÑÐ¹ÑÐµ ÐµÑÑ ÑÐ°Ð·.","note":"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ Ð¾Ñ Ð¸Ð³ÑÐ¾ÐºÐ° Ð½Ðµ Ð¿ÑÐ¸ÑÐ»Ð¾ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ 331 ÑÐµÐºÑÐ½Ð´","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // пересылается ответ от сервера ботов
        let serverMessage = data.message;
        if (serverMessage != lastServerMessage) {
            lastServerMessage = serverMessage;
            let li = document.querySelector("#bot_message_refill");
            li.textContent = `Сообщение от бота: ${serverMessage}`;
            li.style.visibility = "visible";
        };
        if (data.done) {
            let message = 'Заявка закрыта.';
            if (data.close_reason === 'Success') {
                message = `Баланс успешно пополнен на<br>${data.refiil}`;
            } else if (data.close_reason === 'NoMessage') {
                message = 'Ошибка. Вы не написали боту.';
            } else if (data.close_reason === 'ClientScoreLessThanMinimum') {
                message = 'Ошибка. Пополнение в данный момент не доступно. Пожалуйста, попробуйте позже.';
            } else if (data.close_reason === 'ClientBanned') {
                message = 'Ошибка. Приносим извинения. На сервере ведутся технические работы, попробуйте чуть позже.';
            } else if (data.close_reason === 'ClientDontJoined') {
                message = 'Ошибка. Вы не присоединились к игре.';
            } else if (data.close_reason === 'ClientDontReady') {
                message = 'Ошибка. Вы не нажали готов.';
            } else if (data.close_reason === 'Error') {
                message = 'Ошибка. На сервере ведутся работы.';
            } else {
                message = 'Время на выполнение вышло.'
            }
            closeAndOpenWindow(message);
            requestOpened = false;
        };
    };
};


let withdrawSocket = null;

let btnTimerWithdraw = document.querySelector("#modalManualBtn2");
hideFormWithdraw();

// создание заявки по нажатию на кнопку
// вывод
btnTimerWithdraw.addEventListener("click", function(e) {
    if(is_auth && btnTimerWithdraw.textContent == "Начать") {
        // кнопка ожидайте
        btnTimerWithdraw.innerHTML = "<span>Ожидайте...</span>";
        btnTimerWithdraw.classList.add("btn_white");

        withdrawSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/withdraw_payment/create/'
        );

        withdrawSocket.onmessage = withdrawSocketOnMessage;

        let request = {
            "amount": refillAmount,
            "balance": userBalance
        }
        withdrawSocket.addEventListener("open", function (e) {
            withdrawSocket.send(JSON.stringify({
                'create': request
            }));
        });
    }});
// обновление формы
function hideFormWithdraw() {
    let query = document.querySelector("#withdraw_query");
    query.style.visibility =  "hidden";
    query.textContent = "Заявка #";
    let li = document.querySelector("#bot_message");
    li.style.visibility =  "hidden";
    li.textContent = "";
    let span = document.querySelector("#withdraw_nickname");
    span.innerHTML = "(отобразится после начала)";
    btnTimerWithdraw.classList.remove("btn_white");
    btnTimerWithdraw.innerHTML = "Начать";
    if (withdrawSocket !== null && withdrawSocket.readyState === "OPEN") {
        withdrawSocket.close(1000);
    }
};

function closeAndOpenWindowWithdraw(message) {
    const popupOk = document.getElementById("refillOk");
    let message_box = document.querySelector("#refill_message_ok");
    message_box.innerHTML = message;
    popupOpen(popupOk);
    hideFormWithdraw();
    withdrawSocket.close(1000);
    requestOpened = false;
};

let botNameW = '';
let lastServerMessageW = '';
// обработка ответов сервера в заявке на пополнение
function withdrawSocketOnMessage(e) {
    const data = JSON.parse(e.data);

    if (data.hasOwnProperty('request_id') && data.status === 'open') {
        // {"id": 4, "user": {"id": 1}, "request_id": 4, "status": "open", "amount": 1000, "balance": 0, "date_opened": "2022-12-22T21:16:20.118312Z", "date_closed": null, "note": null, "close_reason": null, "game_id": null}
        // сервер прислал созданную заявку
        let query = document.querySelector("#withdraw_query");
        query.style.visibility =  "visible";
        query.textContent = "Заявка #" + data.request_id;
        requestOpened = true;
        let span = document.querySelector("#withdraw_nickname");
        span.innerHTML = `<b>${botNameW}</b>`;
        setTimeout(setCountdown, 0, "#modalManualBtn2", "10:00", function () {
            closeAndOpenWindowWithdraw('Время заявки вышло.');
        });
    } else if (data.hasOwnProperty('status')) {

        let dataStatus = data['status'];

        if (dataStatus === 'error') {
            // {"status": "error", "detail": "\u041d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0437\u0430\u044f\u0432\u043a\u0443 \u0432 \u0431\u0430\u0437\u0435 \u0434\u0430\u043d\u043d\u044b\u0445."}
            // ошибка сервера, заявка не обрабатывается
            let query = document.querySelector("#withdraw_query");
            query.style.visibility =  "visible";
            query.textContent = "Произошла ошибка";
            setTimeout(hideFormWithdraw, 3000);
            withdrawSocket.close(1000);
            requestOpened = false;
        } else if (dataStatus === 'process') {
            // на сервере ошибка, ничего серьёзного))

        } else if (dataStatus === 'continue') {
            // {"status": "continue", "detail": 4}
            // произошёл реконнект на обработку старой заявки
        } else if (dataStatus === 'get_name') {
            // {"status": "get_name", "detail": "\u041c\u0430\u0440\u0438\u043d\u0430 \u0412\u043e\u043b\u043a\u043e\u0432\u0430"}
            // стало известно имя бота
            botNameW = data['detail'];
        }
    } else if (data.hasOwnProperty('message')) {
        // {"closed":false,"done":false,"progress":"None","close_reason":"None","message":"","note":"","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // {"closed":true,"done":true,"progress":"WaitingMessage","close_reason":"NoMessage","message":"ÐÑ Ð½Ðµ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»Ð¸ Ð±Ð¾ÑÑ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ Ð·Ð°Ð´Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð²ÑÐµÐ¼ÐµÐ½Ð¸, Ð¿Ð¾Ð¿ÑÐ¾Ð±ÑÐ¹ÑÐµ ÐµÑÑ ÑÐ°Ð·.","note":"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ Ð¾Ñ Ð¸Ð³ÑÐ¾ÐºÐ° Ð½Ðµ Ð¿ÑÐ¸ÑÐ»Ð¾ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ 331 ÑÐµÐºÑÐ½Ð´","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // пересылается ответ от сервера ботов
        let serverMessage = data.message;
        if (serverMessage != lastServerMessageW) {
            lastServerMessageW = serverMessage;
            let li = document.querySelector("#bot_message");
            li.textContent = `Сообщение от бота: ${serverMessage}`;
            li.style.visibility = "visible";
        };
        if (data.done) {
            let message = 'Заявка закрыта.';
            if (data.close_reason === 'Success') {
                message = `Успешный вывод на сумму<br>${data.withdraw}`;
            } else if (data.close_reason === 'NoMessage') {
                message = 'Ошибка. Вы не написали боту.';
            } else if (data.close_reason === 'ClientScoreLessThanMinimum') {
                message = 'Отклонено. Мы не производим вывод на пустой аккаунт. Пожалуйста, войдите с более старого аккаунта.';
            } else if (data.close_reason === 'ClientBanned') {
                message = 'Ошибка. Приносим извинения. На сервере ведутся технические работы, попробуйте чуть позже.';
            } else if (data.close_reason === 'ClientDontJoined') {
                message = 'Ошибка. Вы не присоединились к игре.';
            } else if (data.close_reason === 'ClientDontReady') {
                message = 'Ошибка. Вы не нажали готов.';
            } else if (data.close_reason === 'Error') {
                message = 'Ошибка. На сервере ведутся работы.';
            } else {
                message = 'Время на выполнение вышло.'
            }
            closeAndOpenWindowWithdraw(message);
            requestOpened = false;
        };
    };
};

// проверка баланса в дураке
document.querySelector('#selectAmountInput').addEventListener('click', function (e) {
    userBalance = parseInt(document.querySelector('input.s-am-input__input').value);
    if (!userBalance || userBalance < 100) {
        e.stopImmediatePropagation();
        e.preventDefault();
        const curentPopup = document.getElementById("selectAmountInput");
        popupOpen(curentPopup);
    };
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

// вешает на кнопки выбора размера пополнения атрибуты со стоимостью
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
            if (refillAmount !== null && parseInt(refillAmount) >= 2000000) {
                let li1 = document.querySelector("#li-p2-less-2M");
                li1.style.display = "none";
                let li2 = document.querySelector("#li-p2-ge-2M");
                li2.style.display = "block";
                let numberOfGames = document.querySelector('#number-of-games');
                numberOfGames.textContent = Math.ceil(parseInt(refillAmount) / 1000000);
            } else {
                let li1 = document.querySelector("#li-p2-less-2M");
                li1.style.display = "block";
                let li2 = document.querySelector("#li-p2-ge-2M");
                li2.style.display = "none";
                let numberOfGames = document.querySelector('#number-of-games');
                numberOfGames.textContent = 'X';
            }
        });
    }
});