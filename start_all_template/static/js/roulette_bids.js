const media_prefix = JSON.parse(document.getElementById('media_prefix').textContent);
const static_prefix = JSON.parse(document.getElementById('static_prefix').textContent);

let balanceUser = 20000;

const createBidItemRow = (data) => {
    console.log(media_prefix)
    console.log(static_prefix)
    console.log(data)

    //balanceUser - текущий баланс user


    const bidItemBlock = document.querySelector(`.${data.bidCard}`)

            const bidItem = document.createElement('div')
            bidItem.className = 'roulette__item-row'
            bidItemBlock.appendChild(bidItem)

            const bidItemLeftBlock = document.createElement('div')
            bidItemLeftBlock.className = 'roulette__item-left'
            bidItem.appendChild(bidItemLeftBlock)

            const itemMoney = document.createElement('div')
            itemMoney.className = 'roulette__item-money'
            itemMoney.innerHTML = `${data.bidCount}`
            bidItem.appendChild(itemMoney)

            const itemAvatar = document.createElement('div')
            itemAvatar.className = 'roulette__item-avatar'
            itemAvatar.innerHTML = `<img src="${media_prefix}${data.avatar}" alt="">`
            bidItemLeftBlock.appendChild(itemAvatar)

            const itemStone = document.createElement('div')
            itemStone.className = 'roulette__item-stoun'
            const stone = document.createElementNS("http://www.w3.org/2000/svg", "svg")
            stone.innerHTML = `<use xlink:href="${static_prefix}/img/icons/sprite.svg#${data.userStone}"></use>`
            itemStone.appendChild(stone)
            bidItemLeftBlock.appendChild(itemStone)

            const itemUserName = document.createElement('div')
            itemUserName.className = 'roulette__item-username'
            itemUserName.innerHTML = `${data.userName}`
            bidItemLeftBlock.appendChild(itemUserName)
        }

const items = document.querySelectorAll('.roulette__radio-item > label')

const itemsClick = (bidCard) => {
    let bidCount = document.querySelector('.roulette__table-input').value * 1000;
    if (is_auth && bidCount) {
        // console.log(cells)
        if (balanceUser > Number(bidCount)) {
            chatSocket.send(JSON.stringify({
                'bidCount': bidCount,
                'userName': username,
                'avatar': ava,
                'rubin': 'rubin_blue',
                userStone: 'rubin_blue',
                bidCard: bidCard
            }));
            ///////////////////////////////////////////////
            //логика БЭК отнимания ставки от баланса/////////
            /////////////////////////////////////////////////
        } else {
            //вывод сообщения НЕДОСТАТОЧНО СРЕДСТВ
            alert('No money')
        }
        document.querySelector('.roulette__table-input').value = ''
        document.querySelector('.roulette__current-block').innerHTML = '';
    }
}

items[0].addEventListener('click', () => itemsClick('hearts'))
items[1].addEventListener('click', () => itemsClick('coin'))
items[2].addEventListener('click', () => itemsClick('spades'))


