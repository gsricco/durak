function generateItems(winnerCard, cardNumber) {
    const list = document.querySelector('.list');
    let cells = cardNumber
    // let cells;
    const heartsArray = [103, 107, 111, 115]
    const spadesArray = [101, 105, 109, 117]


    // switch (winnerCard) {
    //     case'hearts':
    //         winnerCard = heartsArray[Math.round(Math.random() * (2 + 1))]
    //         break
    //     case'spades':
    //         winnerCard = spadesArray[Math.round(Math.random() * (2 + 1))]
    //         break
    //     case'coin':
    //         winnerCard = 113
    //         break
    // }

    // let numbersCards = Math.round(100 + Math.random() * (121 - 100 + 1))
    // if (winnerCard) {
    //     cells = winnerCard
    // } else {
    //     cells = (numbersCards % 2 === 0) ? numbersCards + 1 : numbersCards
    // }

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
// анимация прокрутки
function startRoll(winnerCard, cardNumber, cardPosition) {
    list.innerHTML = '';
    generateItems(winnerCard, cardNumber);

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
        let rand = min + cardPosition * (max - min + 1);
        return Math.round(rand);
    }

    let swingFinish = `translate3d(${randomInteger(-496, -504) / 10}%, 0, 0)`

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
    }
    // blurForTimer()
    timerCounter1()
}

//дергаем ф-цию что бы все сработало 1 раз при загрузке, дальше по сет интервалу в 29сек
// timerCounter()

