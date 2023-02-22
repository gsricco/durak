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

        if (refillSocket !== null && refillSocket.readyState === 1) {
            refillSocket.close(1000);
        }

        refillSocket = new WebSocket(
            'wss://'
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
    let li = document.querySelector("#bot_message_refill");
    li.textContent = '';
    li.style.visibility = "hidden";
    let spanNumber = document.querySelector("#number-of-games");
    spanNumber.textContent = "X";
    btnTimerInstructin.classList.remove("btn_white");
    btnTimerInstructin.innerHTML = "Начать";
    if (refillSocket !== null && refillSocket.readyState === 1) {
        refillSocket.close(1000);
    }
}
// отсчёт на кнопке
function setCountdown(timerContainerId, startTime, callAfter) {
    let timerContainer = document.querySelector(timerContainerId);
    if (!timerContainer.classList.contains("btn_white")) {
        return;
    }
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
}

function closeAndOpenWindow(message, success) {
    const popupOk = document.getElementById("refillOk");
    let message_box = document.querySelector("#refill_message_ok");
    const iconerror = document.getElementById("mes_error");
    const iconok = document.getElementById("mes_ok");
    if (success){
        iconok.style.display = "flex";
        iconerror.style.display = "none";
    } else {
        iconok.style.display = "none";
        iconerror.style.display = "flex";
    }
    message_box.innerHTML = message;
    popupOpen(popupOk);
    hideForm();
    refillSocket.close(1000);
    requestOpened = false;
}
// обработка ответов сервера в заявке на ПОПОЛНЕНИЕ
let lastServerMessage = '';
let requestOpened = false;
let timerStarted = false;
let request_id1 = '';
function refillSocketOnMessage(e) {
    const data = JSON.parse(e.data);
    if (data.hasOwnProperty('request_id') && data.status === 'open') {
        // {"id": 4, "user": {"id": 1}, "request_id": 4, "status": "open", "amount": 1000, "balance": 0, "date_opened": "2022-12-22T21:16:20.118312Z", "date_closed": null, "note": null, "close_reason": null, "game_id": null}
        // сервер прислал созданную заявку
        request_id1 = data.request_id;
        let query1 = document.querySelector("#withdraw_query1");
        query1.style.visibility =  "visible";
        query1.textContent = "Заявка #" + data.request_id;
        let query = document.querySelector("#manual_queries_r");
        query.style.visibility =  "visible";
        query.textContent = "Заявка #" + data.request_id;
        requestOpened = true;
        let span = document.querySelector("#bot-nickname-r");
        span.innerHTML = `<b>${botNameR}</b>`;
        refillAmount = parseInt(data.amount);
        if (refillAmount !== null && parseInt(refillAmount) >= 2000000) {
            let li1 = document.querySelector("#li-p2-less-2M");
            li1.style.display = "none";
            let li2 = document.querySelector("#li-p2-ge-2M");
            li2.style.display = "block";
            let numberOfGames = document.querySelector('#number-of-games');
            numberOfGames.textContent = Math.ceil(parseInt(refillAmount) / 1000000);
        }
        if (!timerStarted) {
            setTimeout(setCountdown, 0, "#modalManualBtn", "6:00", function () {
//                closeAndOpenWindow('Баланс не пополнен.<br> Ошибка!!!!', false);
            });
        }
        timerStarted = false;
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
            if (data.detail === 'Идут работы!!!' )
            {
              let message = 'Пополнение в данный момент не доступно. Пожалуйста, попробуйте позже.';
              let success = false
            closeAndOpenWindow(message, success);
            requestOpened = false;
            }

        } else if (dataStatus === 'process') {
            // на сервере ошибка, ничего серьёзного))

        } else if (dataStatus === 'continue') {
            // {"status": "continue", "detail": 4}
            // произошёл реконнект на обработку старой заявки
            let modalManual = document.querySelector('#modalManual');
            if (modalManual !== null) {
                // кнопка ожидайте
                timerStarted = true;
                btnTimerInstructin.innerHTML = "<span>Ожидайте...</span>";
                btnTimerInstructin.classList.add("btn_white");
                // таймер
                let startTime = parseInt(data.start);
                let timeToStop = 6*60 + startTime - Math.floor(Date.now() / 1000);
//                let timeToStop = 1;
                if (timeToStop < 0) {
                    timeToStop = 120;
                }
                let minutes = Math.floor(timeToStop / 60).toLocaleString('en-US', {minimumIntegerDigits: 2});
                let seconds = (timeToStop % 60).toLocaleString('en-US', {minimumIntegerDigits: 2});
                let timerText = `${minutes}:${seconds}`
                setTimeout(setCountdown, 0, "#modalManualBtn", timerText, function () {
//                    closeAndOpenWindow('Баланс не пополнен.<br> Ошибка (стр 201)', false);
//                      closeAndOpenWindow(`Баланс не пополнен.<br> Ошибка #${request_id1}`, false);
                });
                // модалка открывается
                popupOpen(modalManual);
            };
        } else if (dataStatus === 'get_name') {
            // {"status": "get_name", "detail": "\u041c\u0430\u0440\u0438\u043d\u0430 \u0412\u043e\u043b\u043a\u043e\u0432\u0430"}
            // стало известно имя бота
            botNameR = data['detail'];
        }
    } else if (data.hasOwnProperty('message')) {
        // {"closed":false,"done":false,"progress":"None","close_reason":"None","message":"","note":"","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // {"closed":true,"done":true,"progress":"WaitingMessage","close_reason":"NoMessage","message":"ÐÑ Ð½Ðµ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»Ð¸ Ð±Ð¾ÑÑ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ Ð·Ð°Ð´Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð²ÑÐµÐ¼ÐµÐ½Ð¸, Ð¿Ð¾Ð¿ÑÐ¾Ð±ÑÐ¹ÑÐµ ÐµÑÑ ÑÐ°Ð·.","note":"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ Ð¾Ñ Ð¸Ð³ÑÐ¾ÐºÐ° Ð½Ðµ Ð¿ÑÐ¸ÑÐ»Ð¾ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ 331 ÑÐµÐºÑÐ½Ð´","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // пересылается ответ от сервера ботов
        // let serverMessage = data.message;
        // if (serverMessage != lastServerMessage) {
        //     lastServerMessage = serverMessage;
        //     let li = document.querySelector("#bot_message_refill");
        //     li.textContent = `Сообщение от бота: ${serverMessage}`;
        //     li.style.visibility = "visible";
        // };
        if (data.done) {
            let message = 'Заявка закрыта.';
            let success = false;
            if (data.close_reason === 'Success') {
                message = `Баланс пополнен на <br>${Math.round(data.refiil/100)*100} кредитов. Приятной игры!`;
                success = true;
            } else if (data.close_reason === 'NoMessage') {
                message = 'Ошибка. Пожалуйста, в следующий раз следуйте инструкции.';
            } else if (data.close_reason === 'ClientScoreLessThanMinimum') {
                message = 'Пополнение в данный момент не доступно. Пожалуйста, попробуйте позже.';
            } else if (data.close_reason === 'ClientBanned') {
                message = 'Ошибка. Приносим извинения. Ведутся технические работы, попробуйте чуть позже.';
            } else if (data.close_reason === 'ClientDontJoined') {
                message = 'Ошибка. Пожалуйста, в следующий раз следуйте инструкции.';
            } else if (data.close_reason === 'ClientDontReady') {
                message = 'Ошибка. Пожалуйста, в следующий раз следуйте инструкции.';
            } else if (data.close_reason === 'Error') {
                message = 'Пополнение в данный момент не доступно. Пожалуйста, попробуйте позже.';
            } else if (data.close_reason === 'Timeout') {
                message = 'Ошибка. Пожалуйста, в следующий раз следуйте инструкции.';
            } else {
                message = `Баланс не пополнен.<br> Ошибка ${request_id1}`;
            }
            closeAndOpenWindow(message, success);
            requestOpened = false;
        }
    }
}


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

        if (withdrawSocket !== null && withdrawSocket.readyState === 1) {
            withdrawSocket.close(1000);
        }

        withdrawSocket = new WebSocket(
            'wss://'
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
    if (withdrawSocket !== null && withdrawSocket.readyState === 1) {
        withdrawSocket.close(1000);
    }
}

