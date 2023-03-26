// 'use strict';
const UserBalance1 = document.querySelector('.header__profile-sum>span')
if (UserBalance1) {
    let maxNumber = UserBalance1.innerHTML
}
else {
    let maxNumber = 0
}

window.addEventListener("DOMContentLoaded", () => {
    const BODY = document.querySelector("body");
    const MAIN = document.querySelector("main");
    const FOOTER = document.querySelector("footer");
	
	// Футер убираем на Пользовательском соглашении
  if (document.querySelector(".agreement__title")){
	  let FooterParam = document.querySelector(".footer");
	  FooterParam.style.display = "none";
  }
	
    //Отображение смайла 25%
  if (document.querySelector(".amount-selection__form")) {
    let randomSmileNum = Math.floor(Math.random() * 4);
    var smileView = document.querySelector(".amount-selection__smiley");
    if(randomSmileNum==0){smileView.style.display = "";}
          else {smileView.style.display = "none";}
  }
    
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
                // document
                //     .querySelector(".header__profile")
                //     .append(document.querySelector(".header__profile-progressbar"));
                document
                    .querySelector(".header__profile")
                    .append(document.querySelector(".header__btns"));
            }

            if (document.documentElement.clientWidth > 540) {
                document
                // .querySelector(".header__profile-info")
                // .append(document.querySelector(".header__profile-progressbar"));
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
            // .querySelector(".header__profile")
            // .append(document.querySelector(".header__profile-progressbar"));
            document
                .querySelector(".header__profile")
                .append(document.querySelector(".header__btns"));
        }

        if (document.documentElement.clientWidth > 540) {
            document
            // .querySelector(".header__profile-info")
            // .append(document.querySelector(".header__profile-progressbar"));
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
                // document
                //     .querySelector(".profil__name-text")
                //     .prepend(document.querySelector(".profil__progressbar-lvl-img"));
                // document
                //     .querySelector(".profil__name-text")
                //     .append(document.querySelector(".profil__progressbar-lvl-num"));
                // document
                //     .querySelector(".profil__progressbar-row")
                //     .append(document.querySelector(".profil__progressbar-lvl-progress"));
                document
                    .querySelector(".profil__row")
                    .append(document.querySelector(".profil__btns"));
            }

            if (document.documentElement.clientWidth > 541) {
                document
                //     .querySelector(".profil__progressbar-lvl")
                //     .append(document.querySelector(".profil__progressbar-lvl-img"));
                // document
                //     .querySelector(".profil__progressbar-lvl")
                //     .append(document.querySelector(".profil__progressbar-lvl-num"));
                // document
                //     .querySelector(".profil__progressbar-lvl")
                //     .append(document.querySelector(".profil__progressbar-lvl-progress"));
                document
                    .querySelector(".profil__info")
                    .append(document.querySelector(".profil__btns"));
            }
        });

        if (document.documentElement.clientWidth < 541) {
            document
            //     .querySelector(".profil__name-text")
            //     .prepend(document.querySelector(".profil__progressbar-lvl-img"));
            // document
            //     .querySelector(".profil__name-text")
            //     .append(document.querySelector(".profil__progressbar-lvl-num"));
            // document
            //     .querySelector(".profil__progressbar-row")
            //     .append(document.querySelector(".profil__progressbar-lvl-progress"));
            document
                .querySelector(".profil__row")
                .append(document.querySelector(".profil__btns"));
        }

        if (document.documentElement.clientWidth > 541) {
            // document
            //     .querySelector(".profil__progressbar-lvl")
            // .append(document.querySelector(".profil__progressbar-lvl-img"));
            // document
            //     .querySelector(".profil__progressbar-lvl")
            // .append(document.querySelector(".profil__progressbar-lvl-num"));
            // document
            //     .querySelector(".profil__progressbar-lvl")
            // .append(document.querySelector(".profil__progressbar-lvl-progress"));
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

    // if (document.querySelector(".support__chat")) {
    //     function clickChat() {
    //         let block = document.querySelector(".support__overflow");
    //         block.style.opacity = "0";
    //         setTimeout(function () {
    //             block.style.display = "none";
    //         }, 1000);
    //     }
    //
    //     setTimeout(clickChat, 10000);
    // }

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

    //! Формула перевода рублей в валюту и обратно
    // if (document.querySelector(".amount-selection__form")) {
    //     var inputForm = document.querySelector(".amount-selection__input");
    //     var sumCurrent = document.querySelector(".num-game-currency__span-curent");
    //     var btnForm = document.querySelector(".amount-selection__btn");

    //     inputForm.addEventListener("input", sumScore);
    //     sumCurrent.addEventListener("input", sumValute);

    //     function sumScore() {
    //         let inputValueDinamic = inputForm.value.split(/[^0-9]/g);
    //         if (inputValueDinamic.length > 1) {
    //             inputForm.value = "";
    //         } else {
    //             if (inputForm.value < 69) {
    //                 sumCurrent.value = `${inputForm.value * 0}`;
    //                 btnForm.classList.add("btn-disable-sum");
    //             }

    //             if (inputForm.value >= 69) {
    //                 btnForm.classList.remove("btn-disable-sum");
    //             }

    //             if (inputForm.value >= 69 && inputForm.value <= 109) {
    //                 sumCurrent.value = `${parseFloat(
    //                     (inputForm.value * 725) / 1000,
    //                 ).toFixed(0)}`;
    //             }

    //             if (inputForm.value >= 110 && inputForm.value <= 179) {
    //                 sumCurrent.value = `${parseFloat(
    //                     (inputForm.value * 910) / 1000,
    //                 ).toFixed(0)}`;
    //             }

    //             if (inputForm.value >= 180 && inputForm.value <= 239) {
    //                 sumCurrent.value = `${parseFloat(
    //                     (inputForm.value * 1389) / 1000,
    //                 ).toFixed(0)}`;
    //             }

    //             if (inputForm.value >= 240 && inputForm.value <= 459) {
    //                 sumCurrent.value = `${parseFloat(
    //                     (inputForm.value * 2084) / 1000,
    //                 ).toFixed(0)}`;
    //             }

    //             if (inputForm.value >= 460 && inputForm.value <= 1274) {
    //                 sumCurrent.value = `${parseFloat(
    //                     (inputForm.value * 2174) / 1000,
    //                 ).toFixed(0)}`;
    //             }

    //             if (inputForm.value >= 1275) {
    //                 sumCurrent.value = `${parseFloat(
    //                     (inputForm.value * 2353) / 1000,
    //                 ).toFixed(0)}`;
    //             }
    //         }
    //     }

    //     function sumValute() {
    //         let inputValueDinamic = sumCurrent.value.split(/[^0-9]/g);
    //         if (inputValueDinamic.length > 1) {
    //             sumCurrent.value = "";
    //         } else {
    //             let currentCredint = (sumCurrent.value / 50000) * 1000;

    //             if (currentCredint >= 1) {
    //                 btnForm.classList.remove("btn-disable-sum");
    //             } else {
    //                 btnForm.classList.add("btn-disable-sum");
    //             }

    //             if (currentCredint < 1) {
    //                 inputForm.value = "";
    //             }
    //             if (currentCredint <= 2 && currentCredint >= 1) {
    //                 inputForm.value = `${(currentCredint * 69).toFixed(1)}`;
    //             }

    //             if (currentCredint <= 5 && currentCredint >= 2) {
    //                 inputForm.value = `${(currentCredint * 55).toFixed(1)}`;
    //             }

    //             if (currentCredint <= 10 && currentCredint >= 5) {
    //                 inputForm.value = `${(currentCredint * 36).toFixed(1)}`;
    //             }

    //             if (currentCredint <= 20 && currentCredint >= 10) {
    //                 inputForm.value = `${(currentCredint * 27.5).toFixed(1)}`;
    //             }

    //             if (currentCredint <= 40 && currentCredint >= 20) {
    //                 inputForm.value = `${(currentCredint * 23).toFixed(1)}`;
    //             }

    //             if (currentCredint <= 60 && currentCredint >= 40) {
    //                 inputForm.value = `${(currentCredint * 21.25).toFixed(1)}`;
    //             }

    //             if (currentCredint >= 60) {
    //                 inputForm.value = `${(currentCredint * 20).toFixed(1)}`;
    //             }

    //             if (sumCurrent.value == "" && sumCurrent.value == 0) {
    //                 inputForm.value = "";
    //             }
    //         }
    //     }
    // }

    // ===============================================================
    // Расчёт по кол-ву руб:
    // от 69 до 109р кол-во кредов = (введенное число руб.)*725
    // от 110 до 179р кол-во кредов = (введенное число руб.)*910
    // от 180 до 239р кол-во кредов = (введенное число руб.)*1389
    // от 240 до 459р кол-во кредов = (введенное число руб.)*2084
    // от 460 до 1274р кол-во кредов = (введенное число руб.)*2174
    // от 1275 кол-во кредов = (введенное число руб.)*2353


    //!звук - это надо!!!!!!!!!!!!!!!!!!!!
    if (document.querySelector(".sound")) {
        let sound = document.querySelector(".sound");
        let soundImg = document.querySelector(".sound svg use");
        // if (sessionStorage.getItem("data-value")==="soundOff") {
        //     soundImg.setAttribute("xlink:href", `static/img/icons/sprite.svg#sound_on`);
        //     sound.setAttribute("data-value", "soundOff");
        //     sessionStorage.setItem("data-value",sound.getAttribute("data-value"))
        // } else if (sessionStorage.getItem("data-value")==="soundOn"){
        //     soundImg.setAttribute("xlink:href", `static/img/icons/sprite.svg#sound_off`);
        //     sound.setAttribute("data-value", "soundOn");
        //     sessionStorage.setItem("data-value", sound.getAttribute("data-value"))
        // }

        sound.addEventListener("click", () => {
            if (sound.getAttribute("data-value") == "soundOn") {
                soundImg.setAttribute("xlink:href", `static/img/icons/sprite.svg#sound_on`);
                sound.setAttribute("data-value", "soundOff");
            } else if (sound.getAttribute("data-value") == "soundOff") {
                soundImg.setAttribute("xlink:href", `static/img/icons/sprite.svg#sound_off`);
                sound.setAttribute("data-value", "soundOn");
            }
            // sessionStorage.setItem("data-value", sound.getAttribute("data-value"))
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
                        (document.documentElement.clientWidth <= 991) &&
                        (document.documentElement.clientWidth >= 541)
                    ) {
                        document.querySelector(".online-chat").style.maxHeight = `unset`;
                        // document.querySelector(".online-chat").style.top = 77 + "px";
                    } else if (document.documentElement.clientWidth < 541) {
                        document.querySelector(".online-chat").style.maxHeight = `unset`;
                        // document.querySelector(".online-chat").style.top = valueMax + "px";
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
        let inputTable = document.querySelector(".roulette__table-input");
        let btnsArrow = document.querySelectorAll(".roulette__table-link");
        let currentValue = document.querySelector(".roulette__current-block");

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
                    inputTable.value = maxNumber/1000;
                    currentValue.innerText = String(maxNumber * 1)
                        .split(/(?=(?:...)*$)/)
                        .join(" ");
                }

                if (Number(inputTable.value*1000) > Number(maxNumber)) {
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

if (is_auth) {
    let UserBalancer = Number(document.querySelector('#userBal').textContent)

    if (UserBalancer < 1000000) {
        let nal = UserBalancer / 1000
        if (UserBalancer % 1000 === 0) {
            UserBalancerShow = nal + 'K'
        } else {
            let strList = String(nal).split('.')
            UserBalancerShow = `${strList[0]}.${strList[1].slice(0, 1)}K`
        }
    } else {
        //если больше 1млн
        let nal = UserBalancer / 1000000
        let strList = String(nal).split('.')
        if (UserBalancer % 1000000 === 0) {
            UserBalancerShow = nal + 'M'
        } else if (UserBalancer < 10000000) {
            UserBalancerShow = `${strList[0]}.${strList[1].slice(0, 2)}M`
        } else if (UserBalancer >= 10000000 && UserBalancer < 100000000) {
            UserBalancerShow = `${strList[0]}.${strList[1].slice(0, 1)}M`
        } else if (UserBalancer > 100000000) {
            UserBalancerShow = `${strList[0]}M`
        }
    }

    document.querySelector('#userBal').innerHTML = `${UserBalancerShow}`
    document.querySelector('#userBalMob').innerHTML = `${UserBalancerShow}`
}
const btnAccordionQuestion = document.querySelectorAll(".accordion-wrapper.faq__wrapper>button")
const panelQuestion=document.querySelectorAll('.faq__text-wrapper')

btnAccordionQuestion.forEach((btn,index)=>{
    if (btn){
        btn.addEventListener('click',()=>{
            panelQuestion[index].style.display = panelQuestion[index].style.display === 'block' ? 'none' : 'block'
        })
    }
})

function modalAuth(){
    let modalAuth = document.querySelector('#authorization')
    modalAuth.classList.add("open");
    modalAuth.addEventListener("click", function (e) {
        if (!e.target.closest(".popup__content")) {
            if(document.querySelector('.popup.open')){
                document.querySelector('.popup.open').classList.remove("open");
            }
        }
    });
}
const cahmax=function(n){maxNumber=n}

