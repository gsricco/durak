let unlock = true;
const body = document.querySelector("body");
const lockPadding = document.querySelectorAll(".lock-padding");
const timeout = 800;


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

    unlock = false;
    setTimeout(function () {
        unlock = true;
    }, timeout);
}

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
    }, timeout);

    unlock = false;
    setTimeout(function () {
        unlock = true;
    }, timeout);
}

document.addEventListener("keydown", function (e) {
    if (e.which === 27) {
        const popupActive = document.querySelector(".popup.open");
        popupClose(popupActive);
    }
});

function popupOpen(curentPopup) {
    if (curentPopup && unlock) {
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
}

function popupClose(popupActive, doUnLock = true) {
    if (unlock) {
        popupActive.classList.remove("open");
        if (doUnLock) {
            bodyUnLock();
        }
    }
}

var soldItemName, soldItemCost, forwarItemName, forwarItemUrl

function set_sell_items_params(name, cost) {
    soldItemName = name
    soldItemCost = cost
}

function set_forward_items_params(name, image) {
    forwarItemName = name
    forwarItemImage = image
}

function forward_user_item() {
    let usernameInput = document.querySelector('#modal-forward-username-input')
    console.log(usernameInput.value)
    chatSocket.send(JSON.stringify({
        'chat_type':'support',
        'forward_user_item': {
            'durak_username': usernameInput.value,
            'item_name': forwarItemName,
            'item_image' : forwarItemImage
        }
    }))
    let mod = document.querySelector('#choiceObjects')
    popupClose(mod)

}

function sell_user_item() {
    chatSocket.send(JSON.stringify({
        'sell_user_item': {'name': soldItemName, 'cost': soldItemCost}
    }))
    let mod = document.querySelector('#question')
    popupClose(mod)
    soldItemName = ''
    soldItemCost = ''
}