// const media_prefix = JSON.parse(document.getElementById('media_prefix').textContent);
// const static_prefix = JSON.parse(document.getElementById('static_prefix').textContent);
const items = document.querySelectorAll('.roulette__radio-item > label')
const bidsBlock = document.querySelectorAll('.roulette__item-body')
const bidsButtons = document.querySelectorAll('.roulette__radio-item')


// let balanceUser - из бэка
// let balanceUser = Number(document.querySelector('#balanceUser').textContent)
// let balanceUser = document.querySelector('.header__profile-sum>span')
// let balanceUser = `{{ detail_user.balance }}`


// let balanceUser = document.querySelector('.header__profile-sum>span').innerText;


const createBidItemRow = (data) => {
    //balanceUser - текущий баланс user
    // console.log(data.bet.bidCard)

    const bidItemBlock = document.querySelector(`.${data.bet.bidCard}`)

    if (bidItemBlock.innerHTML != ``) {
        let itemMoney = document.querySelector(`div.${data.bet.bidCard} div.roulette__item-money`)
        let bidOld = Number(itemMoney.textContent) + Number(`${data.bet.bidCount}`)
        console.log(bidOld)
        itemMoney.innerHTML = bidOld;
    } else {

        const bidItem = document.createElement('div')
        bidItem.className = 'roulette__item-row'
        bidItemBlock.appendChild(bidItem)

        const bidItemLeftBlock = document.createElement('div')
        bidItemLeftBlock.className = 'roulette__item-left'
        bidItem.appendChild(bidItemLeftBlock)

        const itemMoney = document.createElement('div')
        itemMoney.className = 'roulette__item-money'
        itemMoney.innerHTML = `${data.bet.bidCount}`
        bidItem.appendChild(itemMoney)

        const itemAvatar = document.createElement('div')
        itemAvatar.className = 'roulette__item-avatar'
        itemAvatar.innerHTML = `<img src="${data.bet.avatar}" alt="">`
        bidItemLeftBlock.appendChild(itemAvatar)

        const itemStone = document.createElement('div')
        itemStone.className = 'roulette__item-stoun'
        const stone = document.createElementNS("http://www.w3.org/2000/svg", "svg")
        stone.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.bet.userStone}"></use>`
        itemStone.appendChild(stone)
        bidItemLeftBlock.appendChild(itemStone)

        const itemUserName = document.createElement('div')
        itemUserName.className = 'roulette__item-username'
        itemUserName.innerHTML = `${data.bet.userName}`
        bidItemLeftBlock.appendChild(itemUserName)
    }
}

// const items = document.querySelectorAll('.roulette__radio-item > label')
const itemsClick = (bidCard) => {
    console.log('itemClick')

    // let balanceUser = document.querySelector('.header__profile-sum>span').innerText;

    // console.log(balanceUser, "ETO BALANCE USERA")
    let bidCount = document.querySelector('.roulette__table-input').value * 1000;

    if (!is_auth) {

        ///////////вывод модалки НЕ_АВТОРИЗОВАН///////////////////
        let modalAuth = document.querySelector('#authorization')
        modalAuth.classList.add("open");
        // document.querySelector('.modal__balance').innerHTML = ` Ваш баланс: ${balanceUser}`
        modalAuth.addEventListener("click", function (e) {
            if (!e.target.closest(".popup__content")) {
                document.querySelector('.popup.open').classList.remove("open");
            }
        });
///////////////////////////////////////////////////////////////////////////////////
    } else if (bidCount) {

        let balanceUser = Number(document.querySelector('.header__profile-sum>span').textContent)

        // console.log(cells)
        if (balanceUser + 1 >= Number(bidCount)) {


            chatSocket.send(JSON.stringify({
                'bet': {
                    'bidCount': bidCount,
                    'userName': username,
                    'avatar': ava,
                    'rubin': rubin,
                    userStone: rubin,
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
            document.querySelector('.header__profile-sum>span').innerHTML = `${balanceUser}`
            // items[0].style.pointerEvents = 'none';
            /////////////////////////////////////////////////
        } else {
            //вывод сообщения НЕДОСТАТОЧНО СРЕДСТВ
            let modalMoney = document.querySelector('#modalMoney')
            modalMoney.classList.add("open");
            document.querySelector('.modal__balance').innerHTML = ` Ваш баланс: ${balanceUser}`
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