function closeAndOpenWindowWithdraw(message, success) {
    const iconerror = document.getElementById("mes_error");
    const iconok = document.getElementById("mes_ok");
    if (success){
        iconok.style.display = "flex";
        iconerror.style.display = "none";
    } else {
        iconok.style.display = "none";
        iconerror.style.display = "flex";
    }
    const popupOk = document.getElementById("refillOk");
    let message_box = document.querySelector("#refill_message_ok");
    message_box.innerHTML = message;
    popupOpen(popupOk);
    hideFormWithdraw();
    withdrawSocket.close(1000);
    requestOpened = false;
}

let botNameW = '';
let lastServerMessageW = '';
let timerStartedW = false;
let request_id = '';
// обработка ответов сервера в заявке на ВЫВОД
function withdrawSocketOnMessage(e) {
    const data = JSON.parse(e.data);
    if (data.hasOwnProperty('request_id') && data.status === 'open') {
        // {"id": 4, "user": {"id": 1}, "request_id": 4, "status": "open", "amount": 1000, "balance": 0, "date_opened": "2022-12-22T21:16:20.118312Z", "date_closed": null, "note": null, "close_reason": null, "game_id": null}
        // сервер прислал созданную заявку
        request_id = data.request_id;
        let query = document.querySelector("#withdraw_query");
        query.style.visibility =  "visible";
        query.textContent = "Заявка #" + data.request_id;
        let query1 = document.querySelector("#withdraw_query1");
        query1.style.visibility =  "visible";
        query1.textContent = "Заявка #" + data.request_id;
        requestOpened = true;
        let span = document.querySelector("#withdraw_nickname");
        span.innerHTML = `<b>${botNameW}</b>`;
        if (!timerStartedW) {
            setTimeout(setCountdown, 0, "#modalManualBtn2", "10:00", function () {
//                closeAndOpenWindowWithdraw('Баланс не пополнен.<br> Ошибка', false);
            });
        }
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
            if (data.detail === 'Идут работы!!!' )
            {
              let message = 'Ошибка. Приносим извинения. Ведутся технические работы, попробуйте чуть позже.';
              let success = false
            closeAndOpenWindowWithdraw(message, success);
            requestOpened = false;
            }
            if (data.detail === 'Недостаточно кредитов.' )
            {
              let message = 'Недостаточно кредитов';
              let success = false
            closeAndOpenWindowWithdraw(message, success);
            requestOpened = false;
            }
        } else if (dataStatus === 'process') {
            // на сервере ошибка, ничего серьёзного))

        } else if (dataStatus === 'continue') {
            // {"status": "continue", "detail": 4}
            // произошёл реконнект на обработку старой заявки
            let modalWithdraw = document.querySelector("#modalManualWithdraw");
            if (modalWithdraw !== null) {
                // кнопка ожидайте
                timerStartedW = true;
                btnTimerWithdraw.innerHTML = "<span>Ожидайте...</span>";
                btnTimerWithdraw.classList.add("btn_white");
                // таймер
                // таймер
                let startTime = parseInt(data.start);
                let timeToStop = 10*60 + startTime - Math.floor(Date.now() / 1000);
                if (timeToStop < 0) {
                    timeToStop = 120;
                }
                let minutes = Math.floor(timeToStop / 60).toLocaleString('en-US', {minimumIntegerDigits: 2});
                let seconds = (timeToStop % 60).toLocaleString('en-US', {minimumIntegerDigits: 2});
                let timerText = `${minutes}:${seconds}`
                setTimeout(setCountdown, 0, "#modalManualBtn2", timerText, function () {
//                    closeAndOpenWindowWithdraw('Время заявки вышло.', false);
                });
                // модалка открывается
                popupOpen(modalWithdraw);
            }
        } else if (dataStatus === 'get_name') {
            // {"status": "get_name", "detail": "\u041c\u0430\u0440\u0438\u043d\u0430 \u0412\u043e\u043b\u043a\u043e\u0432\u0430"}
            // стало известно имя бота
            botNameW = data['detail'];
        }
    } else if (data.hasOwnProperty('message')) {
        // {"closed":false,"done":false,"progress":"None","close_reason":"None","message":"","note":"","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // {"closed":true,"done":true,"progress":"WaitingMessage","close_reason":"NoMessage","message":"ÐÑ Ð½Ðµ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»Ð¸ Ð±Ð¾ÑÑ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ Ð·Ð°Ð´Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð²ÑÐµÐ¼ÐµÐ½Ð¸, Ð¿Ð¾Ð¿ÑÐ¾Ð±ÑÐ¹ÑÐµ ÐµÑÑ ÑÐ°Ð·.","note":"Ð¡Ð¾Ð¾Ð±ÑÐµÐ½Ð¸Ðµ Ð¾Ñ Ð¸Ð³ÑÐ¾ÐºÐ° Ð½Ðµ Ð¿ÑÐ¸ÑÐ»Ð¾ Ð² ÑÐµÑÐµÐ½Ð¸Ð¸ 331 ÑÐµÐºÑÐ½Ð´","ban":false,"last_game_started":"0001-01-01T00:00:00","refill_started":"2022-12-22T21:16:21.7153191Z","refiil":0,"game_id":0}
        // пересылается ответ от сервера ботов
        // let serverMessage = data.message;
        // if (serverMessage != lastServerMessageW) {
        //     lastServerMessageW = serverMessage;
        //     let li = document.querySelector("#bot_message");
        //     li.textContent = `Сообщение от бота: ${serverMessage}`;
        //     li.style.visibility = "visible";
        // }
        if (data.done) {
            let message = 'Заявка закрыта.';
            let success = false;
            if (data.close_reason === 'Success') {
                message = `Выведено <br>${data.withdraw} кредитов.`;
            success = true;
            } else if (data.close_reason === 'NoMessage') {
                message = 'Вы не забрали свою валюту. В следующий раз, пожалуйста, следуйте инструкции!';
            } else if (data.close_reason === 'ClientScoreLessThanMinimum') {
                message = 'Отклонено. Мы не производим вывод на пустой аккаунт. Пожалуйста, войдите с более старого аккаунта.';
            } else if (data.close_reason === 'ClientBanned') {
                message = 'Ошибка. Приносим извинения. Ведутся технические работы, попробуйте чуть позже.';
            } else if (data.close_reason === 'ClientDontJoined') {
                message = 'Вы не забрали свою валюту. В следующий раз, пожалуйста, следуйте инструкции!';
            } else if (data.close_reason === 'ClientDontReady') {
                message = 'Вы не забрали свою валюту. В следующий раз, пожалуйста, следуйте инструкции!';
            } else if (data.close_reason === 'Timeout'){
                message = 'Вы не забрали свою валюту. В следующий раз, пожалуйста, следуйте инструкции!';
            } else if (data.close_reason === 'Error') {
                message = 'Ошибка. Приносим извинения. Ведутся технические работы, попробуйте чуть позже.';
            } else {
                message = `Баланс не пополнен.<br> Ошибка ${request_id}`;
            }
            closeAndOpenWindowWithdraw(message, success);
            requestOpened = false;
        }
    }
}

