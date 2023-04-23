const socket = io();

const textForm = document.getElementById('text-form');
const textInput = document.getElementById('text-input');
const receivedText = document.getElementById('received-text');
const processingIndicator = document.getElementById('processing-indicator');

textForm.addEventListener('upload', (event) => {
    event.preventDefault();
    const text = textInput.value.trim();
    if (text) {
        const userText = document.createElement('p');

        const avatar = document.createElement('img');
        avatar.src = 'http://occ-0-999-1001.1.nflxso.net/dnm/api/v6/K6hjPJd6cR6FpVELC5Pd6ovHRSk/AAAABWHxaOxUNqEupjwCw-M9tgFfGFlQ22EjoG2ZYC1FsjjAWSdxOIfjdifW-rJrpNaLzTC0rpsRhE7DoH8h2zWxIQXEKaAsFUuDO2yl.png?r=2b1)';
        avatar.className = 'user-avatar';
        userText.appendChild(avatar);
        userText.appendChild(document.createTextNode(text));
        userText.className = 'user-text';

        receivedText.appendChild(userText);
        socket.emit('upload_text', text);

        textInput.value = '';
    }
});

textForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const text = textInput.value.trim();
    if (text) {
        const userText = document.createElement('p');

        const avatar = document.createElement('img');
        avatar.src = 'http://occ-0-999-1001.1.nflxso.net/dnm/api/v6/K6hjPJd6cR6FpVELC5Pd6ovHRSk/AAAABWHxaOxUNqEupjwCw-M9tgFfGFlQ22EjoG2ZYC1FsjjAWSdxOIfjdifW-rJrpNaLzTC0rpsRhE7DoH8h2zWxIQXEKaAsFUuDO2yl.png?r=2b1)';
        avatar.className = 'user-avatar';
        userText.appendChild(avatar);
        userText.appendChild(document.createTextNode(text));
        userText.className = 'user-text';

        receivedText.appendChild(userText);

        socket.emit('send_text', text);
        textInput.value = '';
        textInput.disabled = true;
        processingIndicator.style.display = 'block';
        receivedText.scrollTop = receivedText.scrollHeight;

    }
});

textInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    const submitEvent = new Event('submit', {cancelable: true});
    textForm.dispatchEvent(submitEvent);
  }
});

textInput.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    e.preventDefault();
    const start = textInput.selectionStart;
    const end = textInput.selectionEnd;

    // Insert 2 spaces at the current cursor position
    textInput.value = textInput.value.substring(0, start) + '  ' + textInput.value.substring(end);

    // Set the cursor position after the inserted spaces
    textInput.selectionStart = textInput.selectionEnd = start + 2;
  }
});

document.addEventListener("DOMContentLoaded", function() {
    const textInput = document.getElementById("text-input");
    const sendBtn = document.getElementById("sendBtn");
    const uploadBtn = document.getElementById("uploadBtn");

    textInput.addEventListener("input", function() {
        const isInputEmpty = textInput.value.trim() === "";
        sendBtn.disabled = isInputEmpty;
        uploadBtn.disabled = isInputEmpty;
    });
});



document.addEventListener('keydown', (event) => {
  const textInput = document.getElementById('text-input');
  const startBtn = document.getElementById('startBtn');
  const stopBtn = document.getElementById('stopBtn');

  // Check if the spacebar was pressed and if the target was not the text input
  if (event.code === 'Space' && event.target !== textInput) {
    event.preventDefault(); // Prevent the default behavior of the spacebar

    // Simulate the click on either StartBtn or StopBtn depending on which one is not disabled
    if (!startBtn.disabled) {
      startBtn.click();
    } else if (!stopBtn.disabled) {
      stopBtn.click();
    }
  }
});


