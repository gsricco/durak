const sendBtn = document.querySelector('.support__input-block-arrow')
        let inputValue = document.querySelector('.support__chat-input')
        const chatBlock = document.querySelector('.support__chat-block')
        const username = JSON.parse(document.getElementById('username').textContent)
        let room_id = ''
        let byteFile
        let topBlock = document.querySelector('.support_chat_top_block')


        function checkFileSize(elem) {
            const maxSize = 10000000;
            const fileSize = elem.files[0].size;
            if (fileSize > maxSize) {
                showFile.innerHTML = "<span>Файл слишком большой  </span>"
                setInterval(() => showFile.innerHTML = '', 2000)
            } else {
                var reader = new FileReader();
                reader.readAsDataURL(elem.files[0]);
                reader.onload = function () {
                    byteFile = reader.result
                };
                reader.onerror = function (error) {
                    console.log('Error: ', error);
                };
                showFile.innerHTML = "<span>Загрузка</span>"
                setInterval(() => showFile.innerHTML = '', 2000)
            }


        }

        const chat_cleaner = () => {
            const clear_chat_block = document.querySelectorAll('.support__chat-message_your')
            clear_chat_block.forEach(item => item.remove())
        }

        const room_cleaner = () => {
            const clear_room = document.querySelectorAll('.support__chat__room')
            clear_room.forEach(item => item.remove())
        }

         function newUserMessage (message, user, file_path){
            if(user === username || user === room_id) {
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
                    li.style.flexDirection = ''
                    li.style.justifyContent = 'flex-start'
                    li.style.paddingLeft = '0%'
                    li.style.paddingRight = '16%'
                    div.style.background = '#2f2f2f'
                    div.style.borderRadius = '15px 15px 15px 0px'
                    spanUser.style.textAlign = 'left'
                }
                chatBlock.appendChild(li)
                li.appendChild(div)

                spanUser.innerHTML = user
                span.innerHTML = message
                div.appendChild(span)
                fullDiv.appendChild(spanUser)
                fullDiv.appendChild(div)
                if (file_path) {
                    const file_url = document.createElement('div')
                    file_url.innerHTML = 'Файл'
                    file_url.className = 'file_name'
                    file_url.addEventListener('click', () => {
                        window.open(`http://127.0.0.1:8000${file_path}`)
                    })
                    if (user !== username) {
                        li.appendChild(fullDiv)
                        li.appendChild(file_url)
                    } else {
                        li.appendChild(file_url)
                        li.appendChild(fullDiv)
                    }
                } else {
                    li.appendChild(fullDiv)
                }
            }
        }

        const newRoom = (room_name) => {
            if (room_name !== username) {
                const div = document.querySelector('.admin_support_chat_wrapper')
                const room = document.createElement('p')
                room.className = 'support__chat__room'
                room.innerHTML = room_name
                room.addEventListener('click', () => {
                    let room_value = room.innerText
                    room_id = room_value
                    topBlock.innerHTML = `Чат поддержки с ${room_id}`
                    chat_cleaner()
                    room_cleaner()
                    chatS.send(JSON.stringify({
                        'chat_type': 'support_admin',
                        'receiver_user_room': room_value
                    }))
                })
                div.appendChild(room)
            }
        };

        const chatS = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + 'admin_chat'
            + '/'
        )

        chatS.onmessage = function (e) {


            const data = JSON.parse(e.data);
            if (data.room_name) {
                room_cleaner()
                data.room_name.forEach(e => newRoom(e))

            }

                if (data.chat_type === 'support' ) {
                    if (data.list_message) {
                        data.list_message.forEach((mess) => {
                            if (mess.file_message) {
                                newUserMessage(mess.message, mess.user_posted.username, mess.file_message)
                            } else {
                                newUserMessage(mess.message, mess.user_posted.username)
                            }
                        })
                    } else {
                        if (data.file_path !== '/') {
                            newUserMessage(`${data.message}`, data.user, data.file_path)
                        } else {
                            newUserMessage(`${data.message}`, data.user)
                        }
                    }
                    chatBlock.scrollTop = chatBlock.scrollHeight
                }
            }


            inputValue.focus();
            inputValue.onkeyup = function (e) {
                if (e.keyCode === 13) {  // enter, return
                    sendBtn.click();
                }
            };
            sendBtn.addEventListener('click', () => {
                chatS.send(JSON.stringify({
                    'chat_type': 'support_admin',
                    'message': inputValue.value,
                    'receive': room_id,
                    'file': byteFile,
                }));
                byteFile = ''
                inputValue.value = '';
            })

