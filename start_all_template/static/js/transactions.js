const tabs_link_target = document.querySelectorAll("a.profil-main__tabs-link");
// остаёмся на профиле при клике на вкладку
tabs_link_target[0].addEventListener("click", function() {
    const url = new URL(document.location);
    const searchParams = url.searchParams;
    searchParams.delete("page");
    window.history.pushState({}, '', url.toString());
})
// переключаемся на транзакции при загрузке страницы
window.addEventListener("load", function () {
    let click_event = new Event("click", {bubbles: true, cancelable: true, composed: true});
    tabs_link_target[1].dispatchEvent(click_event);
})
