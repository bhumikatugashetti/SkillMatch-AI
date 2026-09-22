/* ============================================================
   SKILLMATCH AI - INTERACTIVE CLIENT ENGINE
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    init3DTilt();
    initRadialGauges();
    initDropzones();
    initCounters();
});

/* ---------- 3D CARD MOUSE TILT EFFECT ---------- */
function init3DTilt() {
    const cards = document.querySelectorAll('.card-3d, .glass-panel');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = ((y - centerY) / centerY) * -6;
            const rotateY = ((x - centerX) / centerX) * 6;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        });
    });
}

/* ---------- RADIAL SCORE GAUGES ---------- */
function initRadialGauges() {
    const fillTracks = document.querySelectorAll('.radial-fill-track');
    
    fillTracks.forEach(track => {
        const score = parseFloat(track.getAttribute('data-score') || '0');
        const circumference = 565; // 2 * PI * r (r = 90)
        const offset = circumference - (score / 100) * circumference;
        
        setTimeout(() => {
            track.style.strokeDashoffset = offset;
        }, 200);
    });
}

/* ---------- DRAG AND DROP FILE UPLOADER ---------- */
function initDropzones() {
    const dropzones = document.querySelectorAll('.upload-dropzone');
    
    dropzones.forEach(zone => {
        const fileInput = zone.querySelector('.file-input-hidden');
        const fileLabel = zone.querySelector('.dropzone-filename');
        
        if (!fileInput) return;

        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.remove('dragover');
            }, false);
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files[0]) {
                const name = fileInput.files[0].name;
                if (fileLabel) {
                    fileLabel.textContent = `📄 Selected File: ${name}`;
                    fileLabel.style.color = '#00f2fe';
                    fileLabel.style.fontWeight = '700';
                }
            }
        });
    });
}

/* ---------- ANIMATED STAT COUNTERS ---------- */
function initCounters() {
    const counters = document.querySelectorAll('.stat-number[data-target]');
    
    counters.forEach(counter => {
        const target = parseFloat(counter.getAttribute('data-target') || '0');
        const isFloat = counter.getAttribute('data-float') === 'true';
        let current = 0;
        const increment = target / 30;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.innerText = isFloat ? current.toFixed(2) : Math.ceil(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.innerText = isFloat ? target.toFixed(2) : target;
            }
        };
        
        updateCounter();
    });
}