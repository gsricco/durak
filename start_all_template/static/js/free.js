/* Создание бонусного кода */
console.log('privet Oleg')
const inviteBtn = document.querySelector('.invite__btn');
const textStatus = document.querySelectorAll('.form__msg');
const inviteInput = document.querySelector('.invite__input');
const channelIdInput = document.querySelector('.s-am-input__input_yt');
const buttonSendYoutubeId = document.querySelector('#ueban');

textStatus[1].textContent = '';
textStatus[2].textContent = '';

fetch(`/api/v1/referal_code/${current_user_id}/`)
    .then(response => response.json())
    .then(function(data) {
        if (data.hasOwnProperty('ref_code')) {
            checkReferal(data);
        }
    });

function checkReferal(refJson) {
    if (refJson.hasOwnProperty('ref_code')) {
        textStatus[1].style.color = 'green';
        textStatus[1].textContent = 'Ваш промокод доступен';
        textStatus[2].style.color = 'green';
        textStatus[2].textContent = 'Ваш промокод доступен';

        inviteInput.style.color = 'green'
        inviteInput.value = refJson.ref_code;
        inviteBtn.innerHTML = "Копировать";
        inviteBtn.disabled = false;
        inviteInput.disabled = true

        inviteBtn.onclick = (e) => {
            const inviteInputValue = refJson.ref_code;
            if (inviteInputValue) {
                navigator.clipboard.writeText(inviteInputValue)
                    .then(() => {
                        inviteInput.style.color = 'white'
                        inviteInput.value = 'Скопированно в буфер';
                        textStatus[1].textContent = 'Промокод скопирован в буфер обмена';
                        textStatus[2].textContent = 'Промокод скопирован в буфер обмена';
                    })
                    .catch(err => {
                        console.log('Something went wrong', err);
                    })
                setTimeout(function () {
                    inviteInput.value = inviteInputValue;
                }, 1000)
            }
            e.preventDefault();
        };
    } else {
        textStatus[1].style.color = 'red';
        textStatus[1].textContent = 'Введённый промокод не доступен.';
        textStatus[2].style.color = 'red';
        textStatus[2].textContent = 'Введённый промокод не доступен.';
        inviteInput.disabled = false;
    }
}

if (inviteBtn) {
    inviteBtn.onclick = function (e) {
        inviteBtn.disabled = true;
        if (!is_auth) {
            const modal = document.querySelector('#authorization')
            modal.classList.add('open')
            modal.addEventListener("click", function (e) {
                if (!e.target.closest(".popup__content")) {
                    popupClose(e.target.closest(".popup"));
                }
            });

        } else {

            if (inviteInput.value !== '') {
                inviteInput.disabled = true;                
                let csrf_token = document.querySelector('[name="csrfmiddlewaretoken"]').value;

                let ref_code = {
                    "ref_code": inviteInput.value,
                    "user": current_user_id
                };
                let result = fetch('/api/v1/referal_code/', {
                    method: 'POST',
                    headers: {
                    'Content-Type': 'application/json;charset=utf-8',
                    "X-CSRFToken": csrf_token
                    },
                    body: JSON.stringify(ref_code)
                })
                .then(response => response.json())
                .then(respJson => checkReferal(respJson));            
            }
        }
        inviteBtn.disabled = false;
        e.preventDefault();  // * чтобы страница не перезагружалась
    }
}

//аккордион Промокода..
const btnAccordionCode = document.querySelector(".accordion.invite__head");
const panelCode = document.querySelector('.panel.invite__panel');

if (btnAccordionCode){
    btnAccordionCode.addEventListener('click',()=>{
        panelCode.style.display = panelCode.style.display === 'block' ? 'none' : 'block'
    })
}

const promoMessage = document.querySelector('#promo_message');
promoMessage.textContent = '';