//ставим функцию на каждые 29сек
chatSocket.onmessage = super_new(chatSocket.onmessage);
// ! Плавные скроллбары
// if (document.querySelector(".scrollbar-overflow")) {
//     let blockArrow = document.querySelectorAll(".scrollbar-overflow");
//
//     blockArrow.forEach(function (item) {
//         item.addEventListener("touchmove", function () {
//             item.classList.add("scrollbar-overflow_active");
//         });
//
//         item.addEventListener("touchend", function () {
//             setTimeout(function () {
//                 item.classList.remove("scrollbar-overflow_active");
//             }, 1000);
//         });
//     });
// }
function super_new(f){
    return function (){
        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data)
        if (data.init) {
        if (data.init.state === 'countdown') {
            let timeNow = Date.now()
            let remainTime = (20 * 1000 - (timeNow - data.init.t)) / 1000
            timerCounter(remainTime)
        }
        if (data.init.state === 'rolling') {

            startRoll(data.init.winner)

        }
    }
    if (data.current_balance) {
        UserBalance.innerHTML = `${data.current_balance}`
    }

    if (data.from_json) {
        createBidItems(data.from_json)
    }
    if (data.roll) {
        console.log(data, 'new data for BIDS')
        startRoll(data.winner, data.c, data.p)
    }
    // if (data.stop) {
    //     let winnerCard = data.w
    //     //winnerCard from backend
    //     // let winnerCard = `coin` //    !!!!!!!!!!!!!!!!!! data.winner - undefined !!!!!!!!!!!!!!!!!!!!!!!!
    //     // console.log(winnerCard)
    //     let bidsNumber = document.querySelectorAll('.roulette__item-money')
    //     const bidsButtons = document.querySelectorAll('.roulette__radio-item')
    //     bidsNumber.forEach(el => {
    //         el.style.color = 'red'
    //     })}
        if (data.stop) {
        let winnerCard = data.w
        //winnerCard from backend
        // let winnerCard = `coin` //    !!!!!!!!!!!!!!!!!! data.winner - undefined !!!!!!!!!!!!!!!!!!!!!!!!
        let bidsNumber = document.querySelectorAll('.roulette__item-money')
        const bidsButtons = document.querySelectorAll('.roulette__radio-item')
        let signWinnerhearts = document.querySelectorAll('.signWinnerhearts');
        let signWinnercoin = document.querySelectorAll('.signWinnercoin');
        let signWinnerspades = document.querySelectorAll('.signWinnerspades');

        bidsNumber.forEach(el => {
            el.style.color = 'red'
            document.querySelector('#spanCardHearts').style.color = 'red';
            document.querySelector('#spanCardCoin').style.color = 'red';
            document.querySelector('#spanCardSpades').style.color = 'red';
             if(signWinnerhearts){
                 signWinnerhearts.forEach(s=>{
                     s.innerHTML=`-`;
                 })
             }
            if(signWinnercoin){
                signWinnercoin.forEach(s=>{
                    s.innerHTML=`-`;
                })
            }
            if(signWinnerspades){
                signWinnerspades.forEach(s=>{
                    s.innerHTML=`-`;
                })
            }

            if (document.querySelector('.signWinnerHearts')) document.querySelector('.signWinnerHearts').innerHTML = ':-';
            if(document.querySelector('.signWinnerCoin'))document.querySelector('.signWinnerCoin').innerHTML = ':-';
            if(document.querySelector('.signWinnerSpades'))document.querySelector('.signWinnerSpades').innerHTML = ':-';
        })
    //     if (winnerCard === 'hearts') {
    //         let bidsNumber = document.querySelectorAll('.hearts .roulette__item-money')
    //         bidsNumber.forEach(el => {
    //             //обновление баланса user////
    //             let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
    //             console.log(balanceUser)
    //             // /////////////////////
    //             el.style.color = 'green'
    //             document.querySelector('.hearts').style.opacity = '1'
    //             bidsButtons[0].style.opacity = '1'
    //         })
    //     } else if (winnerCard === 'coin') {
    //         let bidsNumber = document.querySelectorAll('.coin .roulette__item-money')
    //         bidsNumber.forEach(el => {
    //             //обновление баланса user////
    //             let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
    //             console.log(balanceUser)
    //             // /////////////////////
    //             el.style.color = 'green'
    //             document.querySelector('.coin').style.opacity = '1'
    //             bidsButtons[1].style.opacity = '1'
    //         })
    //     } else if (winnerCard === 'spades') {
    //         let bidsNumber = document.querySelectorAll('.spades .roulette__item-money')
    //         bidsNumber.forEach(el => {
    //             //обновление баланса user////
    //             let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
    //             console.log(balanceUser)
    //             // /////////////////////
    //             el.style.color = 'green'
    //             document.querySelector('.spades').style.opacity = '1'
    //             bidsButtons[2].style.opacity = '1'
    //         })
    //     }
    // }
            if (winnerCard === 'hearts') {
            let bidsNumber = document.querySelectorAll('.hearts .roulette__item-money')
            bidsNumber.forEach(el => {
                // //обновление баланса user////
                // let balanceUser = `+ document.querySelector('.header__profile-sum>span').innerText`;
                // console.log(balanceUser)
                // // /////////////////////
                el.style.color = 'green'

                if(signWinnerhearts){
                    signWinnerhearts.forEach(s=>{
                        s.innerHTML=`+`;
                    })
                }


                document.querySelector('#spanCardHearts').style.color = 'green';
                document.querySelector('#roulHearts').style.border = '1px solid green';
                document.querySelector('#titleHearts').innerHTML = `ПОБЕДА`;
                document.querySelector('.signWinnerHearts').innerHTML = ':+';
                document.querySelector('.hearts').style.opacity = '1'
                bidsButtons[0].style.opacity = '1'
            })
        } else if (winnerCard === 'coin') {
            let bidsNumber = document.querySelectorAll('.coin .roulette__item-money')
            bidsNumber.forEach(el => {
                // //обновление баланса user////
                // let balanceUser = `+document.querySelector('.header__profile-sum>span').innerText`;
                // console.log(balanceUser)
                // // /////////////////////
                el.style.color = 'green'
                if(signWinnercoin){
                    signWinnercoin.forEach(s=>{
                        s.innerHTML=`+`;
                    })
                }

                document.querySelector('#spanCardCoin').style.color = 'green';
                document.querySelector('#roulCoin').style.border = '1px solid green';
                document.querySelector('#titleCoin').innerHTML = `ПОБЕДА`;
                document.querySelector('.signWinnerCoin').innerHTML = ':+';
                document.querySelector('.coin').style.opacity = '1'
                bidsButtons[1].style.opacity = '1'
            })
        } else if (winnerCard === 'spades') {
            let bidsNumber = document.querySelectorAll('.spades .roulette__item-money')
            bidsNumber.forEach(el => {
                // //обновление баланса user////
                // let balanceUser = document.querySelector('.header__profile-sum>span').innerText;
                // console.log(balanceUser)
                // // /////////////////////
                el.style.color = 'green'
                if(signWinnerspades){
                    signWinnerspades.forEach(s=>{
                        s.innerHTML=`+`;
                    })
                }
                document.querySelector('#spanCardSpades').style.color = 'green';
                document.querySelector('#titleSpades').innerHTML = `ПОБЕДА`;
                document.querySelector('#roulSpades').style.border = '1px solid green';
                document.querySelector('.signWinnerSpades').innerHTML = ':+';
                document.querySelector('.spades').style.opacity = '1'
                bidsButtons[2].style.opacity = '1'
            })
        }}

    if (data.back) {
        //winnerCard from backend
        // let rollCards = ['hearts', 'spades', 'hearts','hearts','hearts', 'hearts','hearts', 'spades'] //-message back roll
        let rollCards = data.previous_rolls
        let rollWinnerOld = document.querySelector('.roulette__previous-items');
        rollWinnerOld.innerHTML = ``
        rollCards.map(roll=>{
            rollWinnerOld.innerHTML += `
            <div class="roulette__previous-item">
                <svg>
                    <use xlink:href="${static_prefix}/img/icons/sprite.svg#${roll}_stroke_grey"></use>
                </svg>
            </div>
            `
        })
        returnToStartPosition()
    }
    if (data.roulette) {
        document.querySelector('#spanCardHearts').innerHTML = ``
        document.querySelector('#spanCardCoin').innerHTML = ``
        document.querySelector('#spanCardSpades').innerHTML = ``
        document.querySelector('#spanCardHearts').style.color = '#fff';
        document.querySelector('#spanCardCoin').style.color = '#fff';
        document.querySelector('#spanCardSpades').style.color = '#fff';
        document.querySelector('#titleHearts').innerHTML = `Черви`
        document.querySelector('#titleCoin').innerHTML = `Монета`
        document.querySelector('#titleSpades').innerHTML = `Пики`
        document.querySelector('#roulSpades').style.border = 'none';
        document.querySelector('#roulCoin').style.border = 'none';
        document.querySelector('#roulHearts').style.border = 'none';

        timerCounter(data.roulette)
    }

}}
