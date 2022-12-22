window.addEventListener("load", function () {
    const tabs_link_target = document.querySelectorAll("a.profil-main__tabs-link")[1];
    let click_event = new Event("click", {bubbles: true, cancelable: true, composed: true});
    tabs_link_target.dispatchEvent(click_event);
})
