const items = document.querySelectorAll('.roulette__radio-item > label')
const bidsBlock = document.querySelectorAll('.roulette__item-body')
const bidsButtons = document.querySelectorAll('.roulette__radio-item')
let balanceUserShow;

// const createBidItemRow = (data) => {
//     const bidItemBlock = document.querySelector(`.${data.bet.bidCard}`)
//
//     if (bidItemBlock.innerHTML != ``) {
//         let itemMoney = document.querySelector(`div.${data.bet.bidCard} div.roulette__item-money`)
//         let bidOld = Number(itemMoney.textContent) + Number(`${data.bet.bidCount}`)
//         console.log(bidOld)
//         itemMoney.innerHTML = bidOld;
//     } else {
//
//         const bidItem = document.createElement('div')
//         bidItem.className = 'roulette__item-row'
//         bidItemBlock.appendChild(bidItem)
//
//         const bidItemLeftBlock = document.createElement('div')
//         bidItemLeftBlock.className = 'roulette__item-left'
//         bidItem.appendChild(bidItemLeftBlock)
//
//         const itemMoney = document.createElement('div')
//         itemMoney.className = 'roulette__item-money'
//         itemMoney.innerHTML = `${data.bet.bidCount}`
//         bidItem.appendChild(itemMoney)
//
//         const itemAvatar = document.createElement('div')
//         itemAvatar.className = 'roulette__item-avatar'
//         itemAvatar.innerHTML = `<img src="${data.bet.avatar}" alt="">`
//         bidItemLeftBlock.appendChild(itemAvatar)
//
//         const itemStone = document.createElement('div')
//         itemStone.className = 'roulette__item-stoun'
//         const stone = document.createElementNS("http://www.w3.org/2000/svg", "svg")
//         stone.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.bet.userStone}"></use>`
//         itemStone.appendChild(stone)
//         bidItemLeftBlock.appendChild(itemStone)
//
//         const itemUserName = document.createElement('div')
//         itemUserName.className = 'roulette__item-username'
//         itemUserName.innerHTML = `${data.bet.userName}`
//         bidItemLeftBlock.appendChild(itemUserName)
//     }
// }
const createBidItems = (data) => {
    document.querySelector(`.hearts`).innerHTML = ''
    document.querySelector(`.coin`).innerHTML = ''
    document.querySelector(`.spades`).innerHTML = ''

    let usersId = (Object.keys(data))

    console.log(usersId, 'UseridDDD')
    console.log(data)
    let heartsCounts = 0;
    let coinCounts = 0;
    let spadesCounts = 0;
    let heartsCountsShow = '';
    let coinCountsShow = '';
    let spadesCountsShow = '';
    let usersBids=[]
    usersId.map(user => {
//суммирование в заголовке
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
            document.querySelector('#spanCardHearts').innerHTML = `<span class="signWinnerHearts">:</span> ${heartsCountsShow}`
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
            document.querySelector('#spanCardCoin').innerHTML = `<span class="signWinnerCoin">:</span>  ${coinCountsShow}`

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
            document.querySelector('#spanCardSpades').innerHTML = `<span class="signWinnerSpades">:</span>  ${spadesCountsShow}`
        }

        let objAmount = data[user]['amount']
        let keys = Object.keys(objAmount); //получаем ключи объекта в виде массива
        let avatar = data[user]['avatar']
        let rubin = data[user]['rubin']
        let userName = data[user]['userName']
        console.log(objAmount,'objAmount')
        console.log(keys,'KEYS')

        keys.map(card => {
            user = {
                avatar: avatar,
                bidCard: card,
                bidCount: objAmount[card],
                rubin: rubin,
                userName: userName
            }
            console.log(user,'USER')

            usersBids.push(user)//создание массива всех ставок
            console.log(usersBids,'USERS')

            usersBids.sort((a,b)=>b.bidCount - a.bidCount)//сортировка по ставкам
            console.log(usersBids,'USERS')
        })
    })


    usersBids.map(el=>{
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
                itemMoney.innerHTML = `<span class="signWinner${el.bidCard}"></span>${el.bidCount}`
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
}

// const items = document.querySelectorAll('.roulette__radio-item > label')
const itemsClick = (bidCard) => {
    console.log('itemClick')


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

        let balanceUser = Number(document.querySelector('.header__profile-sum>span').textContent)
        console.log(balanceUser, 'balanceUser')
        // console.log(cells)
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


            document.querySelector('.header__profile-sum>span').innerHTML = `${balanceUser}`

            // items[0].style.pointerEvents = 'none';
            /////////////////////////////////////////////////
        } else {
            //вывод сообщения НЕДОСТАТОЧНО СРЕДСТВ
            let modalMoney = document.querySelector('#modalMoney')
            modalMoney.classList.add("open");
            // document.querySelector('.modal__balance').innerHTML = ` Ваш баланс: ${balanceUser}`
            modalMoney.addEventListener("click", function (e) {
                if (!e.target.closest(".popup__content")) {
                    document.querySelector('.popup.open').classList.remove("open");
                }
            });
///////////////////////////////////////////////////////////////////////////////////
        }
        document.querySelector('.roulette__table-input').value = ''
        document.querySelector('.roulette__current-block').innerHTML = '';
    }
}

items[0].addEventListener('click', () => itemsClick('hearts'))
items[1].addEventListener('click', () => itemsClick('coin'))
items[2].addEventListener('click', () => itemsClick('spades'))
