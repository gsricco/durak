let modalCaseLvl = document.querySelector('.modal-cases__lvl')
let modalCaseCount = document.querySelector('.modal-cases__mum')
let modalCaseTitle = document.querySelector('.modal-cases__title')
let minuteTime, secTime, open_time; // переменные для единиц времени
//значки кристалов по уровням
let bigProfLvl = document.querySelector('.profil__progressbar-lvl-num')
let curLvlImage = document.querySelector('.profil__progressbar-lvl-img')
let curLvlBar = document.querySelector('.progress-bar_cur_svg')
let nextLvlBar = document.querySelector('.progress-bar_next_svg')
//кол-во кристалов на уровнях
let curLvlBarCount = document.querySelector('.progress-bar_cur_count')
let nextLvlBarCount = document.querySelector('.progress-bar_next_count')
let timerBlock = document.querySelector('#timerTwo')
// const UserBalanceMob = document.querySelector('.header__balance>span')
const listCase = document.querySelector('.listCase');
const modalCase = document.querySelector('.modal-cases__case');
let profilProgressLine = document.querySelector('.profil_profil__progressbar-line')
let profilProgressExp = document.querySelector('.profil__progressbar-lvl-progress')
let profileCaseTitle
let caseItems

chatSocket.addEventListener('open', (event) => {
    chatSocket.send(JSON.stringify({
        'item': 'init_item',
        'get_cases_items': 'get_cases_items'
    }))
});

// function update_balance(current_balance){
//     UserBalancer = Number(current_balance)
//             // // Отображать надо уже преобразованное число, а использовать пришедшее
//             if ( UserBalancer/ 1000 > 9 && UserBalancer / 1000 < 1000) {
//                 UserBalancerShow = `${UserBalancer / 1000}K`
//             } else {
//                 if (UserBalancer / 1000000 > 0) {
//                     UserBalancerShow = `${UserBalancer / 1000000}M`
//                 } else
//                     UserBalancerShow = `${UserBalancer}`
//             }
//             if (UserBalancer / 1000 > 0 && UserBalancer / 1000 < 10) {
//                 UserBalancerShow = `${UserBalancer}`
//             }
//             UserBalance.innerHTML = `${UserBalancerShow}`
//             UserBalanceMob.innerHTML = `${UserBalancerShow}`
// }

chatSocket.onmessage = super_new(chatSocket.onmessage);

function super_new(f) {
    return function () {
        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data)
        if (data.user_items) {
            newUserItem(data.user_items)
        }

        if (data.lvl_info) {
            set_lvl_info(data.lvl_info)
        }
        if(data.lvlup){
            if(data.lvlup.max_lvl){
                bigProfLvl.innerHTML = data.lvlup.new_lvl + ' LVL'
            }else{
                bigProfLvl.innerHTML = data.lvlup.levels + ' LVL'
             }
            }
        if (data.expr) {
            setExp(data.expr)
        }
        if (data.cases) {
            setModalConst(data.cases)

        }
        // if (data.current_balance) {
        //     update_balance(data.current_balance)
        // }
        if (data.cases_items) {
            caseItems = data.cases_items
        }
        if (data.case_roll_result) {
            generateItemsCase(caseItems[profileCaseTitle].items, data.case_roll_result)
        }
    }
}

function setExp(data) {
    profilProgressLine.style.width = data.percent + '%'
    profilProgressExp.innerHTML = data.current_exp+'/'+data.max_current_lvl_exp
}

//отрисовывает лвл и кристалы
function set_lvl_info(data) {
    if (data.max_lvl) {
        curLvlImage.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.next_lvl_img}"></use>`
    } else {
        curLvlImage.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.cur_lvl_img}"></use>`
    }

    curLvlBar.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.cur_lvl_img}"></use>`
    nextLvlBar.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.next_lvl_img}"></use>`
    curLvlBarCount.innerHTML = data.cur_lvl_case_count + 'шт.'
    nextLvlBarCount.innerHTML = data.next_lvl_case_count + 'шт.'
}

function setModalConst(data) {
    //отображение количества кейсов и их количества в модалке
    modalCaseTitle.innerHTML = profileCaseTitle
    modalCaseLvl.innerHTML = data.user_cases[profileCaseTitle].open_lvl + '+ LVL'
    modalCaseCount.innerHTML = "X" + data.user_cases[profileCaseTitle].count
    //переводит секунды в секунды и минуты
    if (data.open_time.can_be_opened) {
        secTime = 0
        minuteTime = 0
    } else {
        open_time = 3600 - data.open_time.seconds_since_prev_open
        secTime = open_time % 60
        minuteTime = (open_time - secTime) / 60

    }
    //проверка запущен ли уже таймер
    if (timerBlock.textContent === '') {
        timerSecond(data)
    }
}

