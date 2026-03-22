document.addEventListener('DOMContentLoaded', () => {
    // --- Audio System Setup ---
    let audioContext;
    let droneOscillators = [];
    let isAudioStarted = false;

    // Initialize Audio Context on first interaction
    function initAudio() {
        if (isAudioStarted) return;
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();

        // create a dark synth drone
        const frequencies = [55, 110, 165]; // A1, A2, E3
        frequencies.forEach(freq => {
            const osc = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            osc.type = 'sawtooth';
            osc.frequency.value = freq;

            // Low volume, ambient
            gainNode.gain.value = 0.05;

            // Filter to make it darker
            const filter = audioContext.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.value = 400;

            osc.connect(filter);
            filter.connect(gainNode);
            gainNode.connect(audioContext.destination);

            osc.start();
            droneOscillators.push({ osc, gain: gainNode });
        });
        isAudioStarted = true;
    }


    // --- Upside Down Toggle Logic ---
    const gateToggle = document.getElementById('gate-toggle');
    const upsideDownContent = document.querySelector('.upside-down-content');
    const body = document.body;
    const headerTitle = document.querySelector('.title-box h1');

    gateToggle.addEventListener('click', () => {
        initAudio(); // Start audio on first click

        // Play static sound effect
        if (audioContext) {
            playStaticSound();
        }

        // Toggle the visual state
        body.classList.toggle('upside-down-mode');
        upsideDownContent.classList.toggle('hidden');

        // Change button text
        if (body.classList.contains('upside-down-mode')) {
            gateToggle.textContent = 'CLOSE THE GATE!';
            headerTitle.style.color = '#ff0000'; // Make title redder
            gateToggle.style.borderColor = '#b620e0';
            gateToggle.style.color = '#b620e0';
            gateToggle.style.backgroundColor = '#000';

            // Pitch shift drone down
            if (droneOscillators.length) {
                droneOscillators.forEach(d => {
                    d.osc.frequency.rampToValueAtTime(d.osc.frequency.value * 0.8, audioContext.currentTime + 2);
                });
            }

        } else {
            gateToggle.textContent = 'OPEN THE GATE';
            headerTitle.style.color = ''; // Reset
            gateToggle.style.borderColor = '';
            gateToggle.style.color = '';
            gateToggle.style.backgroundColor = '';

            // Pitch shift drone up
            if (droneOscillators.length) {
                droneOscillators.forEach(d => {
                    d.osc.frequency.rampToValueAtTime(d.osc.frequency.value * 1.25, audioContext.currentTime + 2);
                });
            }
        }
    });

    function playStaticSound() {
        const bufferSize = audioContext.sampleRate * 0.5; // 0.5 seconds
        const buffer = audioContext.createBuffer(1, bufferSize, audioContext.sampleRate);
        const data = buffer.getChannelData(0);

        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }

        const noise = audioContext.createBufferSource();
        noise.buffer = buffer;
        const noiseGain = audioContext.createGain();
        noiseGain.gain.value = 0.1;

        noise.connect(noiseGain);
        noiseGain.connect(audioContext.destination);
        noise.start();
    }


    // --- Wall of Lights Logic ---
    const wallOverlay = document.getElementById('lights-overlay');
    const wallInput = document.getElementById('wall-input');

    // Define positions for A-Z (approximate based on image)
    // In a real app we'd map these precisely. Using grid-like approximation here.
    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const lightPositions = {};

    // Generate lights in DOM
    // Row 1: A-H
    // Row 2: I-Q
    // Row 3: R-Z
    alphabet.split('').forEach((char, index) => {
        const light = document.createElement('div');
        light.classList.add('light-bulb');
        light.id = `light-${char}`;

        // Rough positioning logic
        let top, left;
        if (index < 8) { // Row 1
            top = '30%';
            left = `${15 + (index * 10)}%`;
        } else if (index < 17) { // Row 2
            top = '50%';
            left = `${10 + ((index - 8) * 9)}%`;
        } else { // Row 3
            top = '70%';
            left = `${15 + ((index - 17) * 10)}%`;
        }

        light.style.top = top;
        light.style.left = left;

        // Random colors
        const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff'];
        light.style.color = colors[Math.floor(Math.random() * colors.length)];

        wallOverlay.appendChild(light);
        lightPositions[char] = light;
    });

    wallInput.addEventListener('input', (e) => {
        const text = e.target.value.toUpperCase();
        const lastChar = text.slice(-1);

        if (lastChar && lightPositions[lastChar]) {
            initAudio(); // Also init audio on typing
            flashLight(lastChar);
        }
    });

    function flashLight(char) {
        const light = lightPositions[char];
        if (!light) return;

        light.classList.add('active');

        // Play simple tone
        if (audioContext) {
            const osc = audioContext.createOscillator();
            const g = audioContext.createGain();
            osc.type = 'sine';
            // Simple mapping of A-Z to frequencies
            osc.frequency.value = 220 + (char.charCodeAt(0) - 65) * 20;

            g.gain.value = 0.1;
            g.gain.exponentialRampToValueAtTime(0.001, audioContext.currentTime + 0.5);

            osc.connect(g);
            g.connect(audioContext.destination);
            osc.start();
            osc.stop(audioContext.currentTime + 0.5);
        }

        setTimeout(() => {
            light.classList.remove('active');
        }, 500);
    }

});
