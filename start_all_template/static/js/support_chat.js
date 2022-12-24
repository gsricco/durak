chatSocket.onmessage = super_new(chatSocket.onmessage);
const sendBtn = document.querySelector('.support__input-block-arrow')
let inputValue = document.querySelector('.support__chat-input')
const chatBlock = document.querySelector('.support__chat-block')
// const username = JSON.parse(document.getElementById('username').textContent)
const showFile = document.querySelector('#showFile')
// let imageTypeList = ['jpg', 'jpeg', 'gif', 'pjpeg', 'svg', 'svg+xml', 'tiff', 'icon', 'wbmp', 'webp', 'png']
let inputFile = document.querySelector('#file-add')
let host_url = window.location.host
let room_id = ''
let byteFile

let topBlock = document.querySelector('.support_chat_top_block')


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
//
// const chat_cleaner = () => {
//     const clear_chat_block = document.querySelectorAll('.support__chat-message_your')
//     clear_chat_block.forEach(item => item.remove())
// }
//
// const room_cleaner = () => {
//     const clear_room = document.querySelectorAll('.support__chat__room')
//     clear_room.forEach(item => item.remove())
// }

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
        if (user !== username) {
            spanUser.innerHTML = user
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
            const file_preview = document.querySelectorAll('.support__chat-message-text')
            const file_url = document.createElement('div')
            file_url.innerHTML = 'Файл'
            file_url.className = 'file_name'
            file_url.addEventListener('click', () => {

                window.open(`http://${host_url}${file_path}`)
            })

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
    console.log(dataList[0])
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


// function newUserMessage(message, user, file_path) {
//     if (true) {
//         const li = document.createElement('li')
//         li.className = 'support__chat-message support__chat-message_your'
//         const div = document.createElement('div')
//         div.className = 'support__chat-message-text'
//         const spanUser = document.createElement('span')
//         const span = document.createElement('span')
//         const fullDiv = document.createElement('div')
//         fullDiv.style.display = 'flex'
//         fullDiv.style.flexDirection = 'column'
//         spanUser.style.textAlign = 'right'
//         if (user !== username) {
//             li.style.flexDirection = ''
//             li.style.justifyContent = 'flex-start'
//             li.style.paddingLeft = '0%'
//             li.style.paddingRight = '16%'
//             div.style.background = '#2f2f2f'
//             div.style.borderRadius = '15px 15px 15px 0px'
//             spanUser.style.textAlign = 'left'
//         }
//         chatBlock.appendChild(li)
//         li.appendChild(div)
//
//         spanUser.innerHTML = user
//         span.innerHTML = message
//         div.appendChild(span)
//         fullDiv.appendChild(spanUser)
//         fullDiv.appendChild(div)
//         const file_url = document.createElement('div')
//             file_url.innerHTML = 'Файл'
//             file_url.className = 'file_name'
//             file_url.addEventListener('click', () => {
//                 window.open(`http://127.0.0.1:8000${file_path}`)
//             })
//         if (file_path) {
//             // const file_url = document.createElement('div')
//             // file_url.innerHTML = 'Файл'
//             // file_url.className = 'file_name'
//             // file_url.style.textAlign = ''
//             // file_url.addEventListener('click', () => {
//             //     window.open(`http://127.0.0.1:8000${file_path}`)
//             // })
//             if (user !== username) {
//                 file_url.style.textAlign = 'flex-start'
//                 file_url.style.background = 'red'
//                 li.appendChild(fullDiv)
//                 li.appendChild(file_url)
//             } else {
//                 li.appendChild(file_url)
//                 li.appendChild(fullDiv)
//             }
//         } else {
//             li.appendChild(fullDiv)
//         }
//     }
// }

// const newRoom = (room_name) => {
//     if (room_name !== username) {
//         const div = document.querySelector('.admin_support_chat_wrapper')
//         const room = document.createElement('p')
//         room.className = 'support__chat__room'
//         room.innerHTML = room_name
//         room.addEventListener('click', () => {
//             let room_value = room.innerText
//             room_id = room_value
//             topBlock.innerHTML = `Чат поддержки с ${room_id}`
//             chat_cleaner()
//             room_cleaner()
//             chatS.send(JSON.stringify({
//                 'chat_type': 'support_admin',
//                 'receiver_user_room': room_value
//             }))
//         })
//         div.appendChild(room)
//     }
// };

// const chatS = new WebSocket(
//     'ws://'
//     + window.location.host
//     + '/ws/chat/'
//     + 'admin_chat'
//     + '/'
// )
function super_new(f) {
    return function () {
        let ws_connect = f.apply(this, arguments);
        let data = JSON.parse(arguments[0].data)
        if (data.chat_type === 'support') {
            if (data.list_message) {
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
    if (is_auth === true) {
        if(byteFile || inputValue.value){
        chatSocket.send(JSON.stringify({
            'file': byteFile,
            "chat_type": "support",
            'message': inputValue.value,

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

