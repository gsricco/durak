
let winnerCase = 111


let caseMessage = [
    {
        "item": {
            "name": "1K",
            "image": "dollar",
            "selling_price": 1000
        }
    },
    {
        "item": {
            "name": "5K",
            "image": "dollar",
            "selling_price": 5000
        }
    },
    {
        "item": {
            "name": "Медведь(50К)",
            "image": "smile_bear",
            "selling_price": 50000
        }
    },
    {
        "item": {
            "name": "Робот(50K)",
            "image": "smile_robot",
            "selling_price": 50000
        }
    },
    {
        "item": {
            "name": "Лев",
            "image": "smile_lion",
            "selling_price": 700000
        }
    },
    {
        "item": {
            "name": "VAMPIR",
            "image": "smile_vampire",
            "selling_price": 700000
        }
    }
]


const modalCase = document.querySelector('#modal-cases');
const listCase = document.querySelector('.listCase');
console.log(winnerCase)

function generateItemsCase() {

    console.log('generateItemsCase')
    let title;
    let n = 0;

    const roll = () => {
        function randomInteger(min, max) {
            // получить случайное число от (min-0.5) до (max+0.5)
            let rand = min + Math.random() * (max - min + 1);
            return Math.round(rand);
        }

        let swingFinish = `translate3d(${randomInteger(-496, -504) / 10}%, 0, 0)`
        listCase.style.left = '50%'
        listCase.style.transform = swingFinish
        listCase.style.transition = '5s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
    }

    for (let i = 0; i < winnerCase; i++) {

        let item;
        item = `<svg>
                            <use xlink:href="/static/img/icons/sprite.svg#${caseMessage[n]['item']['image']}"></use>
                        </svg>`;
        title = `${i}`;
        n++;

        // console.log(caseMessage.length)
        if (n === caseMessage.length) n = 0;
        // console.log(n)

        const caseItem = document.createElement('div')
        caseItem.classList.add('modal-case-overflow__item')
        modalCase.appendChild(caseItem)

        const caseWrapper = document.createElement('div')
        caseWrapper.className = 'modal-case__wrapper'
        caseItem.appendChild(caseWrapper)

        const caseImg = document.createElement('div')
        caseImg.className = 'modal-case__img'
        caseImg.innerHTML = item
        caseWrapper.appendChild(caseImg)
        const caseTitle = document.createElement('div')
        caseTitle.className = 'modal-case__title'
        caseTitle.innerHTML = title
        caseWrapper.appendChild(caseTitle)
    }
    roll()
}

let btnCase = document.querySelector('.modal-case__open')
btnCase.addEventListener('click', () => {
    modalCase.innerHTML = '';
    generateItemsCase();
})

let btnTimer = document.querySelector('#timerTwo')
btnCase.addEventListener('dblclick', () => {

    modalCase.innerHTML = ''
    listCase.style.left = '0%'
    listCase.style.transform = 'translate3d(-380px, 0, 0)'
    listCase.style.transition = '1s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
    // modalCase.style.left = '0%'
    // modalCase.style.transform = 'translate3d(0, 0, 0)'
    // modalCase.style.transition = '1s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
    returnToStartPosition()
})

const returnToStartPosition = () => {
    listCase.innerHTML = `
    <div id="modal-cases" class="modal-cases__case modal-case modal-case-overflow">
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_bear"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            МЕДВЕДЯ
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_lion"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            ЛЁВА
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_vampire"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            ЗУБОСКАЛ
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_robot"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            РОБОКОП
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_bear"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            МЕДВЕДЯ
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_lion"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            ЛЁВА
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_vampire"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            ЗУБОСКАЛ
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-case-overflow__item">
                                    <div class="modal-case__wrapper">
                                        <div class="modal-case__img">
                                            <svg>
                                                <use xlink:href="/static/img/icons/sprite.svg#smile_robot"></use>
                                            </svg>
                                        </div>
                                        <div class="modal-case__title">
                                            РОБОКОП
                                        </div>
                                    </div>
                                </div>
                        </div>
    `
    listCase.style.left = '0%'
    listCase.style.transform = 'translate3d(-380px, 0, 0)'
    listCase.style.transition = '1s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
    // modalCase.style.left = '0%'
    // modalCase.style.transform = 'translate3d(-380px, 0, 0)'
    // modalCase.style.transition = '1s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
}
