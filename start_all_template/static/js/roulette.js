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
    let trWidth;
    if (window.screen.width === 1280) trWidth = 500; else if (window.screen.width === 1920) trWidth = 380; else  if (window.screen.width === 360) trWidth = 740;


    list.style.left = '0%'
    list.style.transform = `translate3d(-${trWidth}px, 0, 0)`
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
            console.log('eto init', data.init.previous_rolls)
            previous_rolls(data.init.previous_rolls)
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
        let signWinnerhearts = document.querySelectorAll('#signWinnerhearts');
        let signWinnercoin = document.querySelectorAll('#signWinnercoin');
        let signWinnerspades = document.querySelectorAll('#signWinnerspades');
        let userUser = document.querySelector('.header__profile-name>span').textContent
            console.log(userUser,'UserUser')

        bidsNumber.forEach(el => {
            el.style.color = '#C4364E'
            document.querySelector('#spanCardHearts').style.color = '#C4364E';
            document.querySelector('#spanCardCoin').style.color = '#C4364E';
            document.querySelector('#spanCardSpades').style.color = '#C4364E';
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

            if (document.querySelector('#signWinnerhearts')) document.querySelector('#signWinnerhearts').innerHTML = '-';
            if(document.querySelector('#signWinnercoin'))document.querySelector('#signWinnercoin').innerHTML = '-';
            if(document.querySelector('#signWinnerspades'))document.querySelector('#signWinnerspades').innerHTML = '-';
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
                el.style.color = '#5DD887'

                if(signWinnerhearts){
                    signWinnerhearts.forEach(s=>{
                        s.innerHTML=`+`;
                    })
                }

                    if (username === userUser) {
                        if (document.querySelector('#spanCardHearts').textContent != '') {
                            if (heartsCounts / 1000 > 9 && heartsCounts / 1000 < 1000) {
                                heartsCountsShow = `${heartsCounts / 1000}K`
                            } else {
                                if (heartsCounts / 1000000 > 0) {
                                    heartsCountsShow = `${heartsCounts / 1000000}M`
                                } else
                                    heartsCountsShow = `${heartsCounts}`
                            }
                            if (heartsCounts / 1000 > 0 && heartsCounts / 1000 < 10) {
                                heartsCountsShow = `${heartsCounts * 2}`
                            }
                            if (window.screen.width > 768) {
                                document.querySelector('#spanCardHearts').innerHTML = `+${heartsCountsShow}`;
                                document.querySelector('#titleHearts').innerHTML = `Победа:`;
                                document.querySelector('#signWinnerhearts').innerHTML = ' +';
                            }

                            document.querySelector('#spanCardHearts').style.color = '#5DD887';
                            document.querySelector('#roulHearts').style.border = '2px solid #5DD887';
                            document.querySelector('#roulHearts').style.borderRadius = '5px';


                        } else {
                            if (window.screen.width < 768 && heartsCountsShow) {
                                document.querySelector('#titleHearts').innerHTML = `Победа: +${heartsCountsShow}`;
                                // document.querySelector('.roulette__item-bid').innerHTML = ``;
                                // document.querySelector('#signWinnerhearts').innerHTML = '';

                            }
                        }
                    }
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
                    if (signWinnercoin) {
                        signWinnercoin.forEach(s => {
                            s.innerHTML = `+`;
                        })
                    }


                    if (username === userUser) {
                        if (document.querySelector('#spanCardCoin').textContent != '') {
                            if (coinCounts / 1000 > 9 && coinCounts / 1000 < 1000) {
                                coinCountsShow = `${coinCounts / 1000}K`
                            } else {
                                if (coinCounts / 1000000 > 0) {
                                    coinCountsShow = `${coinCounts / 1000000}M`
                                } else
                                    coinCountsShow = `${coinCounts}`
                            }
                            if (coinCounts / 1000 > 0 && coinCounts / 1000 < 10) {
                                coinCountsShow = `${coinCounts * 14}`
                            }
                            if (window.screen.width > 768) {
                                document.querySelector('#spanCardCoin').innerHTML = `+${coinCountsShow}`;
                                document.querySelector('#titleCoin').innerHTML = `Победа:`;
                                document.querySelector('#signWinnercoin').innerHTML = ' +';
                            }

                            document.querySelector('#spanCardCoin').style.color = '#5DD887';
                            document.querySelector('#roulCoin').style.border = '2px solid #5DD887';
                            document.querySelector('#roulCoin').style.borderRadius = '5px';


                        } else {
                            if (window.screen.width < 768 && username === coinCountsShow) {
                                document.querySelector('#titleCoin').innerHTML = `Победа: +${coinCountsShow}`;
                                // document.querySelector('.roulette__item-bid').innerHTML = ``;
                                // document.querySelector('#signWinnercoin').innerHTML = '';

                            }
                        }
                    }
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
                if (username === userUser) {
                    if (document.querySelector('#spanCardSpades').textContent != '') {
                        if (spadesCounts / 1000 > 9 && spadesCounts / 1000 < 1000) {
                            spadesCountsShow = `${spadesCounts / 1000}K`
                        } else {
                            if (spadesCounts / 1000000 > 0) {
                                spadesCountsShow = `${spadesCounts / 1000000}M`
                            } else
                                spadesCountsShow = `${spadesCounts}`
                        }
                        if (spadesCounts / 1000 > 0 && spadesCounts / 1000 < 10) {
                            spadesCountsShow = `${spadesCounts * 2}`
                        }
                        if (window.screen.width > 768) {
                            document.querySelector('#spanCardSpades').innerHTML = `+${spadesCountsShow}`;
                            document.querySelector('#titleSpades').innerHTML = `Победа:`;
                            document.querySelector('#signWinnerspades').innerHTML = ' +';
                        }


                        document.querySelector('#spanCardSpades').style.color = '#5DD887';

                        document.querySelector('#roulSpades').style.border = '2px solid #5DD887';
                        document.querySelector('#roulSpades').style.borderRadius = '5px';


                    } else {
                        if (window.screen.width < 768 && spadesCountsShow) {
                            document.querySelector('#titleSpades').innerHTML = `Победа: +${spadesCountsShow}`;
                            // document.querySelector('.roulette__item-bid').innerHTML = ``;
                            // document.querySelector('#signWinnerspades').innerHTML = '';

                        }
                    }
                }
                document.querySelector('.spades').style.opacity = '1'
                bidsButtons[2].style.opacity = '1'
            })
            }
        }

    if (data.back) {
        previous_rolls(data.previous_rolls)
        returnToStartPosition()
    }
    if (data.roulette) {
        document.querySelector('#spanCardHearts').innerHTML = ``
        document.querySelector('#spanCardCoin').innerHTML = ``
        document.querySelector('#spanCardSpades').innerHTML = ``
        document.querySelector('#spanCardHearts').style.color = '#FFECA8';
        document.querySelector('#spanCardCoin').style.color = '#FFECA8';
        document.querySelector('#spanCardSpades').style.color = '#FFECA8';
        document.querySelector('#titleHearts').innerHTML = `Черви`
        document.querySelector('#titleCoin').innerHTML = `Монета`
        document.querySelector('#titleSpades').innerHTML = `Пики`
        document.querySelector('#roulSpades').style.border = 'none';
        document.querySelector('#roulCoin').style.border = 'none';
        document.querySelector('#roulHearts').style.border = 'none';

        timerCounter(data.roulette)
    }

}}
// Отрисовка предыдущих победителей
function previous_rolls(rolls){
    console.log('eto prev roll', rolls)
        let rollWinnerOld = document.querySelector('.roulette__previous-items');
        rollWinnerOld.innerHTML = ``
        rolls.map(roll=>{
            rollWinnerOld.innerHTML += `
            <div class="roulette__previous-item">
                <svg>
                    <use xlink:href="${static_prefix}/img/icons/sprite.svg#${roll}_stroke_grey"></use>
                </svg>
            </div>
            `
        })
}