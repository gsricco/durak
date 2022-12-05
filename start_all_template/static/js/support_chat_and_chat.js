const sendBtn = document.querySelector('.support__input-block-arrow')
let inputValue = document.querySelector('.support__chat-input')
const chatBlock = document.querySelector('.support__chat-block')
const showFile = document.querySelector('#showFile')
let byteFile

//проверка на размер файла, если всё ОК преобразуем файл в base64 и записываем его в переменную byteFile
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

//слушаем событие клик на стрелочке отправить , при нажатии отправляем json
//после отпрввки обнуляем byteFile и строку инпута
sendBtn.addEventListener('click', () => {
    if (is_auth === true) {
        chatSocket.send(JSON.stringify({
            'file': byteFile,
            "chat_type": "support",
            'message': inputValue.value,
        }));
    } else {
        alert('No auth user, sorry')
    }
    inputValue.value = '';
    byteFile = ''

})

//отправка сообщения при нажатии на enter
inputValue.focus();
inputValue.onkeyup = function (e) {
    if (e.keyCode === 13) {
        sendBtn.click()
    }
};

//функция отображения сообщений
const newUserMessage = (message, user, file_path) => {

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
        li.style.justifyContent = 'flex-start'
        li.style.paddingLeft = '0%'
        li.style.paddingRight = '16%'
        div.style.background = 'orange'
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