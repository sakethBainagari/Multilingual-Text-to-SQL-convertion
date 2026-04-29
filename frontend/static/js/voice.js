/* ==========================================================
   voice.js – Web Speech API integration with browser fallback
   ========================================================== */

let recognition = null;
let isRecording = false;
let voiceTranscript = '';

function initializeVoiceRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SR) {
        console.warn('Web Speech API not supported');
        const btn = document.getElementById('micButton');
        if (btn) { btn.disabled = true; btn.title = 'Voice not supported – use Chrome or Edge'; }
        const help = document.querySelector('.voice-help');
        if (help) help.innerHTML = '<strong>⚠️ Voice Input Not Available</strong> Use Chrome or Edge for voice features.';
        return;
    }

    recognition = new SR();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = document.getElementById('languageSelector').value;

    recognition.onstart = () => { isRecording = true; updateVoiceUI('listening'); };

    recognition.onresult = (event) => {
        let interim = '', final = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const t = event.results[i][0].transcript;
            if (event.results[i].isFinal) final += t + ' '; else interim += t;
        }
        if (interim) {
            const el = document.getElementById('voiceTranscript');
            el.textContent = '🎙️ Listening: ' + interim;
            el.style.display = 'block';
        }
        if (final) {
            voiceTranscript += final;
            document.getElementById('naturalQuery').value = voiceTranscript.trim();
            document.getElementById('voiceTranscript').textContent = '✅ Recognized: ' + voiceTranscript.trim();
        }
    };

    recognition.onerror = (event) => {
        isRecording = false;
        const msgs = {
            'no-speech': 'No speech detected.',
            'audio-capture': 'Microphone not found.',
            'not-allowed': 'Microphone permission denied.',
            'network': 'Network error.',
        };
        updateVoiceUI('error', msgs[event.error] || `Error: ${event.error}`);
        setTimeout(() => updateVoiceUI('idle'), 3000);
    };

    recognition.onend = () => {
        isRecording = false;
        if (voiceTranscript.trim()) {
            updateVoiceUI('success', '✅ Voice input complete!');
        } else {
            updateVoiceUI('idle');
        }
        setTimeout(() => { if (!isRecording) { const s = document.getElementById('voiceStatus'); if (s) s.style.display = 'none'; } }, 3000);
    };
}

function toggleVoiceRecognition() {
    if (!recognition) { alert('Voice recognition not available. Use Chrome or Edge.'); return; }
    if (isRecording) {
        recognition.stop();
        isRecording = false;
        updateVoiceUI('processing', 'Processing your speech...');
    } else {
        voiceTranscript = '';
        document.getElementById('naturalQuery').value = '';
        document.getElementById('voiceTranscript').style.display = 'none';
        try { recognition.start(); } catch (e) { alert('Could not start voice recognition.'); }
    }
}

function onLanguageChange() {
    const lang = document.getElementById('languageSelector').value;
    if (recognition) recognition.lang = lang;
    if (isRecording) {
        recognition.stop();
        setTimeout(() => { voiceTranscript = ''; document.getElementById('naturalQuery').value = ''; recognition.start(); }, 100);
    }
    const examples = {
        'te-IN': 'ఉదా: "నాకు డిపార్ట్‌మెంట్ వారీగా సగటు జీతం చూపించు"',
        'hi-IN': 'उदाहरण: "मुझे विभाग के अनुसार औसत वेतन दिखाएं"',
        'en-US': 'Example: "Show me average salary by department"',
    };
    showMessage(`Language changed. ${examples[lang] || ''}`, 'info');
}

function updateVoiceUI(state, message) {
    const btn = document.getElementById('micButton');
    const status = document.getElementById('voiceStatus');
    btn.classList.remove('recording', 'processing');
    status.classList.remove('listening', 'processing', 'success');

    switch (state) {
        case 'listening':
            btn.classList.add('recording'); btn.textContent = '🔴'; btn.title = 'Click to stop';
            status.textContent = '🎙️ Listening...'; status.classList.add('listening'); status.style.display = 'inline-block'; break;
        case 'processing':
            btn.classList.add('processing'); btn.textContent = '⏸️';
            status.textContent = message || '⏳ Processing...'; status.classList.add('processing'); status.style.display = 'inline-block'; break;
        case 'success':
            btn.textContent = '🎤'; btn.title = 'Click to start voice input';
            status.textContent = message || '✅ Done!'; status.classList.add('success'); status.style.display = 'inline-block'; break;
        case 'error':
            btn.textContent = '🎤'; btn.title = 'Click to start voice input';
            status.textContent = message || '❌ Error'; status.style.display = 'inline-block'; break;
        default:
            btn.textContent = '🎤'; btn.title = 'Click to start voice input'; status.style.display = 'none'; break;
    }
}