// проверка баланса в дураке
document.querySelector('#selectAmountInput').addEventListener('click', function (e) {
    let redWrite = document.querySelector('.s-am-input__msg')
    // let inputWrite = document.querySelector(`input[name='add-sum']`)
    let inputWrite = document.querySelector('#hesus')
    inputWrite.addEventListener("input", function(e){
    // function validInput() {
        let inputValueDinamic = inputWrite.value.split(/[^0-9]/g);
        if (inputValueDinamic.length > 1 || inputWrite.value.length == 0) {
            inputWrite.value = "";
            redWrite.textContent = "Введите количество ваших кредитов в игре!"
        } else {
            if (inputWrite.value < 100) {
                redWrite.textContent = "Вы должны иметь минимум 100 кредитов!"
                redWrite.style.display = "block";

            } else if (inputWrite.value >= 100) {
                redWrite.style.display = "none";
            }
        }
    });

    userBalance = parseInt(document.querySelector('input.s-am-input__input').value);

    if (e.target == document.querySelector("#unblock_close")) {
        return
    }
    if (!userBalance || userBalance < 100) {
        e.stopImmediatePropagation();
        e.preventDefault();
        const curentPopup = document.getElementById("selectAmountInput");
        popupOpen(curentPopup);
    }
});

// возобновление показа окна с заявкой при его закрытии
let unlockR = true;
const timeoutR = 800;
const lockPaddingR = document.querySelectorAll(".lock-padding");
const bodyR = document.querySelector("body");
function bodyUnLock() {
    setTimeout(function () {
        if (lockPaddingR.length > 0) {
            for (let index = 0; index < lockPaddingR.length; index++) {
                const el = lockPaddingR[index];
                el.style.paddingRight = "0px";
            }
        }
        bodyR.style.paddingRight = "0px";
        bodyR.classList.remove("lock");
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
        for (let index = 0; index < lockPaddingR.length; index++) {
            const el = lockPaddingR[index];
            el.style.paddingRight = lockPaddingRValue;
        }
    }
    bodyR.style.paddingRight = lockPaddingValue;
    bodyR.classList.add("lock");

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
    // извлечение суммы из нажатой кнопки
    let links = document.querySelectorAll("a.select-amount__item.popup-link");
    for (let a of links) {
        a.addEventListener("click", function (e) {
            if (a.hasAttribute("credits")) {
                refillAmount = a.getAttribute("credits");
            }
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
    // возобновление заявки на пополнение
    document.querySelector('[href="#selectAmount"]').addEventListener("click", function () {
        if(is_auth) {
            if (refillSocket !== null && refillSocket.readyState === 1) {
                refillSocket.close(1000);
            }
            refillSocket = new WebSocket(
                'wss://'
                + window.location.host
                + '/ws/refill_payment/create/'
            );

            refillSocket.onmessage = refillSocketOnMessage;
        }
    });
    // возобновление заявки на вывод
    let withdrawButtons = document.querySelectorAll('[href="#selectAmountInput"]');
    for (let withdrawButton of withdrawButtons) {
        withdrawButton.addEventListener("click", function () {
            if (is_auth) {
                if (withdrawSocket !== null && withdrawSocket.readyState === 1) {
                    withdrawSocket.close(1000);
                }
                withdrawSocket = new WebSocket(
                    'wss://'
                    + window.location.host
                    + '/ws/withdraw_payment/create/'
                );

                withdrawSocket.onmessage = withdrawSocketOnMessage;
            }
        });
    }
});

const modal_payment = document.querySelector("#close_withdraw")
modal_payment.addEventListener('click', function(e) {
    if (withdrawSocket !== null && withdrawSocket.readyState === 1) {
        hideFormWithdraw();
    }
})

document.querySelector("#close_refill").addEventListener('click', function(e) {
    if (refillSocket !== null && refillSocket.readyState === 1) {
        hideForm();
    }
})