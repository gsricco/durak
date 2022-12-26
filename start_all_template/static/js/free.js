/* Создание бонусного кода */

const inviteBtn = document.querySelector('.invite__btn');
const textStatus = document.querySelectorAll('.form__msg');
const inviteInput = document.querySelector('.invite__input');
const user_pk = JSON.parse(document.getElementById('user_pk').textContent);
textStatus[1].textContent = '';
textStatus[2].textContent = '';

fetch(`/api/v1/referal_code/${user_pk}/`)
    .then(response => response.json())
    .then(function(data) {
        if (data.hasOwnProperty('ref_code')) {
            checkReferal(data);
        };
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
                var csrf_token = document.querySelector('[name="csrfmiddlewaretoken"]').value;

                let ref_code = {
                    "ref_code": inviteInput.value,
                    "user": user_pk
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