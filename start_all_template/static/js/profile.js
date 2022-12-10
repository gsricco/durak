let modalCaseLvl = document.querySelector('.modal-cases__lvl')
let modalCaseCount = document.querySelector('.modal-cases__mum')
let modalCaseTitle = document.querySelector('.modal-cases__title')
let minuteTime, secTime, open_time; // переменные для единиц времени
//значки кристалов по уровням
let curLvlImage = document.querySelector('.profil__progressbar-lvl-img')
let curLvlBar = document.querySelector('.progress-bar_cur_svg')
let nextLvlBar = document.querySelector('.progress-bar_next_svg')
//кол-во кристалов на уровнях
let curLvlBarCount = document.querySelector('.progress-bar_cur_count')
let nextLvlBarCount = document.querySelector('.progress-bar_next_count')
// let countdown = document.getElementById("timer"); // получить элемент тега
let timerBlock = document.querySelector('#timerTwo')
let profileCaseTitle
let caseData

function set_lvl_info(data) {
    curLvlImage.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.cur_lvl_img}"></use>`
    curLvlBar.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.cur_lvl_img}"></use>`
    nextLvlBar.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.next_lvl_img}"></use>`
    curLvlBarCount.innerHTML = data.cur_lvl_case_count + 'шт.'
    nextLvlBarCount.innerHTML = data.next_lvl_case_count + 'шт.'
}

function setModalConst(data) {
    caseData = data
    //отображение количества кейсов и их количества в модалке

    modalCaseTitle.innerHTML = profileCaseTitle
    modalCaseLvl.innerHTML = caseData.user_cases[profileCaseTitle].open_lvl + '+ LVL'
    modalCaseCount.innerHTML = "X" + caseData.user_cases[profileCaseTitle].count
    console.log(3600 - data.open_time.seconds_since_prev_open)


    open_time = 3600 - data.open_time.seconds_since_prev_open
    secTime = open_time % 60
    minuteTime = (open_time - secTime) / 60
    if (timerBlock.textContent === '') {
        timerSecond()
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
                                        <use xlink:href="${static_prefix}/img/icons/sprite.svg#${e.user_item.image}"></use>
                                    </svg>
                                </div>
                                <div class="modal-case__title">
                                    ${e.user_item.name}
                                </div>
                            </div>
        `
        modalCaseItem.appendChild(modalItem)
    })
}

//функция дергается при клике на кейс , берет имя кейса и записывает в переменную
function case_click(e) {
    chatSocket.send(JSON.stringify({
        'cases': 'cases'
    }))
    profileCaseTitle = e.querySelector('.profil__slider-title').textContent
}


//! Таймер
// if (document.querySelector(".timer")) {
function timerSecond() {
    let timer = setInterval(function () {
        if (secTime < 60) {
            secTime -= 1;
        }

        if (secTime === 0 && minuteTime !== 0) {
            minuteTime -= 1;
            secTime = 59;
        }

        if (minuteTime < 1 && secTime < 1) {
            var countclick = 0
            console.log(timerBlock)
            clearInterval(timer);
            let btnTimerCase = document.querySelector(".modal-case__btn");
                if (caseData.user_cases[profileCaseTitle].count !== 0 ) {
                    btnTimerCase.classList.remove("btn_white");
                    btnTimerCase.style.background = "#c4364e";
                    btnTimerCase.addEventListener('click', () => {
                        chatSocket.send(JSON.stringify({
                            'open_case': profileCaseTitle
                        }))
                    })
                }

        }

        if (secTime >= 10) {
            timerBlock.innerHTML = `${minuteTime}:${secTime}`;
        }

        if (secTime < 10 && secTime >= 0) {
            timerBlock.innerHTML = `${minuteTime}:0${secTime}`;
        }
    }, 1000);
}

// }

function newUserItem(data) {
    let profCaseItem = document.querySelector('.profil__items')
    let allProfCaseItem = document.querySelectorAll('.profil__item')
    allProfCaseItem.forEach((e) => e.remove())
    data.forEach((e) => {
        console.log(e)
        let new_div = document.createElement('div')
        new_div.className = 'profil__item'
        new_div.innerHTML = `
            <div class="profil__item-wrapper">
                <div class="profil__item-img">
                    <svg>
                        <use xlink:href="${static_prefix}/img/icons/sprite.svg#${e.user_item.image}"></use>
                    </svg>
                </div>
                <h3 class="profil__item-title">${e.user_item.name}</h3>
            </div>
            <div class="profil__item-tags">
                <a href="#choiceObjects" class="profil__item-tag popup-link">Получить</a>
                <a href="#question" class="profil__item-tag popup-link">Продать за ${e.user_item.selling_price}</a>
            </div>`

        profCaseItem.appendChild(new_div)
    })
}

// if (document.querySelector(".instruction")) {
//     let repeateOne = 0;
//     document
//         .querySelector(".instruction")
//         .addEventListener("click", function () {
//             if (repeateOne < 1) {
//                 timerSecond("#timerOne", function () {
//                     let btnTimerInstructin =
//                         document.querySelector(".modal-manual__btn");
//                     btnTimerInstructin.classList.remove("btn_white");
//                     btnTimerInstructin.innerHTML = "Начать";
//                     btnTimerInstructin.addEventListener("click", function (event) {
//                         if (event.target.textContent == "Начать") {
//                             event.target.innerHTML = "<span>Ожидайте..</span>";
//                             event.target.classList.add("btn_white");
//                         }
//                     });
//                 });
//                 repeateOne++;
//             }
//         });
// }

