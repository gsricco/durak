//'use strict';
window.addEventListener("DOMContentLoaded", () => {
    const BODY = document.querySelector("body");
    const MAIN = document.querySelector("main");
    const FOOTER = document.querySelector("footer");

    // !Бургер
    if (document.querySelector(".burger-menu")) {
        (function () {
            // let burger = document.querySelector('.header__burger');
            let header = document.querySelector(".header");
            let burger = document.querySelector(".burger-menu");
            let burgerWrapper = document.querySelector(".header__wrapper");
            //let body = document.querySelector('body');
            burger.addEventListener("click", () => {
                // burger.classList.toggle('header__burger_active');
                header.classList.toggle("header_active");
                BODY.classList.toggle("overflow-h");
                burger.classList.toggle("burger-menu_active");
                burgerWrapper.classList.toggle("header__wrapper_active");
            });
        })();
    }

    if (document.querySelector(".header")) {
        window.addEventListener("resize", function () {
            if (document.documentElement.clientWidth < 540) {
                document
                    .querySelector(".header__profile")
                    .append(document.querySelector(".header__profile-progressbar"));
                document
                    .querySelector(".header__profile")
                    .append(document.querySelector(".header__btns"));
            }

            if (document.documentElement.clientWidth > 540) {
                document
                    .querySelector(".header__profile-info")
                    .append(document.querySelector(".header__profile-progressbar"));
                document
                    .querySelector(".header__profile-info")
                    .append(document.querySelector(".header__btns"));
            }

            if (document.documentElement.clientWidth < 991) {
                document.querySelector(".header__wrapper").classList.add("container");
            }

            if (document.documentElement.clientWidth > 991) {
                document
                    .querySelector(".header__wrapper")
                    .classList.remove("container");
            }
        });

        if (document.documentElement.clientWidth < 540) {
            document
                .querySelector(".header__profile")
                .append(document.querySelector(".header__profile-progressbar"));
            document
                .querySelector(".header__profile")
                .append(document.querySelector(".header__btns"));
        }

        if (document.documentElement.clientWidth > 540) {
            document
                .querySelector(".header__profile-info")
                .append(document.querySelector(".header__profile-progressbar"));
            document
                .querySelector(".header__profile-info")
                .append(document.querySelector(".header__btns"));
        }

        if (document.documentElement.clientWidth < 991) {
            document.querySelector(".header__wrapper").classList.add("container");
        }

        if (document.documentElement.clientWidth > 991) {
            document.querySelector(".header__wrapper").classList.remove("container");
        }
    }

    if (document.querySelector(".profil")) {
        window.addEventListener("resize", function () {
            if (document.documentElement.clientWidth < 541) {
                document
                    .querySelector(".profil__name-text")
                    .prepend(document.querySelector(".profil__progressbar-lvl-img"));
                document
                    .querySelector(".profil__name-text")
                    .append(document.querySelector(".profil__progressbar-lvl-num"));
                document
                    .querySelector(".profil__progressbar-row")
                    .append(document.querySelector(".profil__progressbar-lvl-progress"));
                document
                    .querySelector(".profil__row")
                    .append(document.querySelector(".profil__btns"));
            }

            if (document.documentElement.clientWidth > 541) {
                document
                    .querySelector(".profil__progressbar-lvl")
                    .append(document.querySelector(".profil__progressbar-lvl-img"));
                document
                    .querySelector(".profil__progressbar-lvl")
                    .append(document.querySelector(".profil__progressbar-lvl-num"));
                document
                    .querySelector(".profil__progressbar-lvl")
                    .append(document.querySelector(".profil__progressbar-lvl-progress"));
                document
                    .querySelector(".profil__info")
                    .append(document.querySelector(".profil__btns"));
            }
        });

        if (document.documentElement.clientWidth < 541) {
            document
                .querySelector(".profil__name-text")
                .prepend(document.querySelector(".profil__progressbar-lvl-img"));
            document
                .querySelector(".profil__name-text")
                .append(document.querySelector(".profil__progressbar-lvl-num"));
            document
                .querySelector(".profil__progressbar-row")
                .append(document.querySelector(".profil__progressbar-lvl-progress"));
            document
                .querySelector(".profil__row")
                .append(document.querySelector(".profil__btns"));
        }

        if (document.documentElement.clientWidth > 541) {
            document
                .querySelector(".profil__progressbar-lvl")
                .append(document.querySelector(".profil__progressbar-lvl-img"));
            document
                .querySelector(".profil__progressbar-lvl")
                .append(document.querySelector(".profil__progressbar-lvl-num"));
            document
                .querySelector(".profil__progressbar-lvl")
                .append(document.querySelector(".profil__progressbar-lvl-progress"));
            document
                .querySelector(".profil__info")
                .append(document.querySelector(".profil__btns"));
        }
    }

    if (document.querySelector(".profil__slider")) {
        const swiperTwo = new Swiper(".profil__slider", {
            // Optional parameters
            direction: "horizontal",
            slidesPerView: 1,
            spaceBetween: 16,
            loop: false,

            navigation: {
                // prevEl: '.p',
                // nextEl: '.profil__slider-arrow_next',
                nextEl: ".profil__slider-arrow_next",
                prevEl: ".profil__slider-arrow_back",
            },

            breakpoints: {
                767: {
                    direction: "vertical",
                    slidesPerView: 2,
                    spaceBetween: 25,
                    navigation: {
                        nextEl: ".profil__slider-arrow_back",
                        prevEl: ".profil__slider-arrow_next",
                    },
                },
            },
        });
    }

    if (document.querySelector(".support__chat")) {
        function clickChat() {
            let block = document.querySelector(".support__overflow");
            block.style.opacity = "0";

            setTimeout(function () {
                block.style.display = "none";
            }, 1000);
        }

        setTimeout(clickChat, 590);
    }

    //!Modal sliders
    if (document.querySelector(".amount-selection__checkbox")) {
        let SwiperLeft = document.querySelector(".amount-selection__left");
        let SwiperRight = document.querySelector(".amount-selection__right");

        const slider = document.querySelector(".amount-selection__checkbox");
        const sliderWrapper = document.querySelector(".amount-selection__wrapper");
        const slides = sliderWrapper.querySelectorAll(".swiper-slide");

        //function swiperF() {

        if (document.documentElement.clientWidth > 575 && slides.length > 7) {
            let amountSelectionCheckbox = new Swiper(".amount-selection__checkbox", {
                slidesPerView: 3,
                allowTouchMove: false,
                grid: {
                    rows: 2,
                },
                navigation: {
                    nextEl: ".amount-selection__left",
                    prevEl: ".amount-selection__right",
                },
                breakpoints: {
                    767: {
                        slidesPerView: 4,
                    },
                },
            });
        } else {
            slider.classList.remove("swiper");

            sliderWrapper.classList.remove("swiper-wrapper");
            sliderWrapper.classList.add("swiper-wrapper-reset");

            slides.forEach(function (item) {
                item.classList.remove("swiper-slide");
            });

            SwiperLeft.remove();
            SwiperRight.remove();
        }
        //}

        // window.addEventListener('resize', swiperF());
        // swiperF();
    }

    if (document.querySelector("#selectAmountInput .select-amount__slider")) {
        let SwiperLeft = document.querySelector(".select-amount__up");
        let SwiperRight = document.querySelector(".select-amount__down");

        const slider = document.querySelector(
            "#selectAmountInput .select-amount__slider",
        );
        const sliderWrapper = document.querySelector(
            "#selectAmountInput .select-amount__wrapper",
        );
        const slides = sliderWrapper.querySelectorAll(
            "#selectAmountInput .swiper-slide",
        );

        if (document.documentElement.clientWidth > 575 && slides.length > 2) {
            let selectAmountSlider = new Swiper(
                "#selectAmountInput .select-amount__slider",
                {
                    slidesPerView: 2,
                    watchSlidesProgress: true,
                    allowTouchMove: false,
                    direction: "vertical",
                    navigation: {
                        nextEl: ".select-amount__down",
                        prevEl: ".select-amount__up",
                    },
                },
            );
        } else {
            slider.classList.remove("swiper");

            sliderWrapper.classList.remove("swiper-wrapper");
            sliderWrapper.classList.add("swiper-wrapper-reset");

            slides.forEach(function (item) {
                item.classList.remove("swiper-slide");
                item.classList.add("swiper-slide-reset");
            });

            SwiperLeft.remove();
            SwiperRight.remove();
        }
    }

    if (document.querySelector("#selectAmount .select-amount__slider")) {
        let SwiperLeft = document.querySelector(".select-amount__up");
        let SwiperRight = document.querySelector(".select-amount__down");

        const slider = document.querySelector(
            "#selectAmount .select-amount__slider",
        );
        const sliderWrapper = document.querySelector(
            "#selectAmount .select-amount__wrapper",
        );
        const slides = sliderWrapper.querySelectorAll(
            "#selectAmount .swiper-slide",
        );

        if (document.documentElement.clientWidth > 575 && slides.length > 2) {
            let selectAmountSlider = new Swiper(
                "#selectAmount .select-amount__slider",
                {
                    slidesPerView: 2,
                    watchSlidesProgress: true,
                    allowTouchMove: false,
                    direction: "vertical",
                    navigation: {
                        nextEl: ".select-amount__down",
                        prevEl: ".select-amount__up",
                    },
                },
            );
        } else {
            slider.classList.remove("swiper");

            sliderWrapper.classList.remove("swiper-wrapper");
            sliderWrapper.classList.add("swiper-wrapper-reset");

            slides.forEach(function (item) {
                item.classList.remove("swiper-slide");
                item.classList.add("swiper-slide-reset");
            });

            SwiperLeft.remove();
            SwiperRight.remove();
        }
    }

    // !Support logic
    if (document.querySelector(".support")) {
        function heightWindowUser() {
            if (document.documentElement.clientWidth < 540) {
                let windowChat = document.querySelector(".support");
                let windowHeigth = window.innerHeight;
                let chatBlock = document.querySelector(".support__chat");
                chatBlock.style.height = windowHeigth - windowChat.offsetTop + "px";
            } else if (document.documentElement.clientWidth > 540) {
                let chatBlock = document.querySelector(".support__chat");
                chatBlock.style.height = '645px'
            }
        }

        window.addEventListener("resize", heightWindowUser);
        heightWindowUser();
    }

    //! Футер на странице честность
    if (document.querySelector(".honesty")) {
        document.querySelector(".footer").classList.add("footer_honesty");
    }

    //! Прелоадер
    if (document.querySelector(".preloader")) {
        window.onload = function () {
            setTimeout(() => {
                document.body.classList.add("loaded_hiding");
                window.setTimeout(function () {
                    document.body.classList.add("loaded");
                    document.body.classList.remove("loaded_hiding");
                }, 500);
            }, 500);
        };
    }

    //! Активные аккардионы
    if (document.querySelector(".roulette__accardion")) {
        window.addEventListener("resize", activeAccardin);

        function activeAccardin() {
            let accardionArr = document.querySelectorAll(".roulette__accardion");

            accardionArr.forEach(function (item) {
                let panel = item.nextElementSibling;

                if (document.documentElement.clientWidth > 767) {
                    item.classList.add("accordion_active");
                    panel.style.maxHeight = panel.scrollHeight + "px";
                }
            });
        }

        activeAccardin();


        const btnBids = document.querySelectorAll(".roulette__accardion")
        const rouIt = document.querySelectorAll(".roulette__item")
        btnBids.forEach((el, index) => {
            el.addEventListener('click', () => {
                rouIt[index].style.display = rouIt[index].style.display === 'block' ? 'none' : 'block'
            })
        })

    }

    // //! Таймер рулетка
    // if (document.querySelector(".roulette")) {
    //     let timerWrapper = document.querySelector(".roulette__rull-timer-wrapper");
    //     let timerNums = document.querySelector(".roulette__rull-timer");
    //     let wrapperItems = document.querySelector(".roulette__rull-wrapper");
    //     let rull_line = document.querySelector(".roulette__rull-line");
    //     let num = 12.5;
    //
    //     let intervalTimerRull = setInterval(function () {
    //         if (num.toFixed(1) <= 0.1) {
    //             clearInterval(intervalTimerRull);
    //             wrapperItems.classList.remove("roulette__rull-wrapper_blur");
    //             timerWrapper.style.display = "none";
    //             rull_line.style.display = "block";
    //         } else {
    //             num -= 0.1;
    //             timerNums.innerHTML = num.toFixed(1);
    //         }
    //     }, 100);
    // }
    //
    // //! Плавные скроллбары
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

    //!Таймер
    let target_date = new Date().getTime() + /*(1000 * 60 * 5)*/ 1000 * 30; // установить дату обратного отсчета
    let days, hours, minutes, seconds; // переменные для единиц времени
    let countdown = document.getElementById("timer"); // получить элемент тега

    // getCountdown();

    // setInterval(function () { getCountdown(); }, 1000);

    // function getCountdown() {
    // 	let btn = document.getElementById('modalManualBtn');
    // 	let current_date = new Date().getTime();
    // 	let seconds_left = (target_date - current_date) / 1000;
    // 	days = pad(parseInt(seconds_left / 86400));
    // 	seconds_left = seconds_left % 86400;

    // 	hours = pad(parseInt(seconds_left / 3600));
    // 	seconds_left = seconds_left % 3600;

    // 	minutes = pad(parseInt(seconds_left / 60));
    // 	seconds = pad(parseInt(seconds_left % 60));

    // 	let timeSum = days + hours + minutes + seconds;
    // 	if (timeSum > 0) {
    // 		// строка обратного отсчета  + значение тега
    // 		countdown.innerHTML = /*+ days + hours + */"<span>" + minutes + "</span>:<span>" + seconds + "</span>";
    // 		btn.classList.add('btn_white');
    // 	}
    // 	else if (timeSum < 1) {
    // 		countdown.innerHTML = "Начать";
    // 		btn.classList.remove('btn_white');
    // 	}

    // }

    // function pad(n) {
    // 	// return (n < 10 ? '0' : '') + n;

    // }
    //! Таймер
    if (document.querySelector(".timer")) {
        function timerSecond(timerSpan, functionTimer) {
            let timerBlock = document.querySelector(timerSpan);
            let valueTimer = timerBlock.textContent.split(":");
            [minuteTime, secTime] = valueTimer;

            let timer = setInterval(function () {
                if (secTime < 60) {
                    secTime -= 1;
                }

                if (secTime < 0) {
                    minuteTime -= 1;
                    secTime = 59;
                }

                if (minuteTime < 1 && secTime < 1) {
                    clearInterval(timer);
                    setTimeout(functionTimer, 0);
                }

                if (secTime >= 10) {
                    timerBlock.innerHTML = `${minuteTime}:${secTime}`;
                }

                if (secTime < 10 && secTime >= 0) {
                    timerBlock.innerHTML = `${minuteTime}:0${secTime}`;
                }
            }, 1000);
        }

        if (document.querySelector(".instruction")) {
            let repeateOne = 0;
            document
                .querySelector(".instruction")
                .addEventListener("click", function () {
                    if (repeateOne < 1) {
                        timerSecond("#timerOne", function () {
                            let btnTimerInstructin =
                                document.querySelector(".modal-manual__btn");
                            btnTimerInstructin.classList.remove("btn_white");
                            btnTimerInstructin.innerHTML = "Начать";
                            btnTimerInstructin.addEventListener("click", function (event) {
                                if (event.target.textContent == "Начать") {
                                    event.target.innerHTML = "<span>Ожидайте..</span>";
                                    event.target.classList.add("btn_white");
                                }
                            });
                        });
                        repeateOne++;
                    }
                });
        }

        if (document.querySelector('a[href="#cases"]')) {
            let repeateTwo = 0;
            document
                .querySelector('a[href="#cases"]')
                .addEventListener("click", function () {
                    if (repeateTwo < 1) {
                        timerSecond("#timerTwo", function () {
                            let btnTimerCase = document.querySelector(".modal-case__btn");
                            btnTimerCase.classList.remove("btn_white");
                            btnTimerCase.style.background = "#c4364e";
                        });
                        repeateTwo++;
                    }
                });
        }
    }

    //! Формула перевода рублей в валюту и обратно
    if (document.querySelector(".amount-selection__form")) {
        var inputForm = document.querySelector(".amount-selection__input");
        var sumCurrent = document.querySelector(".num-game-currency__span-curent");
        var btnForm = document.querySelector(".amount-selection__btn");

        inputForm.addEventListener("input", sumScore);
        sumCurrent.addEventListener("input", sumValute);

        function sumScore() {
            let inputValueDinamic = inputForm.value.split(/[^0-9]/g);
            if (inputValueDinamic.length > 1) {
                inputForm.value = "";
            } else {
                if (inputForm.value < 69) {
                    sumCurrent.value = `${inputForm.value * 0}`;
                    btnForm.classList.add("btn-disable-sum");
                }

                if (inputForm.value >= 69) {
                    btnForm.classList.remove("btn-disable-sum");
                }

                if (inputForm.value >= 69 && inputForm.value <= 109) {
                    sumCurrent.value = `${parseFloat(
                        (inputForm.value * 725) / 1000,
                    ).toFixed(0)}`;
                }

                if (inputForm.value >= 110 && inputForm.value <= 179) {
                    sumCurrent.value = `${parseFloat(
                        (inputForm.value * 910) / 1000,
                    ).toFixed(0)}`;
                }

                if (inputForm.value >= 180 && inputForm.value <= 239) {
                    sumCurrent.value = `${parseFloat(
                        (inputForm.value * 1389) / 1000,
                    ).toFixed(0)}`;
                }

                if (inputForm.value >= 240 && inputForm.value <= 459) {
                    sumCurrent.value = `${parseFloat(
                        (inputForm.value * 2084) / 1000,
                    ).toFixed(0)}`;
                }

                if (inputForm.value >= 460 && inputForm.value <= 1274) {
                    sumCurrent.value = `${parseFloat(
                        (inputForm.value * 2174) / 1000,
                    ).toFixed(0)}`;
                }

                if (inputForm.value >= 1275) {
                    sumCurrent.value = `${parseFloat(
                        (inputForm.value * 2353) / 1000,
                    ).toFixed(0)}`;
                }
            }
        }

        function sumValute() {
            let inputValueDinamic = sumCurrent.value.split(/[^0-9]/g);
            if (inputValueDinamic.length > 1) {
                sumCurrent.value = "";
            } else {
                let currentCredint = (sumCurrent.value / 50000) * 1000;

                if (currentCredint >= 1) {
                    btnForm.classList.remove("btn-disable-sum");
                } else {
                    btnForm.classList.add("btn-disable-sum");
                }

                if (currentCredint < 1) {
                    inputForm.value = "";
                }
                if (currentCredint <= 2 && currentCredint >= 1) {
                    inputForm.value = `${(currentCredint * 69).toFixed(1)}`;
                }

                if (currentCredint <= 5 && currentCredint >= 2) {
                    inputForm.value = `${(currentCredint * 55).toFixed(1)}`;
                }

                if (currentCredint <= 10 && currentCredint >= 5) {
                    inputForm.value = `${(currentCredint * 36).toFixed(1)}`;
                }

                if (currentCredint <= 20 && currentCredint >= 10) {
                    inputForm.value = `${(currentCredint * 27.5).toFixed(1)}`;
                }

                if (currentCredint <= 40 && currentCredint >= 20) {
                    inputForm.value = `${(currentCredint * 23).toFixed(1)}`;
                }

                if (currentCredint <= 60 && currentCredint >= 40) {
                    inputForm.value = `${(currentCredint * 21.25).toFixed(1)}`;
                }

                if (currentCredint >= 60) {
                    inputForm.value = `${(currentCredint * 20).toFixed(1)}`;
                }

                if (sumCurrent.value == "" && sumCurrent.value == 0) {
                    inputForm.value = "";
                }
            }
        }
    }

    // ===============================================================
    // Расчёт по кол-ву руб:
    // от 69 до 109р кол-во кредов = (введенное число руб.)*725
    // от 110 до 179р кол-во кредов = (введенное число руб.)*910
    // от 180 до 239р кол-во кредов = (введенное число руб.)*1389
    // от 240 до 459р кол-во кредов = (введенное число руб.)*2084
    // от 460 до 1274р кол-во кредов = (введенное число руб.)*2174
    // от 1275 кол-во кредов = (введенное число руб.)*2353

    //!Настройка профиля

    let avatarSocial;
    let avatarka;

    if (document.querySelector(".profile-settings")) {
        const avaBtnHide = document.getElementById("avaBtnHide");
        const avaBtnShow = document.getElementById("avaBtnShow");
        const profileImage = document.getElementById("profileImage");


        function getImage() {

            fetch(' http://127.0.0.1:8000/api/v1/avatar_default/')
                .then(response => response.json())
                .then((data) => {
                    let randomNum = Math.floor(Math.random() * (data.length));
                    avatarka = data[randomNum]['avatar_default']
                    profileImage.setAttribute("src", `${avatarka}`);
                });
        }

        if (avaBtnHide) {
            avaBtnHide.addEventListener("click", () => {
                getImage();
                avaBtnHide.style.display = "none";
                avaBtnShow.style.display = "block";
            });
        }


        avaBtnShow.addEventListener("click", () => {
            fetch('http://127.0.0.1:8000/api/v1/avatar/')
                .then(response => response.json())
                .then((data) => {
                    let userNow = data.filter(el => el['username'] === username)
                    avatarSocial = userNow[0]['avatar']
                    profileImage.setAttribute("src", `${avatarSocial}`);
                    // profileImage.setAttribute("src", `/media/img/avatar/user/image_1`);
                });
            avaBtnShow.style.display = "none";
            avaBtnHide.style.display = "block";
        });
    }
    let btnSaveAvatar = document.querySelector('#btnSaveImgAvatar');
    if (btnSaveAvatar) {
        btnSaveAvatar.addEventListener('click', () => {

            fetch('http://127.0.0.1:8000/api/v1/message/',
                {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': 'f2IQIW2uLUfxPuzHdfwKJyQKBc66wMGCSTdeQkTGc3AUUepZLMX11zloNK0mhDCv'
                    },
                    body: JSON.stringify({avatar: 'Фото', name: 'Имя'})
                })
                .then(resp => resp)
                .then(data => console.log(data))
        })
    }


    //!звук
    if (document.querySelector(".sound")) {
        let sound = document.querySelector(".sound");
        let soundImg = document.querySelector(".sound svg use");

        sound.addEventListener("click", () => {
            if (sound.getAttribute("data-value") == "soundOn") {
                soundImg.setAttribute("xlink:href", `img/icons/sprite.svg#sound_on`);
                sound.setAttribute("data-value", "soundOff");
            } else if (sound.getAttribute("data-value") == "soundOff") {
                soundImg.setAttribute("xlink:href", `img/icons/sprite.svg#sound_off`);
                sound.setAttribute("data-value", "soundOn");
            }
        });
    }


    //! Копирование никнейма (текста)
    if (document.querySelector(".choice-object__btn")) {
        function copyToClipboard() {
            const str = document.querySelector(".choice-object__input_min").value;
            const el = document.createElement("textarea");
            el.value = str;
            el.setAttribute("readonly", "");
            el.style.position = "absolute";
            el.style.left = "-9999px";
            document.body.appendChild(el);
            el.select();
            document.execCommand("copy");
            document.body.removeChild(el);
        }

        document
            .querySelector(".choice-object__btn")
            .addEventListener("click", copyToClipboard);
    }

    //!Чат
    if (document.querySelector(".online-chat__icon-doc")) {
        let docChat = document.querySelector(".online-chat__icon-doc");
        let rules = document.querySelector(".rules");
        docChat.addEventListener("click", () => {
            setTimeout(() => rules.classList.toggle("rules_active"), 100);
        });
    }

    // if (document.querySelector('.support__chat-message-text')) {
    // 	let lineString = document.querySelector('.support__chat-message-text span');
    // 	let lineBlock = document.querySelector('.support__chat-message-text');
    // 	let tagText = lineString.clientWidth;
    // 	console.log(tagText);
    // 	console.log(lineString.offsetWidth + 'px');
    // 	lineBlock.style.width = lineString.offsetWidth + 'px';
    // }

    //!футер
    if (document.querySelector("main") && document.querySelector("footer")) {
        function footerHeigth() {
            let footerHeight = document.querySelector(".footer").offsetHeight;
            let headerHeight = document.querySelector(".header").offsetHeight;
            let mainHeight = document.querySelector("main").offsetHeight;
            let winHeight = window.innerHeight;
            let containerHeight =
                document.querySelector("main .container").offsetHeight;


            if (document.documentElement.clientWidth > 991) {
                if (containerHeight + headerHeight + footerHeight + 30 > winHeight) {
                    FOOTER.classList.add("footer_dofix");
                    FOOTER.classList.remove("footer_fix");
                    // let valuemargin = (-1 * (containerHeight + headerHeight - winHeight));
                    let valuemargin = -1 * (containerHeight + headerHeight - winHeight);

                    if (valuemargin > 0) {
                        FOOTER.style.marginTop = valuemargin + "px";
                    } else {
                        FOOTER.style.marginTop = 20 + "px";
                    }
                } else {
                    FOOTER.classList.add("footer_fix");
                    FOOTER.classList.remove("footer_dofix");
                }
            } else {
                if (containerHeight + headerHeight + footerHeight + 50 > winHeight) {
                    FOOTER.classList.add("footer_dofix");
                    FOOTER.classList.remove("footer_fix");
                    // let valuemargin = (-1 * (containerHeight + headerHeight - winHeight));
                    let valuemargin = -1 * (containerHeight + headerHeight - winHeight);

                    if (valuemargin > 0) {
                        FOOTER.style.marginTop = valuemargin + "px";
                    } else {
                        FOOTER.style.marginTop = 20 + "px";
                    }
                } else {
                    FOOTER.classList.add("footer_fix");
                    FOOTER.classList.remove("footer_dofix");
                }
            }

            // let footerHeight = document.querySelector('footer').offsetHeight;
            // console.log(mainHeight + '||' + headerHeight + '||' + winHeight)
            // console.log(footerHeight)
            // console.log(winHeight - (mainHeight + footerHeight))

            //if ((mainHeight < winHeight) && (mainHeight + 5 > winHeight)) {
            // if ((mainHeight < winHeight) && (mainHeight + footerHeight > winHeight)) {
            // 	FOOTER.classList.add('footer_dofix');
            // 	FOOTER.classList.remove('footer_fix');
            // 	// console.log('d');
            // }
            // else if (mainHeight + footerHeight <= winHeight) {
            // 	FOOTER.classList.add('footer_fix');
            // 	FOOTER.classList.remove('footer_dofix');
            // 	// console.log('f');
            // }
            // else {
            // 	FOOTER.classList.remove('footer_fix');
            // 	FOOTER.classList.remove('footer_dofix');
            // }
        }

        footerHeigth();
        window.addEventListener("resize", footerHeigth);
    }

    //! При нажатии на чат
    if (document.querySelector(".online-chat") && window.innerWidth <= 991) {
        let chatHeight = null;
        let chatBlockBody = document.querySelector(".online-chat__body");

        function heightOnlineChat() {
            setTimeout(function () {
                if (
                    !document
                        .querySelector(".online-chat")
                        .classList.contains("online-chat-focus")
                ) {
                    let valueMax = document.querySelector(".header__logo").offsetHeight;
                    chatHeight = window.innerHeight - valueMax;

                    if (
                        (document.documentElement.clientWidth <= 991) &
                        (document.documentElement.clientWidth >= 541)
                    ) {
                        document.querySelector(".online-chat").style.maxHeight = `${
                            chatHeight - 40
                        }px`;
                        chatBlockBody.scrollTop = chatBlockBody.scrollHeight;
                    } else if (document.documentElement.clientWidth < 541) {
                        document.querySelector(
                            ".online-chat",
                        ).style.maxHeight = `${chatHeight}px`;
                        chatBlockBody.scrollTop = chatBlockBody.scrollHeight;
                    }
                }
            }, 100);
        }

        function eventFocusChat() {
            let valueMax = document.querySelector(".header__logo").offsetHeight;

            document
                .querySelector(".online-chat__input")
                .addEventListener("focus", function () {
                    document
                        .querySelector(".online-chat")
                        .classList.add("online-chat-focus");
                    if (
                        (document.documentElement.clientWidth <= 991) &
                        (document.documentElement.clientWidth >= 541)
                    ) {
                        document.querySelector(".online-chat").style.maxHeight = `unset`;
                        document.querySelector(".online-chat").style.top = 77 + "px";
                    } else if (document.documentElement.clientWidth < 541) {
                        document.querySelector(".online-chat").style.maxHeight = `unset`;
                        document.querySelector(".online-chat").style.top = valueMax + "px";
                    }
                });

            document
                .querySelector(".online-chat__input")
                .addEventListener("blur", function () {
                    document
                        .querySelector(".online-chat")
                        .classList.remove("online-chat-focus");
                    if (
                        (document.documentElement.clientWidth <= 991) &
                        (document.documentElement.clientWidth >= 541)
                    ) {
                        document.querySelector(".online-chat").style.top = "unset";
                        document.querySelector(".online-chat").style.maxHeight = `${
                            chatHeight - 40
                        }px`;
                        chatBlockBody.scrollTop = chatBlockBody.scrollHeight;
                    }
                    if (document.documentElement.clientWidth < 541) {
                        document.querySelector(".online-chat").style.top = "unset";
                        document.querySelector(
                            ".online-chat",
                        ).style.maxHeight = `${chatHeight}px`;
                        chatBlockBody.scrollTop = chatBlockBody.scrollHeight;
                    }
                });
        }

        window.addEventListener("resize", () => {
            setTimeout(() => {
                chatBlockBody.scrollTop = chatBlockBody.scrollHeight;
            }, 500);
        });

        heightOnlineChat();
        window.addEventListener("resize", heightOnlineChat);

        eventFocusChat();
        window.addEventListener("resize", eventFocusChat);

        function closeRegulations() {
            let windowTerms = document.querySelector(".online-chat__rules");
            document.addEventListener("click", (e) => {
                if (windowTerms.classList.contains("rules_active")) {
                    const withinBoundaries = e.composedPath().includes(windowTerms);
                    if (!withinBoundaries) {
                        windowTerms.classList.remove("rules_active");
                    }
                }
            });
        }

        function closeChatClickWindow() {
            let windowTerms = document.querySelector(".online-chat");
            document.addEventListener("click", (e) => {
                if (windowTerms.classList.contains("online-chat_active")) {
                    const withinBoundaries = e.composedPath().includes(windowTerms);
                    if (!withinBoundaries) {
                        windowTerms.classList.remove("online-chat_active");
                        windowTerms.classList.remove("online-chat_active");
                        windowTerms.style.display = "none";
                        document.body.classList.remove("overflow-h");
                    }
                }
            });
        }

        closeChatClickWindow();
        closeRegulations();
    }

    //! Октрытие и закрытие чата на мобилках
    if (document.querySelector(".chat-open-btn")) {
        let btnOpenChat = document.querySelector(".chat-open-btn");
        let chatBlock = document.querySelector(".online-chat");
        let chatBlockBody = document.querySelector(".online-chat__body");
        let closeBtnChat = document.querySelector(".online-chat__icon-close");
        btnOpenChat.addEventListener("click", function () {
            setTimeout(() => {
                chatBlock.classList.add("online-chat_active");
                chatBlock.style.display = "flex";
                document.body.classList.add("overflow-h");
                chatBlockBody.scrollTop = chatBlockBody.scrollHeight;
            }, 100);
        });

        closeBtnChat.addEventListener("click", function () {
            chatBlock.classList.remove("online-chat_active");
            chatBlock.style.display = "none";
            document.body.classList.remove("overflow-h");
        });
    }

    //! Рулетка формула
    if (document.querySelector(".roulette__table")) {
        var inputTable = document.querySelector(".roulette__table-input");
        var btnsArrow = document.querySelectorAll(".roulette__table-link");
        var currentValue = document.querySelector(".roulette__current-block");
        var maxNumber = 500000000;

        inputTable.addEventListener("focus", function () {
            currentValue.classList.add("roulette__current-block_focus");
        });

        inputTable.addEventListener("focusout", function () {
            currentValue.classList.remove("roulette__current-block_focus");
        });

        inputTable.addEventListener("input", function () {
            if (
                inputTable.value != "" &&
                inputTable.value > 0 &&
                inputTable.value <= 500000
            ) {
                currentValue.style.color = "#fff";

                currentValue.classList.remove("roulette__current-block_focus");

                if (inputTable.value >= 10) {
                    currentValue.innerText = (inputTable.value + "000")
                        .split(".")
                        .join("")
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                } else {
                    currentValue.innerText = (inputTable.value + "000")
                        .split(".")
                        .join("");
                }

                inputTable.style.caretColor = "transparent";
            } else {
                currentValue.style.color = "#575757";
                currentValue.innerText = "Введите сумму...";
                inputTable.value = "";
                inputTable.style.caretColor = "#fff";
                currentValue.classList.add("roulette__current-block_focus");
            }
        });

        btnsArrow.forEach(function (input) {
            input.addEventListener("click", function (event) {
                currentValue.style.color = "#fff";
                // inputTable.focus();

                if (event.target.textContent == "CLEAR") {
                    inputTable.value = "";
                    currentValue.innerText = "";
                    currentValue.style.color = "#575757";
                    currentValue.innerText = "Введите сумму...";
                }

                if (event.target.textContent == "+10K") {
                    inputTable.value = Number(inputTable.value) + 10;
                    currentValue.innerText = String(Number(inputTable.value * 1000))
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (event.target.textContent == "+100K") {
                    inputTable.value = Number(inputTable.value) + 100;
                    currentValue.innerText = String(Number(inputTable.value * 1000))
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (event.target.textContent == "+1M") {
                    inputTable.value = Number(inputTable.value) + 1000;

                    currentValue.innerText = String(Number(inputTable.value * 1000))
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (event.target.textContent == "+10M") {
                    inputTable.value = Number(inputTable.value) + 10000;
                    currentValue.innerText = String(Number(inputTable.value * 1000))
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (event.target.textContent == "1/2") {
                    inputTable.value = (Number(inputTable.value) / 2).toFixed(3);

                    currentValue.innerText = String(
                        Math.round(Number(inputTable.value * 1000)),
                    )
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (event.target.textContent == "X2") {
                    inputTable.value = Number(inputTable.value) * 2;
                    currentValue.innerText = String(Number(inputTable.value * 1000))
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (event.target.textContent == "MAX") {
                    inputTable.value = maxNumber;
                    currentValue.innerText = String(maxNumber * 1000)
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (inputTable.value > maxNumber) {
                    inputTable.value = "";
                    currentValue.innerText = "";
                    currentValue.style.color = "#575757";
                    currentValue.innerText = "Введите сумму...";
                }
            });
        });
    }

    //TODO Сделать сниппет
    //!Перенос сообщения ошибку в рулетке
    let rouletteMsg = document.querySelector(".roulette__msg"); //что перенести
    let whereRouletteMsg = document.querySelector(".roulette-msg"); //куда перенести

    if (rouletteMsg && whereRouletteMsg) {
        if (document.documentElement.clientWidth < 575) {
            whereRouletteMsg.append(rouletteMsg);
        }
    }

    // //! скроллбар в конце
    // if (document.querySelector(".online-chat__list")) {
    // 	document.querySelector('.chat-open-btn').addEventListener('click', () => {
    // 		console.log(1)
    // 		let scrollBlock = document.body;
    // 		setTimeout(() => scrollBlock.scrollTo(0, 10000))
    // 	})
    // }

    //! Медиазапросы рулетка
    if (document.querySelector(".roulette")) {
        function setResizeStyle() {
            let windowHeigth = window.innerHeight;
            let windowWight = window.innerWidth;
            let bodyContent = document.body;

            if (windowWight <= 575) {
                if (windowHeigth >= 640 && windowHeigth <= 799) {
                    bodyContent.classList.add("height640-799");
                }
                if (windowHeigth >= 800 && windowHeigth <= 895) {
                    bodyContent.classList.add("height800-895");
                }
                if (windowHeigth >= 896 && windowHeigth <= 1000) {
                    bodyContent.classList.add("height896-1000");
                }
            }
        }

        setResizeStyle();
        //window.addEventListener('resize', setResizeStyle)
    }

    //===Модули===============================
    const popupLinks = document.querySelectorAll(".popup-link");
    const body = document.querySelector("body");
    const lockPadding = document.querySelectorAll(".lock-padding");

    let unlock = true;

    const timeout = 800;

    if (popupLinks.length > 0) {
        for (let index = 0; index < popupLinks.length; index++) {
            const popupLink = popupLinks[index];
            popupLink.addEventListener("click", function (e) {
                const popupName = popupLink.getAttribute("href").replace("#", "");
                const curentPopup = document.getElementById(popupName);
                popupOpen(curentPopup);
                e.preventDefault();
            });
        }
    }

    const popupCloseIcon = document.querySelectorAll(".close-popup,.modal-answer__no");
    if (popupCloseIcon.length > 0) {
        for (let index = 0; index < popupCloseIcon.length; index++) {
            const el = popupCloseIcon[index];
            el.addEventListener("click", function (e) {
                popupClose(el.closest(".popup"));
                e.preventDefault();
            });
        }
    }

    function popupOpen(curentPopup) {
        if (curentPopup && unlock) {
            const popupActive = document.querySelector(".popup.open");
            if (popupActive) {
                popupClose(popupActive, false);
            } else {
                bodyLock();
            }
            curentPopup.classList.add("open");
            curentPopup.addEventListener("click", function (e) {
                if (!e.target.closest(".popup__content")) {
                    popupClose(e.target.closest(".popup"));
                }
            });
        }
    }

    function popupClose(popupActive, doUnLock = true) {
        if (unlock) {
            popupActive.classList.remove("open");
            if (doUnLock) {
                bodyUnLock();
            }
        }
    }

    function bodyLock() {
        const lockPaddingValue =
            window.innerWidth - document.querySelector(".wrapper").offsetWidth + "px";
        if (lockPaddingValue.length > 0) {
            for (let index = 0; index < lockPadding.length; index++) {
                const el = lockPadding[index];
                el.style.paddingRight = lockPaddingValue;
            }
        }
        body.style.paddingRight = lockPaddingValue;
        body.classList.add("lock");

        unlock = false;
        setTimeout(function () {
            unlock = true;
        }, timeout);
    }

    function bodyUnLock() {
        setTimeout(function () {
            if (lockPadding.length > 0) {
                for (let index = 0; index < lockPadding.length; index++) {
                    const el = lockPadding[index];
                    el.style.paddingRight = "0px";
                }
            }
            body.style.paddingRight = "0px";
            body.classList.remove("lock");
        }, timeout);

        unlock = false;
        setTimeout(function () {
            unlock = true;
        }, timeout);
    }

    document.addEventListener("keydown", function (e) {
        if (e.which === 27) {
            const popupActive = document.querySelector(".popup.open");
            popupClose(popupActive);
        }
    });

    (function () {
        if (!Element.prototype.closest) {
            Element.prototype.closest = function (css) {
                var node = this;
                while (node) {
                    if (node.matches(css)) return node;
                    else node = node.parentElement;
                }
                return null;
            };
        }
    })();
    (function () {
        if (!Element.prototype.matches) {
            Element.prototype.matches =
                Element.prototype.matchesSelector ||
                Element.prototype.webkitMatchesSelector ||
                Element.prototype.mozMatchesSelector ||
                Element.prototype.msMatchesSelector;
        }
    })(); //Модальное окно  //!Сниппет "!modal" html
    //https://itchief.ru/javascript/tabs-for-site-on-css-js
    //TABS

    var $tabs = function (target) {
        var _elemTabs =
                typeof target === "string" ? document.querySelector(target) : target,
            _eventTabsShow,
            _showTab = function (tabsLinkTarget) {
                var tabsPaneTarget, tabsLinkActive, tabsPaneShow;
                tabsPaneTarget = document.querySelector(
                    tabsLinkTarget.getAttribute("href"),
                );
                tabsLinkActive =
                    tabsLinkTarget.parentElement.querySelector(".tabs__link_active");
                tabsPaneShow =
                    tabsPaneTarget.parentElement.querySelector(".tabs__pane_show");
                // если следующая вкладка равна активной, то завершаем работу
                if (tabsLinkTarget === tabsLinkActive) {
                    return;
                }
                // удаляем классы у текущих активных элементов
                if (tabsLinkActive !== null) {
                    tabsLinkActive.classList.remove("tabs__link_active");
                }
                if (tabsPaneShow !== null) {
                    tabsPaneShow.classList.remove("tabs__pane_show");
                }
                // добавляем классы к элементам (в завимости от выбранной вкладки)
                tabsLinkTarget.classList.add("tabs__link_active");
                tabsPaneTarget.classList.add("tabs__pane_show");
                document.dispatchEvent(_eventTabsShow);
            },
            _switchTabTo = function (tabsLinkIndex) {
                var tabsLinks = _elemTabs.querySelectorAll(".tabs__link");
                if (tabsLinks.length > 0) {
                    if (tabsLinkIndex > tabsLinks.length) {
                        tabsLinkIndex = tabsLinks.length;
                    } else if (tabsLinkIndex < 1) {
                        tabsLinkIndex = 1;
                    }
                    _showTab(tabsLinks[tabsLinkIndex - 1]);
                }
            };

        _eventTabsShow = new CustomEvent("tab.show", {detail: _elemTabs});

        _elemTabs.addEventListener("click", function (e) {
            var tabsLinkTarget = e.target;
            // завершаем выполнение функции, если кликнули не по ссылке
            if (!tabsLinkTarget.classList.contains("tabs__link")) {
                return;
            }
            // отменяем стандартное действие
            e.preventDefault();
            _showTab(tabsLinkTarget);
        });

        return {
            showTab: function (target) {
                _showTab(target);
            },
            switchTabTo: function (index) {
                _switchTabTo(index);
            },
        };
    };
    if (document.querySelectorAll(".tabs").length > 0) {
        $tabs(".tabs");
    } //Тултип  //!Сниппет "!tooltip" html
    //@//@include('../../../_module/JS/_validator-form.js', {}) //Валидатор форм  //!Сниппет "!forma" html
    if (document.getElementsByClassName("accordion")) {
        let acc = document.getElementsByClassName("accordion");
        let i;

        for (i = 0; i < acc.length; i++) {
            acc[i].addEventListener("click", function () {
                this.classList.toggle("accordion_active");
                let panel = this.nextElementSibling;
                if (panel.style.maxHeight) {
                    panel.style.maxHeight = null;
                } else {
                    panel.style.maxHeight = panel.scrollHeight + "px";
                }
            });
        }
    }
    //Валидатор форм  //!Сниппет "!accordion" html

    if (document.querySelector(".tel")) {
        //@//@include('../../../_module/JS/_maskPhone.js', {}) //Маска номера телефона (библиотека)
        //maskPhone('.tel');//Вызов функции маски номера телефона
    }


    /*
    Отправка суммы для вывода на бэкенд
     */

    const selectAmountItems = document.querySelectorAll(".select-amount__item");
    if (selectAmountItems.length > 0) {
        for (let index = 0; index < selectAmountItems.length; index++) {
            const el = selectAmountItems[index];
            el.addEventListener("click", async function (e) {
                const elAmount = el.querySelector('.select-amount__value');
                if (elAmount != null) {
                    const amount = parseInt(elAmount.innerText.trim());

                    // На бэкенд придет запрос в JSON-строке. Пример тела запроса: {"amount":50}
                    const body = {amount: amount};

                    // /out-amount - поменяйте на url,нужный бэкендерам
                    const r = await fetch('/out-amount', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json;charset=utf-8'
                        },
                        body: JSON.stringify(body)
                    });

                    if (r.ok) {
                        // всё прошло удачно
                    } else {
                        // Ошибка запроса
                    }

                }
                e.preventDefault();
            });
        }
    }

/////////Аккаунт уже привязан////////////////
    if (document.querySelector('#qqq')) {
        const vkBtn = document.querySelector('#qqq');
        vkBtn.addEventListener('click', () => {
            let modalAuth = document.querySelector('#modalAccountSocial')
            modalAuth.classList.add("open");
            // document.querySelector('.modal__balance').innerHTML = ` Ваш баланс: ${balanceUser}`
            modalAuth.addEventListener("click", function (e) {
                if (!e.target.closest(".popup__content")) {
                    document.querySelector('.popup.open').classList.remove("open");
                }
            });
        })
    }


    if (document.documentElement.clientWidth < 1000 | document.documentElement.clientWidth > 1000) {
        const h = document.querySelector('body').scrollHeight;
        document.querySelector('main').style.height = `${h}px`
    }

});
const media_prefix = JSON.parse(document.getElementById('media_prefix').textContent);
const static_prefix = JSON.parse(document.getElementById('static_prefix').textContent);