function newModalUserItem(data) {
    let modalCaseItem = document.querySelector('.modal-cases-all__case')
    let allModCaseItem = document.querySelectorAll('.modal-case__item')
    //при отрисовке новых айтемов удаляет старые
    allModCaseItem.forEach((e) => e.remove())
    data.forEach((e) => {
        let modalItem = document.createElement('a')
        modalItem.className = 'modal-case__item'
        modalItem.innerHTML = `
        <div class="modal-case__wrapper">
                                <div class="modal-case__img">
                                    <svg>
                                        <use xlink:href="${static_prefix}/img/icons/sprite.svg#${e.item.image}"></use>
                                    </svg>
                                </div>
                                <div class="modal-case__title">
                                    ${e.item.name}
                                </div>
                            </div>
        `
        modalCaseItem.appendChild(modalItem)
    })
}

//функция дергается при клике на кейс , берет имя кейса и записывает в переменную
function case_click(e) {
    chatSocket.send(JSON.stringify({
        'cases': 'cases',
    }))
    profileCaseTitle = e.querySelector('.profil__slider-title').textContent
    startCaseListRoll()
    newModalUserItem(caseItems[profileCaseTitle].items)


}

function startCaseListRoll() {
    modalCase.innerHTML = ''
    caseItems[profileCaseTitle].items.map((e) => {
        modalCase.innerHTML += `<div class="modal-case-overflow__item">
                                     <div class="modal-case__wrapper">
                                    <div class="modal-case__img">
                                        <svg>
                                            <use xlink:href="${static_prefix}/img/icons/sprite.svg#${e.item.image}"></use>
                                        </svg>
                                    </div>
                                    <div class="modal-case__title">
                                        ${e.item.name}
                                    </div>
                                </div>
                                   </div>`

    })

}

let butClick = () => {
    chatSocket.send(JSON.stringify({
        'open_case': profileCaseTitle
    }))
}

//! Таймер
function timerSecond(caseData) {
    let btnTimerCase = document.querySelector(".modal-case__btn");
    btnTimerCase.classList.add("btn_white")
    btnTimerCase.style.background = "#272727";
    let timer = setInterval(function () {
        if (secTime < 60 && secTime > 0) {
            secTime -= 1;
        }

        if (secTime === 0 && minuteTime !== 0) {
            minuteTime -= 1;
            secTime = 59;
        }

        if (minuteTime === 0 && secTime === 0) {
            clearInterval(timer);
            if (caseData.user_cases[profileCaseTitle].count > 0) {
                btnTimerCase = document.querySelector(".modal-case__btn");
                btnTimerCase.removeEventListener('click', butClick)
                btnTimerCase.classList.remove("btn_white");
                btnTimerCase.style.background = "#c4364e";
                btnTimerCase.addEventListener('click', butClick)
            }
        }
        if (minuteTime === 0 && secTime === 0) {
            timerBlock.innerHTML = ''
        } else {
            if (secTime >= 10) {
                timerBlock.innerHTML = `${minuteTime}:${secTime}`;
            }

            if (secTime < 10 && secTime >= 0) {
                timerBlock.innerHTML = `${minuteTime}:0${secTime}`;
            }
        }
    }, 1000);
}


function newUserItem(data) {
    let profCaseItem = document.querySelector('.profil__items')
    // profCaseItem.innerHTML = ''
    let allProfCaseItem = document.querySelectorAll('.profil__item')
    allProfCaseItem.forEach((e) => e.remove())
    data.forEach((e) => {
        let cost = e.user_item.selling_price
        let name = e.user_item.name
        let image = e.user_item.image
        let format_cost
        if(cost >= 1000 && cost < 1000000 ){
            format_cost = (cost/1000)+'К'
        } else if (cost >= 1000000 ){
            let countM = cost/1000000
            format_cost = countM+'M'
        }else {
            format_cost = cost
        }
        let new_div = document.createElement('div')
        new_div.className = 'profil__item'
        new_div.innerHTML = `
            <div class="profil__item-wrapper">
                <div class="profil__item-img">
                    <svg>
                        <use xlink:href="${static_prefix}/img/icons/sprite.svg#${image}"></use>
                    </svg>
                </div>
                <h3 class="profil__item-title">${name}</h3>
            </div>
            <div class="profil__item-tags">
                <a href="#choiceObjects" class="profil__item-tag popup-link" 
                onclick="set_forward_items_params('${name}','${image}')">Получить</a>
                <a href="#question" class="profil__item-tag popup-link"
                onclick="set_sell_items_params('${name}',${cost})">Продать за ${format_cost}</a>
            </div>`

        profCaseItem.appendChild(new_div)
    })
    let popupLi = document.querySelectorAll(".profil__item-tag")
    if (popupLi.length > 0) {
        for (let index = 0; index < popupLi.length; index++) {
            const popupLink = popupLi[index];
            popupLink.addEventListener("click", function (e) {
                const popupName = popupLink.getAttribute("href").replace("#", "");
                const curentPopup = document.getElementById(popupName);
                popupOpen(curentPopup);
                e.preventDefault();
            });
        }
    }
}

