
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;
const currentTheme = localStorage.getItem('theme') || 'light';
html.classList.toggle('dark', currentTheme === 'dark');

themeToggle.addEventListener('click', () => {
    html.classList.toggle('dark');
    const isDark = html.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

const contentCards = document.querySelectorAll('.content-card');
contentCards.forEach((card, index) => {
    card.style.animationDelay = `${index * 200}ms`;
});

function editTurfName() {
    const nameElement = document.getElementById('turf-name');
    const currentText = nameElement.querySelector('span').textContent;

    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentText;
    input.className = 'edit-input text-3xl md:text-4xl font-bold bg-gradient-to-r from-emerald-600 via-teal-500 to-green-500 bg-clip-text text-transparent';

    nameElement.innerHTML = '';
    nameElement.appendChild(input);
    input.focus();

    input.addEventListener('blur', saveTurfName);
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            saveTurfName();
        }
    });
}

function editPrice(priceId) {
    const oldSpan = document.getElementById(priceId);
    const turfId = oldSpan.dataset.turfId;
    const field = oldSpan.dataset.field;
    const current = oldSpan.textContent;

    const input = document.createElement('input');
    input.type = 'text';
    input.value = current;
    // carry over the identifiers
    input.dataset.turfId = turfId;
    input.dataset.field = field;
    input.className = 'edit-input text-emerald-600 dark:text-emerald-400 font-bold text-lg w-24';

    oldSpan.replaceWith(input);
    input.focus();

    input.addEventListener('blur', () => savePrice(priceId, input));
    input.addEventListener('keypress', e => {
        if (e.key === 'Enter') savePrice(priceId, input);
    });
}

function editTurfAddress() {
    const addressElement = document.getElementById('turf-address');
    const currentText = addressElement.textContent.replace('📍 ', '');

    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentText;
    input.className = 'edit-input text-lg text-gray-700 dark:text-gray-300';

    addressElement.innerHTML = '📍 ';
    addressElement.appendChild(input);
    input.focus();

    input.addEventListener('blur', saveTurfAddress);
    input.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            saveTurfAddress();
        }
    });
}

function saveTurfAddress() {
    const addressElement = document.getElementById('turf-address');
    const input = addressElement.querySelector('input');
    const newText = input.value.trim() || '123 Sports Avenue, Downtown City';

    addressElement.textContent = `📍 ${newText}`;
}

function editPrice(priceId) {
    const oldSpan = document.getElementById(priceId);
    const turfId = oldSpan.dataset.turfId;
    const field = oldSpan.dataset.field;
    const current = oldSpan.textContent;

    const input = document.createElement('input');
    input.type = 'text';
    input.value = current;
    input.dataset.turfId = turfId;
    input.dataset.field = field;
    input.className = 'edit-input text-emerald-600 dark:text-emerald-400 font-bold text-lg w-24';

    oldSpan.replaceWith(input);
    input.focus();

    // Use keydown here so Enter is always caught
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter') {
            e.preventDefault();
            savePrice(priceId, input);
        }
    });
    // And still save on blur
    input.addEventListener('blur', () => savePrice(priceId, input));
}

function savePrice(priceId, input) {
    const newText = input.value.trim() || '0';
    const numeric = extractNumber(newText);

    console.log('Parsed numeric:', numeric, 'from raw:', newText);

    const turfId = input.dataset.turfId;
    const field = input.dataset.field;
    if (!turfId || !field) {
        alert('Internal error: missing identifiers.');
        return;
    }

    fetch(`/api/turf/${turfId}/price`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field, value: numeric })
    })
        .then(async res => {
            const text = await res.text();
            let data;
            try { data = JSON.parse(text); }
            catch (e) { throw new Error('Invalid JSON returned: ' + text); }

            if (!res.ok) {
                throw new Error(data.message || `HTTP ${res.status}`);
            }
            return data;
        })
        .then(data => {
            // rebuild the <span> with the DB‐confirmed price
            const span = document.createElement('span');
            span.id = priceId;
            span.dataset.turfId = turfId;
            span.dataset.field = field;
            span.className = 'text-emerald-600 dark:text-emerald-400 font-bold text-lg';
            span.textContent = `₹${data.new}/hr`;
            input.replaceWith(span);
        })
        .catch(err => {
            console.error('Error saving price:', err);
            alert('Could not save price. Try again.\n' + err.message);
            // optionally revert to original span here
        });
}

function extractNumber(str) {
    const m = str.match(/(\d+(\.\d+)?)/);
    return m ? parseFloat(m[1]) : 0;
}


// Add images
document.getElementById('add-images-btn').addEventListener('click', () => {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.multiple = true;
    fileInput.style.display = 'none';

    fileInput.addEventListener('change', function (e) {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    showSuccessMessage('Images uploaded successfully!');
                };
                reader.readAsDataURL(file);
            }
        });
    });

    document.body.appendChild(fileInput);
    fileInput.click();
    document.body.removeChild(fileInput);
});

function showSuccessMessage(message) {
    const successMsg = document.createElement('div');
    successMsg.className = 'fixed top-20 right-6 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm';
    successMsg.textContent = message;
    document.body.appendChild(successMsg);

    setTimeout(() => {
        successMsg.remove();
    }, 3000);
}