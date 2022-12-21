function generateItems(winnerCard, cardNumber) {
    const list = document.querySelector('.list');
    let cells = cardNumber

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
    if (window.screen.width === 1920) trWidth = 380;
    if (window.screen.width === 1366) trWidth = 470;
    if (window.screen.width === 1280) trWidth = 500;
    if (window.screen.width === 1080) trWidth = 530;
    if (window.screen.width === 1024) trWidth = 550;
    if (window.screen.width === 991) trWidth = 420;
    if (window.screen.width === 800) trWidth = 515;
    if (window.screen.width === 767) trWidth = 530;
    if (window.screen.width === 750) trWidth = 530;
    if (window.screen.width === 640) trWidth = 590;
    if (window.screen.width === 414) trWidth = 850;
    if (window.screen.width === 412) trWidth = 860;
    if (window.screen.width === 375) trWidth = 650;
    if (window.screen.width === 360) trWidth = 655;


    list.style.left = '0%'
    list.style.transform = `translate3d(-${trWidth}px, 0, 0)`
    list.style.transition = '1s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
    wrapperItems.classList.add("roulette__rull-wrapper_blur");
    timerWrapper.style.display = "flex";

    rull_line.style.display = "none";
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
    // rull_line.style.display = "inline-block";
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

function super_new(f) {
    return function () {
        let bidsNumber = document.querySelectorAll('.roulette__item-money')
        let bidsNumberMob = document.querySelectorAll('.roulette__accardion-num')
        const bidsButtons = document.querySelectorAll('.roulette__radio-item')
        let signWinnerhearts = document.querySelectorAll('#signWinnerhearts');
        let signWinnercoin = document.querySelectorAll('#signWinnercoin');
        let signWinnerspades = document.querySelectorAll('#signWinnerspades');
        let userUser = document.querySelector('.header__profile-name>span').textContent
        const UserBalanceMob = document.querySelector('.header__balance>span')


        function rouletteInitialSettings() {
            document.querySelector('#spanCardHearts').innerHTML = ``
            document.querySelector('#spanCardHeartsMob').innerHTML = ``
            document.querySelector('#spanCardCoin').innerHTML = ``
            document.querySelector('#spanCardCoinMob').innerHTML = ``
            document.querySelector('#spanCardSpades').innerHTML = ``
            document.querySelector('#spanCardSpadesMob').innerHTML = ``
            document.querySelector('#spanCardHearts').style.color = '#FFECA8';
            document.querySelector('#spanCardCoin').style.color = '#FFECA8';
            document.querySelector('#spanCardSpades').style.color = '#FFECA8';
            document.querySelector('#spanCardHeartsMob').style.color = '#9A9A9A;';
            document.querySelector('#spanCardCoinMob').style.color = '#9A9A9A;';
            document.querySelector('#spanCardSpadesMob').style.color = '#9A9A9A;';
            document.querySelector('#titleHearts').innerHTML = `Черви`
            document.querySelector('#titleCoin').innerHTML = `Монета`
            document.querySelector('#titleSpades').innerHTML = `Пики`
            document.querySelector('#roulSpades').style.border = 'none';
            document.querySelector('#roulCoin').style.border = 'none';
            document.querySelector('#roulHearts').style.border = 'none';
            document.querySelector('#itemHeartsBid').innerHTML = `<span>Ставка</span> Х2`;
            document.querySelector('#itemCoinBid').innerHTML = `<span>Ставка</span> Х14`;
            document.querySelector('#itemSpadesBid').innerHTML = `<span>Ставка</span> Х2`;
            document.querySelector('#memberHearts').innerHTML=`0 участников`
            document.querySelector('#memberCoin').innerHTML=`0 участников`
            document.querySelector('#memberSpades').innerHTML=`0 участников`
        }

        function winnerCheckInitialSettings() {
            bidsNumber.forEach(el => {
                el.style.color = '#C4364E'
                document.querySelector('#spanCardHearts').style.color = '#C4364E';
                document.querySelector('#spanCardCoin').style.color = '#C4364E';
                document.querySelector('#spanCardSpades').style.color = '#C4364E';

                if (signWinnerhearts) {
                    signWinnerhearts.forEach(s => {
                        s.innerHTML = `-`;
                    })
                }
                if (signWinnercoin) {
                    signWinnercoin.forEach(s => {
                        s.innerHTML = `-`;
                    })
                }
                if (signWinnerspades) {
                    signWinnerspades.forEach(s => {
                        s.innerHTML = `-`;
                    })
                }

                if (document.querySelector('#signWinnerhearts')) document.querySelector('#signWinnerhearts').innerHTML = '-';
                if (document.querySelector('#signWinnercoin')) document.querySelector('#signWinnercoin').innerHTML = '-';
                if (document.querySelector('#signWinnerspades')) document.querySelector('#signWinnerspades').innerHTML = '-';

            })
            // bidsNumberMob.forEach(el => {
            //     el.style.color = '#C4364E'
            //     document.querySelector('#spanCardHeartsMob').style.color = '#C4364E';
            //     document.querySelector('#spanCardCoinMob').style.color = '#C4364E';
            //     document.querySelector('#spanCardSpadesMob').style.color = '#C4364E';
            //
            //
            //     if (document.querySelector('#signWinnerheartsMob')) document.querySelector('#spanCardHeartsMob').innerHTML = `-${heartsCountsShow}`;
            //     if (document.querySelector('#signWinnercoinMob')) document.querySelector('#spanCardCoinMob').innerHTML = `-${coinCountsShow}`;
            //     if (document.querySelector('#signWinnerspadesMob')) document.querySelector('#spanCardSpadesMob').innerHTML = `-${spadesCountsShow}`;
            //
            // })
        }

        function checkWinner(cardWinner, bidIncrease) {
            let signWinner, counts, countsShow;
            let lowerCard = cardWinner.toLowerCase();
            let nameWinnerCard = cardWinner[0].toUpperCase() + cardWinner.slice(1);
            console.log(lowerCard, nameWinnerCard)
            let bidsNumber = document.querySelectorAll(`.${lowerCard} .roulette__item-money`)
            bidsNumber.forEach(el => {
                el.style.color = '#5DD887'

                switch (lowerCard) {
                    case 'hearts': {
                        signWinner = signWinnerhearts;
                        counts = heartsCounts;
                        countsShow = heartsCountsShow;
                        break;
                    }
                    case 'coin': {
                        signWinner = signWinnercoin;
                        counts = coinCounts;
                        countsShow = coinCountsShow;
                        break;
                    }
                    case 'spades': {
                        signWinner = signWinnerspades;
                        counts = spadesCounts;
                        countsShow = spadesCountsShow;
                        break;
                    }

                }

                if (signWinner) {
                    signWinner.forEach(s => {
                        s.innerHTML = `+`;
                    })
                }
                if (username === userUser && document.querySelector(`#spanCard${nameWinnerCard}`).textContent != '') {
                    if (counts * bidIncrease / 1000 > 9 && counts * bidIncrease / 1000 < 1000) {
                        countsShow = `${counts * 2 / 1000}K`
                    } else {
                        if (counts * bidIncrease / 1000000 > 0) {
                            countsShow = `${counts * bidIncrease / 1000000}M`
                        } else
                            countsShow = `${counts * bidIncrease}`
                    }
                    if (counts * bidIncrease / 1000 > 0 && counts * bidIncrease / 1000 < 10) {
                        countsShow = `${counts * bidIncrease}`
                    }
                    console.log(countsShow)
                    document.querySelector(`#spanCard${nameWinnerCard}`).innerHTML = `+${countsShow}`;
                    document.querySelector(`#title${nameWinnerCard}`).innerHTML = `Победа:`;
                    document.querySelector(`#signWinner${lowerCard}`).innerHTML = ' +';
                    document.querySelector(`#spanCard${nameWinnerCard}`).style.color = '#5DD887';
                    document.querySelector(`#roul${nameWinnerCard}`).style.border = '1px solid #5DD887';
                    document.querySelector(`#roul${nameWinnerCard}`).style.borderRadius = '5px';
                    // if (window.screen.width < 768) {
                    //     document.querySelector(`#spanCard${nameWinnerCard}Mob`).innerHTML = `+${countsShow}`;
                    //     document.querySelector(`#spanCard${nameWinnerCard}Mob`).style.color = '#5DD887';
                    //     document.querySelector(`#item${nameWinnerCard}Bid`).innerHTML = ``;
                    // }
                }
                document.querySelector(`.${lowerCard}`).style.opacity = '1'
                bidsButtons[0].style.opacity = '1'
            })
        }

        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data);
        if(data.bets){
                createBidItems(data.bets)
            }
        if (data.init) {
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
        console.log(document.querySelector('#userBal').textContent, 'BALANCE_FRONT_FOREVER')
        if (data.current_balance) {
            console.log(data.current_balance,"BALANCE_BACK")
            console.log(document.querySelector('#userBal').textContent, 'BALANCE_FRONT')
            UserBalancer = Number(data.current_balance)
            // // Отображать надо уже преобразованное число, а использовать пришедшее
            if ( UserBalancer/ 1000 > 9 && UserBalancer / 1000 < 1000) {
                UserBalancerShow = `${UserBalancer / 1000}K`
            } else {
                if (UserBalancer / 1000000 > 0) {
                    UserBalancerShow = `${UserBalancer / 1000000}M`
                } else
                    UserBalancerShow = `${UserBalancer}`
            }
            if (UserBalancer / 1000 > 0 && UserBalancer / 1000 < 10) {
                UserBalancerShow = `${UserBalancer}`
            }


            //
            UserBalance.innerHTML = `${UserBalancerShow}`
            UserBalanceMob.innerHTML = `${UserBalancerShow}`
            // UserBalance.innerHTML = `${data.current_balance}`
        }

        if (data.from_json) {
            createBidItems(data.from_json)
        }
        if (data.roll) {
            console.log(data, 'new data for BIDS')
            startRoll(data.winner, data.c, data.p)
        }

        if (data.stop) {
            let winnerCard = data.w
            winnerCheckInitialSettings();
            if (winnerCard === 'hearts') {
                checkWinner('hearts', 2)
            } else if (winnerCard === 'coin') {
                checkWinner('coin', 14)
            } else if (winnerCard === 'spades') {
                checkWinner('spades', 2)
            }
        }

        if (data.back) {
            previous_rolls(data.previous_rolls)
            returnToStartPosition()
        }
        if (data.roulette) {
            rouletteInitialSettings();
            timerCounter(data.roulette)
        }

    }
}

// Отрисовка предыдущих победителей
function previous_rolls(rolls) {
    console.log('eto prev roll', rolls)
    let rollWinnerOld = document.querySelector('.roulette__previous-items');
    rollWinnerOld.innerHTML = ``
    rolls.map(roll => {
        rollWinnerOld.innerHTML += `
            <div class="roulette__previous-item">
                <svg>
                    <use xlink:href="${static_prefix}/img/icons/sprite.svg#${roll}_stroke_grey"></use>
                </svg>
            </div>
            `
    })
}