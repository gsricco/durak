

            ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
            //! Прокрутка рулетки
            // 113 - coin
            //111 - red7
            //109 - black6
            //107 - red5
            //105 - black4
            //103 - red3
            //101 - black2

            // window.addEventListener('focus', function() { timerCounter(10); });
            let responseBack; // определенная карта с бэкенда
            let cells;

            let numbersCards = Math.round(100 + Math.random() * (121 - 100 + 1))
            if (responseBack){
                cells = responseBack
            } else {
                cells = (numbersCards % 2 === 0 ) ? numbersCards+1:numbersCards
            }
            console.log(cells)
            // const cells = 113

            const list = document.querySelector('.list');

            function generateItems() {
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

            //генерируем при загрузке страницы первоначальную верстку картинок
            generateItems();

            // анимацию прокрутки
            function startRoll() {
                //докрутка от -49.6% до -50.4%
                function randomInteger(min, max) {
                    // получить случайное число от (min-0.5) до (max+0.5)
                    let rand = min + Math.random() * (max - min + 1);
                    return Math.round(rand);
                }
                let swingFinish = `translate3d(${randomInteger(-496,-504)/10}%, 0, 0)`
                console.log('sss '+ swingFinish)

                list.style.left = '50%'
                list.style.transform = swingFinish
                list.style.transition = '5s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
            }

            // анимация возврата после прокрутки
            const returnToStartPosition = () => {
                list.style.left = '0%'
                list.style.transform = 'translate3d(-380px, 0, 0)'
                list.style.transition = '1s cubic-bezier(0.21, 0.53, 0.29, 0.99)'
            }

            //! Таймер рулетка

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

                // стартовое значение таймера
                let num = back_counter

                // происходит отсчет и его отрисовка
                let intervalTimerRull = setInterval(() => {
                    if (num.toFixed(1) <= 0.1) {
                        clearInterval(intervalTimerRull);
                        // удаляем счетчик после отсчета
                        wrapperItems.classList.remove("roulette__rull-wrapper_blur");
                        timerWrapper.style.display = "none";
                        rull_line.style.display = "block";
                    } else {
                        num -= 0.1;
                        timerNums.innerHTML = num.toFixed(1);
                    }
                }, 100);

                //добавляем стили счетчика для его отображения при новой прокрутке
                blurForTimer()

                //после отсчета вызывается цепочка промисов

                setTimeout(() => {
                    // тут стартует анимация прокрута с задержкой в 20 секунд
                    startRoll()
                    setTimeout(() => {
                        // тут происходит возврат после прокрутки на исходное положение через 8 секунд после начала прокрутки
                        returnToStartPosition()
                    }, 8000);
                }, back_counter*1000)
            }

            //дергаем ф-цию что бы все сработало 1 раз при загрузке, дальше по сет интервалу в 29сек
            // timerCounter()

            //ставим функцию на каждые 29сек
            // setInterval(timerCounter, 29000)


            //! Плавные скроллбары
            if (document.querySelector(".scrollbar-overflow")) {
                let blockArrow = document.querySelectorAll(".scrollbar-overflow");

                blockArrow.forEach(function (item) {
                    item.addEventListener("touchmove", function () {
                        item.classList.add("scrollbar-overflow_active");
                    });

                    item.addEventListener("touchend", function () {
                        setTimeout(function () {
                            item.classList.remove("scrollbar-overflow_active");
                        }, 1000);
                    });
                });
            }
            /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
