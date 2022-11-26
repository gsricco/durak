const media_prefix = JSON.parse(document.getElementById('media_prefix').textContent);
const static_prefix = JSON.parse(document.getElementById('static_prefix').textContent);
const items = document.querySelectorAll('.roulette__radio-item > label')
const bidsBlock = document.querySelectorAll('.roulette__item-body')
const bidsButtons = document.querySelectorAll('.roulette__radio-item')



// let balanceUser - из бэка
// let balanceUser = Number(document.querySelector('.header__profile-sum>span').textContent)
let balanceUser = Number(document.querySelector('#balanceUser').textContent)
// let balanceUser = `{{ detail_user.balance }}`

console.log(balanceUser)


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

// const items = document.querySelectorAll('.roulette__radio-item > label')
const itemsClick = (bidCard) => {
    let bidCount = document.querySelector('.roulette__table-input').value * 1000;
    if (is_auth && bidCount) {
        // console.log(cells)
        if (balanceUser + 1 > Number(bidCount)) {
            chatSocket.send(JSON.stringify({
                'bidCount': bidCount,
                'userName': username,
                'avatar': ava,
                'rubin': 'rubin_blue',
                userStone: 'rubin_blue',
                bidCard: bidCard
            }));
            if (bidCard === 'hearts') {
                items[2].style.pointerEvents = 'none';
            } else if(bidCard ==='spades') {
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

            document.querySelector('.profil-main__content').innerHtml = `
            <div className="popup" id="authorization">
                <div className="popup__body">
                    <div className="popup__content modal modal_popup modal_authorization">
                        <a href="#" className="popup__close close-popup close-popup_close">
                            <svg className="close-popup__icon ">
                                <use xlink:href="img/icons/sprite.svg#close"></use>
                            </svg>
                        </a>
                        <div className="modal-enter">
                            <h3 className="modal__title modal-enter__title">
                                Авторизуйтесь для продолжения
                            </h3>
                            <div className="modal-enter__body">
                                <div className="modal-enter__row">
                                    <div className="modal-enter__item">
                                        <div className="modal-enter__img">
                                            <svg className="yt">
                                                <use xlink:href="img/icons/sprite.svg#youtube"></use>
                                            </svg>
                                        </div>
                                        <a href="##" className="btn btns_yt modal-enter__btn">Войти через Google</a>
                                    </div>
                                    <div className="modal-enter__item">
                                        <div className="modal-enter__img">
                                            <svg className="vk">
                                                <use xlink:href="img/icons/sprite.svg#vk"></use>
                                            </svg>
                                        </div>
                                        <a href="##" className="btn btns_vk modal-enter__btn">Войти через Вконтакте</a>
                                    </div>

                                </div>

                            </div>
                        </div>


                    </div>
                </div>
            </div>
            `


            alert('No money')
        }
        document.querySelector('.roulette__table-input').value = ''
        document.querySelector('.roulette__current-block').innerHTML = '';
    }
}

items[0].addEventListener('click', () => itemsClick('hearts'))
items[1].addEventListener('click', () => itemsClick('coin'))
items[2].addEventListener('click', () => itemsClick('spades'))