function checkBonus(response) {
    if (response.status == 200) {
        promoMessage.textContent = 'Промокод активирован.';
        promoMessage.style.color = 'green';
    } else if (response.status == 401) {
        promoMessage.textContent = 'Зарегистрируйтесь на сайте.';
        promoMessage.style.color = 'red';
    } else if (response.status == 403) {
        promoMessage.textContent = 'Промокод уже активирован.';
        promoMessage.style.color = 'red';
    } else if (response.status == 404) {
        promoMessage.textContent = 'Промокод не найден.';
        promoMessage.style.color = 'red';
    }
}

// активация бонусного кода
const activatePromoButton = document.querySelector('#promo_btn');
const activateInput = document.querySelector('.form__input.promo-code__input');
activatePromoButton.onclick = function (e) {
    activatePromoButton.disabled = true;
    if (!is_auth) {
        const modal = document.querySelector('#authorization')
        modal.classList.add('open')
        modal.addEventListener("click", function (e) {
            if (!e.target.closest(".popup__content")) {
                popupClose(e.target.closest(".popup"));
            }
        });
    } else {
        if (activateInput.value !== '') {
            activateInput.disabled = true;                

            fetch('/api/v1/get_bonus/' + activateInput.value.trim())
                .then(response => checkBonus(response));

            activateInput.disabled = false;    
        }
    }
    activatePromoButton.disabled = false;
    e.preventDefault();  // * чтобы страница не перезагружалась
}
chatSocket.onmessage = super_new(chatSocket.onmessage);
function super_new(f) {
    return function () {
        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data)
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
    if(data.sub ==='info') {
        if (data.youtube_subscribe === 'success') {
            show_modal('sub__success')
        } else if (data.youtube_subscribe === 'fail') {
            show_modal('youtubeError')
        }
        if(data.vk_subscribe === 'success'){
            show_modal('sub__success')
        } else if (data.vk_subscribe === 'fail'){
            show_modal('vkError')
        }
    }
    }}
chatSocket.onopen = function (e) {
    chatSocket.send(JSON.stringify({
        'get_free_balance': 'g'
    }));

};
function show_modal(id){
    const modal = document.querySelector(`#${id}`)
    modal.classList.add('open')
    modal.addEventListener("click", function (e) {
        if (!e.target.closest(".popup__content")) {
            popupClose(e.target.closest(".popup"));
}})}
let btn_vk = document.querySelector("#btn_vk");
let btn_youtube = document.querySelector("#btn_youtube");
if(btn_vk){
    btn_vk.addEventListener('click',
        ()=> {
        if (!is_auth) {
            show_modal('authorization')
        }
        else{
            btn_vk.href = "#";
            // let a_inside_button = document.querySelector("#a__inside__button");
            btn_vk.innerHTML = 'Подписка проверяется...';
            // a_inside_button.remove()
            btn_vk.disabled = true;
            btn_vk.style.cursor = 'not-allowed';
            chatSocket.send(JSON.stringify(
                {"vk_youtube_api": 1,
                "subscribe": "vk"}))
    }})
}
if (btn_youtube) {
    btn_youtube.addEventListener('click',
        () => {
            if (!is_auth) {
                show_modal('authorization')
            } else {
                show_modal('youtubeBonus')
            }
        });
}
let btn_vk_new_modal = document.querySelector("#btn_vk_new_modal");
let btn_youtube_new_modal = document.querySelector("#btn_youtube_new_modal");
if (btn_vk_new_modal) {
    btn_vk_new_modal.addEventListener('click',
        () => {
            show_modal('auth_to_vk_you')
        });
}
if(btn_youtube_new_modal){
    btn_youtube_new_modal.addEventListener('click',
        () => {
            show_modal('auth_to_vk_you')
        });
}
if(buttonSendYoutubeId){
    buttonSendYoutubeId.addEventListener('click',
        ()=>{
            const youtubeId = channelIdInput.value;
            if(youtubeId && youtubeId.length === 24 && youtubeId.startsWith('UC')){
                buttonSendYoutubeId.disabled = true;
                buttonSendYoutubeId.style.cursor = 'not-allowed';
                chatSocket.send(JSON.stringify({
                    'vk_youtube_api': 1,
                    'subscribe': 'y',
                    'payload': youtubeId
                    }
                ))
            }
        })
}