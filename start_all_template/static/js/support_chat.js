chatSocket.onmessage = super_new(chatSocket.onmessage);
const sendBtn = document.querySelector('.support__input-block-arrow')
let inputValue = document.querySelector('.support__chat-input')
const chatBlock = document.querySelector('.support__chat-block')
const showFile = document.querySelector('#showFile')
let inputFile = document.querySelector('#file-add')
let host_url = window.location.host
let room_id = ''
let byteFile

chatBlock.addEventListener('mouseup', (event) => {
    chatSocket.send(JSON.stringify({
            'init_faq': 'init_faq',
        }));
});

function checkFileSize(elem) {
    //проверка размера файла
    const maxSize = 10000000;
    const fileSize = elem.files[0].size;
    if (fileSize > maxSize) {
        showFile.innerHTML = "<span>File is big</span>"
        setTimeout(() => {showFile.innerHTML = '';
                                    inputFile.value = '';
            }
            , 2000)
    }
    else {
        //проверка является ли файл картинкой
        if (elem.files[0].type.split('/')[0] === 'image'){
        var reader = new FileReader();
        reader.readAsDataURL(elem.files[0]);
        reader.onload = function () {
            byteFile = reader.result
        };
        reader.onerror = function (error) {
        };
        showFile.innerHTML = "<span>Load</span>"
        setTimeout(() => showFile.innerHTML = '', 2000)
            }else {

            showFile.innerHTML = "<span>File not image</span>"
            setTimeout(() => {showFile.innerHTML = ''
                                      inputFile.value = ''
                }
                , 2000)
        }
    }
}


function newUserMessage(message, user, file_path) {

        const li = document.createElement('li')
        li.className = 'support__chat-message support__chat-message_your'
        const div = document.createElement('div')
        div.className = 'support__chat-message-text'
        const spanUser = document.createElement('span')
        const span = document.createElement('span')
        const fullDiv = document.createElement('div')
        fullDiv.style.display = 'flex'
        fullDiv.style.flexDirection = 'column'
        spanUser.style.textAlign = 'right'
        console.log(username, 'ETO V SUPPORT CHATE')
    console.log(user)
        if (user !== username) {
            // spanUser.innerHTML = user
            li.style.flexDirection = ''
            li.style.justifyContent = 'flex-start'
            li.style.paddingLeft = '0%'
            li.style.paddingRight = '16%'
            div.style.background = '#2f2f2f'
            div.style.borderRadius = '15px 15px 15px 0px'
            spanUser.style.textAlign = 'left'
        }
        chatBlock.appendChild(li)
        span.innerHTML = message
        div.appendChild(span)
        fullDiv.appendChild(spanUser)
        if (file_path) {
                if (user !== username) {
                    let newDiv = document.createElement('div')
                    newDiv.innerHTML = `<div style="display: flex; flex-direction: column; padding-bottom: 10px">
                                            <div class="support__chat-message-text" style=" padding: 0px ">
                                                <img src="http://${host_url}${file_path}">
                                            </div>                
                                        </div>`
                    div.style.alignItems = 'flex-start'
                    fullDiv.appendChild(newDiv)
                    if(message){fullDiv.appendChild(div)
                        }
                    li.appendChild(fullDiv)

                } else {
                    let newDiv = document.createElement('div')
                    newDiv.innerHTML = `<div style="display: flex; flex-direction: column; padding-bottom: 10px">
                                            <div class="support__chat-message-text" style=" padding: 0px ">
                                                <img src="http://${host_url}${file_path}">
                                            </div>                
                                        </div>`
                    div.style.alignItems = 'flex-end'
                    fullDiv.appendChild(newDiv)
                    if(message){fullDiv.appendChild(div)}
                    li.appendChild(fullDiv)
                }
        } else {
            fullDiv.appendChild(div)
            li.appendChild(fullDiv)

        }
    }

function newSellItemMessage(message,user) {
    let dataList = message.split(';')
    const li = document.createElement('li')
     if (user !== username) {
            li.className = 'support__chat-message'
        } else {
            li.className = 'support__chat-message support__chat-message_your'
        }
    const div = document.createElement('div')
    div.className = 'support__chat-message-text'
    div.innerHTML = `    
              <span class="support__chat-name">${dataList[0]}</span>
                <div class="support__chat-smile-img">
                  <svg><use xlink:href="/static/img/icons/sprite.svg#${dataList[2]}"></use></svg>
                </div>
              <h3 class="support__chat-smile-title">${dataList[1]}</h3>
`
    chatBlock.appendChild(li)
li.appendChild(div)
}


function super_new(f) {
    return function () {
        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data)

        if (data.chat_type === 'support') {
            if (data.list_message) {
                console.log(data, "SUPPORT WS")
                data.list_message.forEach((mess) => {
                        if (mess.is_sell_item) {
                            newSellItemMessage(mess.message,mess.user_posted.username)
                        } else {
                            if (mess.file_message) {
                                newUserMessage(mess.message, mess.user_posted.username, mess.file_message)
                            } else {
                                newUserMessage(mess.message, mess.user_posted.username)
                            }
                        }
                    }
                )
            } else {
                if (data.is_sell_item) {
                    newSellItemMessage(data.message,data.user)
                } else {
                    if (data.file_path !== '/') {
                        newUserMessage(`${data.message}`, data.user, data.file_path)
                    } else {
                        newUserMessage(`${data.message}`, data.user)
                    }
                }
            }
        setTimeout(()=>{chatBlock.scrollTop = chatBlock.scrollHeight},100)
        }
        if (data.not_read_count){
            document.title = `Помощь (${data.not_read_count})`
        }else{document.title = 'Помощь'}
        if (0<=data.last_visit<=1){
            disableChat(data.last_visit)
        }
    }
}


inputValue.onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        sendBtn.click();
    }
};
sendBtn.addEventListener('click', () => {
    if (is_auth === true) {
        if(byteFile || inputValue.value.trim()){
        chatSocket.send(JSON.stringify({
            'file': byteFile,
            "chat_type": "support",
            'message': inputValue.value.trim(),
            // 'init_faq': 'init_faq'
        }));
        }

    } else {
        let modalAuth = document.querySelector('#authorization')
        modalAuth.classList.add("open");
        modalAuth.addEventListener("click", function (e) {
            if (!e.target.closest(".popup__content")) {
                document.querySelector('.popup.open').classList.remove("open");
            }
        });
    }
    inputValue.value = '';
    byteFile = ''
    inputFile.value = ''
})
chatSocket.onopen = function (e) {
    chatSocket.send(JSON.stringify({
        'last_visit': current_user_id
    }));

};
function disableChat(foo) {
    let timer = 60000
    if (foo === 1){
        timer = 0
    }
    if (document.querySelector(".support__chat")) {
        function clickChat() {
            let block = document.querySelector(".support__overflow");
            block.style.opacity = "0";
            setTimeout(function () {
                block.style.display = "none";
            }, 1000);
            inputValue.focus();
        }
        setTimeout(clickChat, timer);
    }
}