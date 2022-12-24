const items = document.querySelectorAll('.roulette__radio-item > label')
const bidsBlock = document.querySelectorAll('.roulette__item-body')
const bidsButtons = document.querySelectorAll('.roulette__radio-item')
let balanceUserShow;

var heartsCountsShow;
var heartsCounts;
var coinCounts;
var spadesCounts;
var coinCountsShow;
var spadesCountsShow;
var heartsCountsShowMob;
var heartsCountsMob;
var coinCountsMob;
var spadesCountsMob;
var coinCountsShowMob;
var spadesCountsShowMob;
var userCountHearts;
var userCountCoin;
var userCountSpades;


const createBidItems = (data) => {
    document.querySelector(`.hearts`).innerHTML = ''
    document.querySelector(`.coin`).innerHTML = ''
    document.querySelector(`.spades`).innerHTML = ''

    let usersId = (Object.keys(data))
    let memberHeartsShow = '';
    let memberCoinShow = '';
    let memberSpadesShow = '';
    userCountHearts = 0;
    userCountCoin = 0;
    userCountSpades = 0;
    heartsCounts = 0;
    coinCounts = 0;
    spadesCounts = 0;
    heartsCountsShow = '';
    coinCountsShow = '';
    spadesCountsShow = '';
    heartsCountsMob = 0;
    coinCountsMob = 0;
    spadesCountsMob = 0;
    heartsCountsShowMob = '';
    coinCountsShowMob = '';
    spadesCountsShowMob = '';
    let usersBids = []
    usersId.map(user => {
//суммирования всех для мобилок
        if (data[user]['amount']['hearts']) {
            userCountHearts += 1
            heartsCountsMob += data[user]['amount']['hearts']
            if (heartsCountsMob / 1000 > 9 && heartsCountsMob / 1000 < 1000) {
                heartsCountsShowMob = `${heartsCountsMob / 1000}K`
            } else {
                if (heartsCountsMob / 1000000 > 0) {
                    heartsCountsShowMob = `${heartsCountsMob / 1000000}M`
                } else
                    heartsCountsShowMob = `${heartsCountsMob}`
            }
            if (heartsCountsMob / 1000 > 0 && heartsCountsMob / 1000 < 10) {
                heartsCountsShowMob = `${heartsCountsMob}`
            }
            document.querySelector('#spanCardHeartsMob').innerHTML = `${heartsCountsShowMob}`
        }
        if (data[user]['amount']['coin']) {
            userCountCoin += 1
            coinCountsMob += data[user]['amount']['coin']
            if (coinCountsMob / 1000 > 9 && coinCountsMob / 1000 < 1000) {
                coinCountsShowMob = `${coinCountsMob / 1000}K`
            } else {
                if (coinCountsMob / 1000000 > 0) {
                    coinCountsShowMob = `${coinCountsMob / 1000000}M`
                } else
                    coinCountsShowMob = `${coinCountsMob}`
            }
            if (coinCountsMob / 1000 > 0 && coinCountsMob / 1000 < 10) {
                coinCountsShowMob = `${coinCountsMob}`
            }
            document.querySelector('#spanCardCoinMob').innerHTML = `${coinCountsShowMob}`

        }
        if (data[user]['amount']['spades']) {
            userCountSpades += 1
            spadesCountsMob += data[user]['amount']['spades']
            if (spadesCountsMob / 1000 > 9 && spadesCountsMob / 1000 < 1000) {
                spadesCountsShowMob = `${spadesCountsMob / 1000}K`
            } else {
                if (spadesCountsMob / 1000000 > 0) {
                    spadesCountsShowMob = `${spadesCountsMob / 1000000}M`
                } else
                    spadesCountsShowMob = `${spadesCountsMob}`
            }
            if (spadesCountsMob / 1000 > 0 && spadesCountsMob / 1000 < 10) {
                spadesCountsShowMob = `${spadesCountsMob}`
            }
            document.querySelector('#spanCardSpadesMob').innerHTML = `${spadesCountsShowMob}`
        }

//суммирование в заголовке
        if (data[user]['userName'] === username) {
            if (data[user]['amount']['hearts']) {
                heartsCounts += data[user]['amount']['hearts']
                if (heartsCounts / 1000 > 9 && heartsCounts / 1000 < 1000) {
                    heartsCountsShow = `${heartsCounts / 1000}K`
                } else {
                    if (heartsCounts / 1000000 > 0) {
                        heartsCountsShow = `${heartsCounts / 1000000}M`
                    } else
                        heartsCountsShow = `${heartsCounts}`
                }
                if (heartsCounts / 1000 > 0 && heartsCounts / 1000 < 10) {
                    heartsCountsShow = `${heartsCounts}`
                }
                document.querySelector('#titleHearts').innerHTML = `Черви: `;
                document.querySelector('#spanCardHearts').innerHTML = `<span id="signWinnerhearts"></span>${heartsCountsShow}`
                // document.querySelector('#spanCardHeartsMob').innerHTML = `<span id="signWinnerhearts"></span>${heartsCountsShow}`

            }
            if (data[user]['amount']['coin']) {
                coinCounts += data[user]['amount']['coin']
                if (coinCounts / 1000 > 9 && coinCounts / 1000 < 1000) {
                    coinCountsShow = `${coinCounts / 1000}K`
                } else {
                    if (coinCounts / 1000000 > 0) {
                        coinCountsShow = `${coinCounts / 1000000}M`
                    } else
                        coinCountsShow = `${coinCounts}`
                }
                if (coinCounts / 1000 > 0 && coinCounts / 1000 < 10) {
                    coinCountsShow = `${coinCounts}`
                }
                document.querySelector('#titleCoin').innerHTML = `Монета: `;
                document.querySelector('#spanCardCoin').innerHTML = `<span id="signWinnercoin"></span>${coinCountsShow}`
                // document.querySelector('#spanCardCoinMob').innerHTML = `<span id="signWinnercoin"></span>${coinCountsShow}`
            }

            if (data[user]['amount']['spades']) {
                spadesCounts += data[user]['amount']['spades']
                if (spadesCounts / 1000 > 9 && spadesCounts / 1000 < 1000) {
                    spadesCountsShow = `${spadesCounts / 1000}K`
                } else {
                    if (spadesCounts / 1000000 > 0) {
                        spadesCountsShow = `${spadesCounts / 1000000}M`
                    } else
                        spadesCountsShow = `${spadesCounts}`
                }
                if (spadesCounts / 1000 > 0 && spadesCounts / 1000 < 10) {
                    spadesCountsShow = `${spadesCounts}`
                }
                document.querySelector('#spanCardSpades').innerHTML = `<span id="signWinnerspades"></span>${spadesCountsShow}`;
                document.querySelector('#titleSpades').innerHTML = `Пики: `;
                // document.querySelector('#spanCardSpadesMob').innerHTML = `<span id="signWinnerspades"></span>${spadesCountsShow}`
            }
        }

        let objAmount = data[user]['amount']
        let keys = Object.keys(objAmount); //получаем ключи объекта в виде массива
        let avatar = data[user]['avatar']
        let rubin = data[user]['rubin']
        let userName = data[user]['userName']

        keys.map(card => {
            user = {
                avatar: avatar,
                bidCard: card,
                bidCount: objAmount[card],
                rubin: rubin,
                userName: userName
            }
            usersBids.push(user)//создание массива всех ставок
            usersBids.sort((a, b) => b.bidCount - a.bidCount)//сортировка по ставкам
        })
    })

    usersBids.map(el => {
        // отрисовка  ставки одной масти одного пользователя
        const bidItemBlock = document.querySelector(`.${el.bidCard}`)

        const bidItem = document.createElement('div')
        bidItem.className = 'roulette__item-row'
        bidItemBlock.appendChild(bidItem)

        const bidItemLeftBlock = document.createElement('div')
        bidItemLeftBlock.className = 'roulette__item-left'
        bidItem.appendChild(bidItemLeftBlock)

        const itemMoney = document.createElement('div')
        itemMoney.className = 'roulette__item-money'
        itemMoney.innerHTML = `<span id="signWinner${el.bidCard}"></span>${el.bidCount}`
        bidItem.appendChild(itemMoney)

        const itemAvatar = document.createElement('div')
        itemAvatar.className = 'roulette__item-avatar'
        itemAvatar.innerHTML = `<img src="${el.avatar}" alt="">`
        bidItemLeftBlock.appendChild(itemAvatar)

        const itemStone = document.createElement('div')
        itemStone.className = 'roulette__item-stoun'
        const stone = document.createElementNS("http://www.w3.org/2000/svg", "svg")
        stone.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${el.rubin}"></use>`
        itemStone.appendChild(stone)
        bidItemLeftBlock.appendChild(itemStone)

        const itemUserName = document.createElement('div')
        itemUserName.className = 'roulette__item-username'
        itemUserName.innerHTML = `${el.userName}`
        bidItemLeftBlock.appendChild(itemUserName)
    })
    switch (userCountHearts){
        case 1: {
            memberHeartsShow = 'участник';
            break;
        }
        case 2:
        case 3:
        case 4:
        {
            memberHeartsShow = 'участника';
            break;
        }
            default:{
                memberHeartsShow = 'участников';
                break;
            }
    }
switch (userCountCoin){
        case 1: {
            memberCoinShow = 'участник';
            break;
        }
        case 2:
        case 3:
        case 4:
        {
            memberCoinShow = 'участника';
            break;
        }
            default:{
                memberCoinShow = 'участников';
                break;
            }
    }
switch (userCountSpades){
        case 1: {
            memberSpadesShow = 'участник';
            break;
        }
        case 2:
        case 3:
        case 4:
        {
            memberSpadesShow = 'участника';
            break;
        }
            default:{
                memberSpadesShow = 'участников';
                break;
            }
    }


    document.querySelector('#memberHearts').innerHTML = `${userCountHearts} ${memberHeartsShow}`
    document.querySelector('#memberCoin').innerHTML = `${userCountCoin} ${memberCoinShow}`
    document.querySelector('#memberSpades').innerHTML = `${userCountSpades} ${memberSpadesShow}`
}


