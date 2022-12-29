function popupOpen(curentPopup) {
        if (curentPopup) {
            curentPopup.classList.add("open");
            curentPopup.addEventListener("click", function (e) {
                if (!e.target.closest(".popup__content")) {
                    popupClose(e.target.closest(".popup"));
                }
            });
        }
    }


const popupPay = document.getElementById("balanceOk");
popupOpen(popupPay);




