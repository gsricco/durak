let title;
let n = 0;


function generateItemsCase(caseMessage, winner) {
    listCase.className = 'listCase'


    const roll = () => {
        function randomInteger(min, max) {
            // получить случайное число от (min-0.5) до (max+0.5)
            let rand = min + Math.random() * (max - min + 1);
            return Math.round(rand);
        }

        //докрутка рулетки
        let swingFinish = `translate3d(${randomInteger(-496, -504) / 10}%, 0, 0)`
        listCase.style.left = '50%'
        listCase.style.transform = swingFinish
        listCase.style.transition = '5s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
    }

    function oneRollItem() {
        let item;
        item = `<svg>
                <use xlink:href="/static/img/icons/sprite.svg#${caseMessage[n]['item']['image']}"></use>
                </svg>`;
        title = `${caseMessage[n]['item']['name']}`
        n++;
        if (n === caseMessage.length) n = 0;
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

    for (let i = 0; i < 24; i++) {
        oneRollItem()
    }
    caseMessage.forEach((e) => {
        if (e.item.name === winner) {
            item = `<svg>
                <use xlink:href="/static/img/icons/sprite.svg#${e['item']['image']}"></use>
                </svg>`;
            title = `${e['item']['name']}`;

            n++;
            if (n === caseMessage.length) n = 0;
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
    })

    for (let i = 0; i < 24; i++) {
        oneRollItem()
    }

    roll()
    setTimeout(returnToStartPosition, 6000)
}


const returnToStartPosition = () => {
    listCase.style.left = '0%'
    listCase.style.transform = 'translate3d(-363px, 0, 0)'
    listCase.style.transition = '2s cubic-bezier(0.21,0.53, 0.29, 0.99)'

}