// const items = document.querySelectorAll('.roulette__radio-item > label')
const itemsClick = (bidCard) => {


    let bidCount = document.querySelector('.roulette__table-input').value * 1000;

    if (!is_auth) {

        ///////////вывод модалки НЕ_АВТОРИЗОВАН///////////////////
        let modalAuth = document.querySelector('#authorization')
        modalAuth.classList.add("open");
        modalAuth.addEventListener("click", function (e) {
            if (!e.target.closest(".popup__content")) {
                document.querySelector('.popup.open').classList.remove("open");
            }
        });
    } else if (bidCount) {

        let userBalFront = document.querySelector('.header__profile-sum>span')
        // let userBalFront = Number(document.querySelector('.header__profile-sum>span').textContent)
        let userBal = userBalFront.textContent;
        let lastSymbol = userBal[userBal.length-1];
        let balanceUser;


        if(lastSymbol === 'M'){
            balanceUser=Number(userBal.slice(0,userBal.length-1))*1000000
        } else if(lastSymbol === 'K'){
            balanceUser=Number(userBal.slice(0,userBal.length-1))*1000
        }else balanceUser=Number(userBal)



        // let balanceUser = Number(document.querySelector('.header__profile-sum>span').textContent)
        if (balanceUser + 1 >= Number(bidCount)) {


            chatSocket.send(JSON.stringify({
                'bet': {
                    'bidCount': bidCount,
                    'userName': username,
                    'avatar': ava,
                    'rubin': rubin,
                    'bidCard': bidCard
                }
            }));
            if (bidCard === 'hearts') {
                items[2].style.pointerEvents = 'none';
            } else if (bidCard === 'spades') {
                items[0].style.pointerEvents = 'none';
            }

            ///////////////////////////////////////////////
            //логика БЭК отнимания ставки от баланса/////////
            /////пока на фронте//////////////////////////////
            balanceUser = balanceUser - Number(bidCount)


            if (balanceUser / 1000 > 9 && balanceUser / 1000 < 1000) {
                balanceUserShow = `${balanceUser / 1000}K`
            } else {
                if (balanceUser / 1000000 > 0) {
                    balanceUserShow = `${balanceUser / 1000000}M`
                } else
                    balanceUserShow = `${balanceUser}`
            }
            if (balanceUser / 1000 > 0 && balanceUser / 1000 < 10) {
                balanceUserShow = `${balanceUser}`
            }


            document.querySelector('.header__profile-sum>span').innerHTML = `${balanceUserShow}`
            document.querySelector('#userBalMob').innerHTML = `${balanceUserShow}`
            // items[0].style.pointerEvents = 'none';
            /////////////////////////////////////////////////
        } else {
            //вывод сообщения НЕДОСТАТОЧНО СРЕДСТВ
            if (window.screen.width > 542) {
                let modalMoney = document.querySelector('#modalMoney')
                modalMoney.classList.add("open");
                // document.querySelector('.modal__balance').innerHTML = ` Ваш баланс: ${balanceUser}`
                modalMoney.addEventListener("click", function (e) {
                    if (!e.target.closest(".popup__content")) {
                        document.querySelector('.popup.open').classList.remove("open");
                    }
                });
            } else {
                document.querySelector('.roulette__msg').innerHTML = `Недостастаточно кредитов`;
                setTimeout(() => {
                    document.querySelector('.roulette__msg').innerHTML = ``;
                }, 2000)
            }
///////////////////////////////////////////////////////////////////////////////////
        }
        document.querySelector('.roulette__table-input').value = ''
        document.querySelector('.roulette__current-block').innerHTML = '';

    }
}

items[0].addEventListener('click', () => itemsClick('hearts'))
items[1].addEventListener('click', () => itemsClick('coin'))
items[2].addEventListener('click', () => itemsClick('spades'))