// This shit works confirmed, but does not usefully render code blocks
socket.on('receive_transcription', (transcribed_text) => {
    // Create and append the user-text paragraph to the received-text container
    const userText = document.createElement('p');
    const avatar = document.createElement('img');
    avatar.src = 'http://occ-0-999-1001.1.nflxso.net/dnm/api/v6/K6hjPJd6cR6FpVELC5Pd6ovHRSk/AAAABWHxaOxUNqEupjwCw-M9tgFfGFlQ22EjoG2ZYC1FsjjAWSdxOIfjdifW-rJrpNaLzTC0rpsRhE7DoH8h2zWxIQXEKaAsFUuDO2yl.png?r=2b1)';
    avatar.className = 'user-avatar';
    userText.appendChild(avatar);
    userText.appendChild(document.createTextNode(transcribed_text));
    userText.className = 'user-text';
    receivedText.appendChild(userText);

    socket.emit('send_text', transcribed_text);
    textInput.value = '';
    textInput.disabled = true;
    processingIndicator.style.display = 'block';
    receivedText.scrollTop = receivedText.scrollHeight;

});


let inCodeBlock = false;
let codeLanguage = '';
let codeBlock;

socket.on('receive_word', (word) => {

    // Check if the user is near the bottom of the receivedText container
    const isNearBottom = receivedText.scrollTop + receivedText.clientHeight >= receivedText.scrollHeight - 50;

    if (word.startsWith('```')) {
        if (!inCodeBlock) {
            inCodeBlock = true;
            codeLanguage = word.slice(3).trim();
            const codeBlock = document.createElement('pre');
            codeBlock.height = 'auto'
            codeElement = document.createElement('code');
            codeElement.className = `language-${codeLanguage}`;
            codeBlock.appendChild(codeElement);
            receivedText.appendChild(codeBlock);
            // Prism.highlightElement(codeElement);
        } else {
            inCodeBlock = false;
            Prism.highlightElement(codeElement);
        }
        return;
    }

    if (inCodeBlock) {
        codeElement.textContent += word;
        Prism.highlightElement(codeElement);

    } else {
        const lastElem = receivedText.lastElementChild;
        const lastServerTextSpan = lastElem && lastElem.querySelector('.server-text-content');

        if (lastServerTextSpan && lastElem.className === 'server-text') {
            lastServerTextSpan.textContent += word;
        } else {
            const serverText = document.createElement('p');

            if (!lastElem || lastElem.className !== 'server-text') {
                const avatar = document.createElement('img');
                avatar.src = 'https://thumbs.dreamstime.com/z/cute-cartoon-robot-head-creative-illustrated-149232864.jpg'
                avatar.className = 'server-avatar';
                serverText.appendChild(avatar);
            }

            const serverTextSpan = document.createElement('span');
            serverTextSpan.textContent = word;
            serverTextSpan.className = 'server-text-content';
            serverText.appendChild(serverTextSpan);

            serverText.className = 'server-text';
            receivedText.appendChild(serverText);
        }
    }
    if (isNearBottom) {
        receivedText.scrollTop = receivedText.scrollHeight;
    }

});



socket.on('processing_done', () => {
    processingIndicator.style.display = 'none';
    const newline = document.createElement('br');
    receivedText.appendChild(newline);
    receivedText.scrollTop = receivedText.scrollHeight;
    textInput.disabled = false;
    // textInput.focus();
});

// This from the parent index, for audio processing
let startBtn = document.getElementById('startBtn');
let stopBtn = document.getElementById('stopBtn');
let recorder;

startBtn.onclick = function() {
    navigator.mediaDevices.getUserMedia({audio: true}).then(stream => {
        recorder = new RecordRTC(stream, {type: 'audio'});
        recorder.startRecording();
        startBtn.disabled = true;
        stopBtn.disabled = false;
    });
};

stopBtn.onclick = function() {
    recorder.stopRecording(() => {
        let formData = new FormData();
        formData.append('audio_data', recorder.getBlob());
        fetch('http://localhost:5000/upload_audio', {method: 'POST', body: formData}).then(response => {
            if (response.ok) {
                console.log('Audio file uploaded successfully');
            } else {
                console.log('Error uploading the audio file');
            }
        });
        startBtn.disabled = false;
        stopBtn.disabled = true;
        // get transcription from server, fill the input bar with this
        // Request words from the server
    });
};

const sendBtn = document.getElementById("sendBtn");
const uploadBtn = document.getElementById("uploadBtn");


sendBtn.onclick = function() {
    const submitEvent = new Event('submit', {cancelable: true});
    textForm.dispatchEvent(submitEvent);
};


uploadBtn.onclick = function() {
    const uploadEvent = new Event('upload', {cancelable: true});
    textForm.dispatchEvent(uploadEvent);
};