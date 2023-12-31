const sendBtn = document.querySelector('.support__input-block-arrow')
let inputValue = document.querySelector('.support__chat-input')
let inputFile = document.querySelector('#file-add')
const chatBlock = document.querySelector('.support__chat-block')
const username = JSON.parse(document.getElementById('username').textContent)
const usernamegame = JSON.parse(document.getElementById("usernamegame").textContent)
let room_id = ''
let room_name = ''
let byteFile
let topBlock = document.querySelector('.support_chat_top_block')
let onlineAdmin = document.querySelector('#onlineAdmin')
let host_url = window.location.host
let notReadAllCount = 0
document.title = 'Админ ЧАТ'

document.querySelector('#content h1').innerHTML = 'Выберите ЧАТ'
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

function newSellItemMessage(message, user, usernamegame) {
    if (user === username || user === room_name) {
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
}


const chat_cleaner = () => {
    chatBlock.innerHTML = ''
}

const room_cleaner = () => {
    notReadAllCount = 0
    const clear_room = document.querySelectorAll('.support__chat__room')
    clear_room.forEach(item => item.remove())
}

function newUserMessage(message, user, usernamegame, file_path) {
    if (user === username || user === room_name) {
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
        spanUser.style.color = '#c8c8c8'
        if (user !== username) {
            url = `http://${host_url}/Gtt56fgutedghuuteesgy43f/accaunts/customuser/${room_id}/change/`
            spanUser.onclick = ()=>{ window.open(url,'_blank')}
            spanUser.classList.add('username_active')
            li.style.flexDirection = ''
            li.style.justifyContent = 'flex-start'
            li.style.paddingLeft = '0%'
            li.style.paddingRight = '16%'
            div.style.background = '#2f2f2f'
            div.style.borderRadius = '15px 15px 15px 0px'
            spanUser.style.textAlign = 'left'
        }
        chatBlock.appendChild(li)
        spanUser.innerHTML = usernamegame
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
}

let text;
const newRoom = (data) => {
    if (data.user.username && username) {
        if (data.user.username !== username) {
            const div = document.querySelector('.admin_support_chat_wrapper')
            const room = document.createElement('p')
            room.className = 'support__chat__room'
                      if(data.user.username === room_name){
                room.classList.add('active_room')
            }
            room.innerHTML = data.user.usernamegame

            room.addEventListener('click', (e) => {
                let room_value = room.innerText
                room_id = data.room_id
                room_name = data.user.username
                topBlock.innerHTML = `Чат поддержки`
                chat_cleaner()
                room_cleaner()
                text = e.target.textContent
                e.target.classList.toggle('active_room')
                chatS.send(JSON.stringify({
                    'chat_type': 'support_admin',
                    'receiver_user_room': data.room_id
                }))
            })
            div.appendChild(room)
            if (data.notread.not_read_counter !== 0){
                notReadAllCount += data.notread.not_read_counter
                let notRead = document.createElement('span')
                notRead.innerHTML = `${data.notread.not_read_counter} `
                notRead.className = 'not_read'
                room.appendChild(notRead)
            }
        }
    }
};

const chatS = new WebSocket(
    'wss://'
    + window.location.host
    + '/ws/chat/'
    + 'admin_chat'
    + '/'
)

chatS.onmessage = function (e) {
    const data = JSON.parse(e.data);
    if (data.get_online && data.staff){
        onlineAdmin.innerHTML = ` ${data.get_online}`
    }

    if (data.room_data) {
        room_cleaner()
        data.room_data.forEach(e => newRoom(e))
    }
        if(notReadAllCount>0){
        document.title = `Сообщения (${notReadAllCount})`
        }else {
          document.title = 'Админ ЧАТ'
               }
    if (data.chat_type === 'support') {
        if (data.list_message) {
            data.list_message.forEach((mess) => {
                    if (mess.is_sell_item) {
                        newSellItemMessage(mess.message, mess.user_posted.username, mess.user_posted.usernamegame)
                    } else {
                        if (mess.file_message) {
                            newUserMessage(mess.message, mess.user_posted.username, mess.user_posted.usernamegame, mess.file_message)
                        } else {
                            newUserMessage(mess.message, mess.user_posted.username, mess.user_posted.usernamegame)
                        }
                    }
                }
            )
        } else {
            if (data.is_sell_item) {
                newSellItemMessage(data.message, data.user)
            } else {
                if (data.file_path !== '/') {
                    newUserMessage(`${data.message}`, data.user, data.usernamegame, data.file_path)
                } else {
                    newUserMessage(`${data.message}`, data.user, data.usernamegame)
                }
            }
        }
        setTimeout(()=>{chatBlock.scrollTop = chatBlock.scrollHeight},100)
    }
}


inputValue.focus();
inputValue.onkeyup = function (e) {
    if (e.keyCode === 13) {  // enter, return
        sendBtn.click();
    }
};
sendBtn.addEventListener('click', () => {
    if(byteFile || inputValue.value.trim()) {
        chatS.send(JSON.stringify({
            'chat_type': 'support_admin',
            'message': inputValue.value.trim(),
            'receive': room_id,
            'file': byteFile,
        }));
    }
    byteFile = ''
    inputValue.value = '';
    inputFile.value = ''
})

