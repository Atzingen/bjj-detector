/* ============================================
   BJJ Detector — Detection Page JS
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initImageUpload();
    initCamera();
    initVideoUpload();
});

/* ---- TABS ---- */
function initTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('tab-btn--active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('tab-content--active'));
            tab.classList.add('tab-btn--active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('tab-content--active');
        });
    });
}

/* ---- IMAGE UPLOAD ---- */
function initImageUpload() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('preview-img');
    const btnDetect = document.getElementById('btn-detect');
    const resultImg = document.getElementById('result-img');
    const placeholder = document.getElementById('result-placeholder');
    const detectionsList = document.getElementById('detections-list');

    let selectedFile = null;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', e => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', e => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImageFile(file);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files[0]) handleImageFile(fileInput.files[0]);
    });

    function handleImageFile(file) {
        selectedFile = file;
        const url = URL.createObjectURL(file);
        preview.src = url;
        preview.hidden = false;
        dropzone.querySelector('.dropzone-content').style.display = 'none';
        btnDetect.disabled = false;

        // Reset results
        resultImg.hidden = true;
        placeholder.hidden = false;
        detectionsList.innerHTML = '';
    }

    btnDetect.addEventListener('click', async () => {
        if (!selectedFile) return;

        btnDetect.disabled = true;
        btnDetect.textContent = 'Analisando...';

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const res = await fetch('/api/detect', { method: 'POST', body: formData });
            const data = await res.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            resultImg.src = data.image;
            resultImg.hidden = false;
            placeholder.hidden = true;

            renderDetections(detectionsList, data.detections);
        } catch (err) {
            alert('Erro ao processar imagem: ' + err.message);
        } finally {
            btnDetect.disabled = false;
            btnDetect.textContent = 'Detectar Posicoes';
        }
    });
}

/* ---- CAMERA ---- */
function initCamera() {
    const btnStart = document.getElementById('btn-start-camera');
    const btnCapture = document.getElementById('btn-capture');
    const video = document.getElementById('camera-feed');
    const canvas = document.getElementById('camera-canvas');
    const resultImg = document.getElementById('camera-result-img');
    const placeholder = document.getElementById('camera-result-placeholder');
    const detectionsList = document.getElementById('camera-detections-list');

    let stream = null;

    btnStart.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
            });
            video.srcObject = stream;
            btnStart.hidden = true;
            btnCapture.hidden = false;
        } catch (err) {
            alert('Nao foi possivel acessar a camera: ' + err.message);
        }
    });

    btnCapture.addEventListener('click', async () => {
        if (!stream) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);

        btnCapture.disabled = true;
        btnCapture.textContent = 'Analisando...';

        canvas.toBlob(async blob => {
            const formData = new FormData();
            formData.append('image', blob, 'capture.jpg');

            try {
                const res = await fetch('/api/detect', { method: 'POST', body: formData });
                const data = await res.json();

                resultImg.src = data.image;
                resultImg.hidden = false;
                placeholder.hidden = true;

                renderDetections(detectionsList, data.detections);
            } catch (err) {
                alert('Erro: ' + err.message);
            } finally {
                btnCapture.disabled = false;
                btnCapture.textContent = 'Capturar e Detectar';
            }
        }, 'image/jpeg', 0.9);
    });
}

/* ---- VIDEO ---- */
function initVideoUpload() {
    const dropzone = document.getElementById('video-dropzone');
    const fileInput = document.getElementById('video-input');
    const preview = document.getElementById('video-preview');
    const btnDetect = document.getElementById('btn-detect-video');
    const skipRange = document.getElementById('skip-frames');
    const skipVal = document.getElementById('skip-frames-val');
    const progressBar = document.getElementById('video-progress');
    const progressFill = document.getElementById('video-progress-fill');
    const progressText = document.getElementById('video-progress-text');
    const resultVideo = document.getElementById('video-result');
    const placeholder = document.getElementById('video-result-placeholder');
    const detectionsList = document.getElementById('video-detections-list');

    let selectedFile = null;

    skipRange.addEventListener('input', () => {
        const skip = parseInt(skipRange.value);
        skipVal.textContent = `Processar 1 a cada ${skip + 1} frames`;
    });

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', e => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', e => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('video/')) {
            handleVideoFile(file);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files[0]) handleVideoFile(fileInput.files[0]);
    });

    function handleVideoFile(file) {
        selectedFile = file;
        const url = URL.createObjectURL(file);
        preview.src = url;
        preview.hidden = false;
        dropzone.querySelector('.dropzone-content').style.display = 'none';
        btnDetect.disabled = false;
    }

    btnDetect.addEventListener('click', async () => {
        if (!selectedFile) return;

        btnDetect.disabled = true;
        progressBar.hidden = false;
        progressFill.style.width = '0%';
        progressText.textContent = 'Enviando video...';

        const formData = new FormData();
        formData.append('video', selectedFile);
        formData.append('skip_frames', skipRange.value);

        // Simulate progress during upload
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + 2, 90);
            progressFill.style.width = `${progress}%`;
            if (progress > 10) progressText.textContent = 'Processando frames...';
        }, 500);

        try {
            const res = await fetch('/api/detect-video', { method: 'POST', body: formData });
            clearInterval(progressInterval);
            progressFill.style.width = '100%';
            progressText.textContent = 'Concluido!';

            const data = await res.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            resultVideo.src = data.video;
            resultVideo.hidden = false;
            placeholder.hidden = true;

            // Show detection summary
            const summary = {};
            (data.detections || []).forEach(frame => {
                frame.detections.forEach(d => {
                    if (!summary[d.label]) summary[d.label] = { count: 0, maxConf: 0 };
                    summary[d.label].count++;
                    summary[d.label].maxConf = Math.max(summary[d.label].maxConf, d.confidence);
                });
            });

            const summaryList = Object.entries(summary)
                .sort((a, b) => b[1].count - a[1].count)
                .map(([label, info]) => ({
                    label,
                    confidence: info.maxConf,
                    extra: `${info.count} deteccoes`,
                }));

            renderDetections(detectionsList, summaryList, true);

        } catch (err) {
            clearInterval(progressInterval);
            alert('Erro ao processar video: ' + err.message);
        } finally {
            btnDetect.disabled = false;
            setTimeout(() => { progressBar.hidden = true; }, 2000);
        }
    });
}

/* ---- RENDER DETECTIONS ---- */
function renderDetections(container, detections, isVideoSummary = false) {
    container.innerHTML = '';

    if (!detections || detections.length === 0) {
        container.innerHTML = '<div class="detection-item"><span class="detection-label">Nenhuma posicao detectada</span></div>';
        return;
    }

    detections.forEach(d => {
        const item = document.createElement('div');
        item.className = 'detection-item';

        const label = d.label || d.class;
        const conf = d.confidence;

        item.innerHTML = `
            <div>
                <span class="detection-label">${label}</span>
                ${isVideoSummary && d.extra ? `<br><small style="color: var(--gray-500)">${d.extra}</small>` : ''}
            </div>
            <span class="detection-conf">${conf}%</span>
        `;
        container.appendChild(item);
    });
}
