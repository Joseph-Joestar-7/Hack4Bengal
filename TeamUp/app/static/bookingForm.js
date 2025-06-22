// Global state


let timeSlots = [
    { id: '1', startTime: '00:00', endTime: '01:00', selected: false },
    { id: '2', startTime: '01:00', endTime: '02:00', selected: false },
    { id: '3', startTime: '02:00', endTime: '03:00', selected: false },
    { id: '4', startTime: '03:00', endTime: '04:00', selected: false },
    { id: '5', startTime: '04:00', endTime: '05:00', selected: false },
    { id: '6', startTime: '05:00', endTime: '06:00', selected: false },
    { id: '7', startTime: '06:00', endTime: '07:00', selected: false },
    { id: '8', startTime: '07:00', endTime: '08:00', selected: false },
    { id: '9', startTime: '08:00', endTime: '09:00', selected: false },
    { id: '10', startTime: '09:00', endTime: '10:00', selected: false },
    { id: '11', startTime: '10:00', endTime: '11:00', selected: false },
    { id: '12', startTime: '11:00', endTime: '12:00', selected: false },
    { id: '13', startTime: '12:00', endTime: '13:00', selected: false },
    { id: '14', startTime: '13:00', endTime: '14:00', selected: false },
    { id: '15', startTime: '14:00', endTime: '15:00', selected: false },
    { id: '16', startTime: '15:00', endTime: '16:00', selected: false },
    { id: '17', startTime: '16:00', endTime: '17:00', selected: false },
    { id: '18', startTime: '17:00', endTime: '18:00', selected: false },
    { id: '19', startTime: '18:00', endTime: '19:00', selected: false },
    { id: '20', startTime: '19:00', endTime: '20:00', selected: false },
    { id: '21', startTime: '20:00', endTime: '21:00', selected: false },
    { id: '22', startTime: '21:00', endTime: '22:00', selected: false },
    { id: '23', startTime: '22:00', endTime: '23:00', selected: false },
    { id: '24', startTime: '23:00', endTime: '00:00', selected: false }

];

let selectedSlots = [];
let totalHours = 0;
let totalAmount = 0;

// DOM elements
const darkModeToggle = document.getElementById('darkModeToggle');
const timeSlotsGrid = document.getElementById('timeSlotsGrid');
const bookingSummary = document.getElementById('bookingSummary');
const proceedPaymentBtn = document.getElementById('proceedPayment');
const confirmBookingBtn = document.getElementById('confirmBooking');
const gameSelect = document.getElementById('gameType');
const bookDate = document.getElementById('bookingDate');

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    initializeTimeSlots();
    setupEventListeners();
    updateBookingSummary();
    updatePaymentButton();
    onGameTypeChange();
    getturfId();
});

function getturfId() {
    const turfID = confirmBookingBtn.dataset.turfId;
    handleConfirmBooking(turfID);
}

function onGameTypeChange() {
    const ds = gameSelect.dataset;
    const sel = gameSelect.value;
    if (sel === 'Cricket') pricePerHour = parseFloat(ds.cricketPrice);
    else if (sel === 'Football') pricePerHour = parseFloat(ds.footballPrice);
    else if (sel === 'Tennis') pricePerHour = parseFloat(ds.tennisPrice);

    totalAmount = totalHours * pricePerHour;
    updateBookingSummary();
}

// Setup event listeners
function setupEventListeners() {
    // Dark mode toggle
    darkModeToggle.addEventListener('click', toggleDarkMode);

    
    gameSelect.addEventListener('change', onGameTypeChange);

    bookDate.addEventListener('change', (e) => {
        window.location.reload();
    })
    // Payment method change
    document.querySelectorAll('input[name="payment"]').forEach(radio => {
        radio.addEventListener('change', updatePaymentButton);
    });

    // Proceed payment button
    proceedPaymentBtn.addEventListener('click', handleProceedPayment);

    // Confirm booking button
    confirmBookingBtn.addEventListener('click', getturfId);
    //confirmBookingBtn.addEventListener('click', handleConfirmBooking);
}

// Initialize time slots in the grid
function initializeTimeSlots() {
    timeSlotsGrid.innerHTML = '';
    timeSlots.forEach(slot => {
        const slotElement = document.createElement('button');
        slotElement.className = 'time-slot';
        slotElement.dataset.slotId = slot.id;
        slotElement.textContent = `${slot.startTime} - ${slot.endTime}`;

        if (slot.selected) {
            slotElement.classList.add('selected');
        }

        slotElement.addEventListener('click', () => handleTimeSlotSelection(slot.id));
        timeSlotsGrid.appendChild(slotElement);
    });
}

// Handle time slot selection
function handleTimeSlotSelection(slotId) {
    // Toggle the selected state
    timeSlots = timeSlots.map(slot => {
        if (slot.id === slotId) {
            return { ...slot, selected: !slot.selected };
        }
        return slot;
    });

    // Get currently selected slots
    const currentlySelected = timeSlots.filter(slot => slot.selected);

    // Validate consecutive slots
    if (currentlySelected.length > 0 && !validateConsecutiveSlots(currentlySelected)) {
        // Reset all selections if not consecutive
        timeSlots = timeSlots.map(slot => ({ ...slot, selected: false }));
        selectedSlots = [];
        totalHours = 0;
        totalAmount = 0;
        alert('Please select consecutive time slots only!');
    } else {
        selectedSlots = currentlySelected;
        totalHours = selectedSlots.length;
        totalAmount = totalHours * pricePerHour;
    }

    // Update UI
    initializeTimeSlots();
    updateBookingSummary();
    updateButtonStates();
}

// Validate that selected slots are consecutive
function validateConsecutiveSlots(slots) {
    if (slots.length <= 1) return true;

    // Sort slots by start time
    const sortedSlots = [...slots].sort((a, b) => {
        const aHour = parseInt(a.startTime.replace(/[^\d]/g, ''));
        const bHour = parseInt(b.startTime.replace(/[^\d]/g, ''));
        return aHour - bHour;
    });
    console.log(sortedSlots)
    // Check if slots are consecutive
    for (let i = 0; i < sortedSlots.length - 1; i++) {
        const currentEndHour = parseInt(sortedSlots[i].endTime.split(':')[0]);
        const nextStartHour = parseInt(sortedSlots[i + 1].startTime.split(':')[0]);

        if (Math.abs(currentEndHour - nextStartHour) > 0) {
            return false;
        }
    }
    return true;
}

// Get booking time range string
function getBookingTimeRange() {
    if (selectedSlots.length === 0) return '';

    const sortedSlots = [...selectedSlots].sort((a, b) => {
        const aHour = parseInt(a.startTime.replace(/[^\d]/g, ''));
        const bHour = parseInt(b.startTime.replace(/[^\d]/g, ''));
        return aHour - bHour;
    });

    return `${sortedSlots[0].startTime} - ${sortedSlots[sortedSlots.length - 1].endTime}`;
}

// Update booking summary display
function updateBookingSummary() {
    if (selectedSlots.length === 0) {
        bookingSummary.innerHTML = '<div class="no-selection">No time slots selected</div>';
    } else {
        bookingSummary.innerHTML = `
            <div class="booking-details show">
                <div class="booking-time">Time Slots: ${getBookingTimeRange()}</div>
                <div class="booking-hours">Total Hours: <span style="font-weight: 600;">${totalHours}</span></div>
                <div class="booking-total">Total Amount: ₹${totalAmount}</div>
            </div>
        `;
    }
}

// Update payment button text based on selected payment method
function updatePaymentButton() {
    const selectedPayment = document.querySelector('input[name="payment"]:checked').value;
    const buttonText = selectedPayment === 'online' ? 'Proceed to Payment' : 'Proceed to Confirmation';
    proceedPaymentBtn.textContent = buttonText;
}

// Update button states based on selection
function updateButtonStates() {
    const hasSelection = selectedSlots.length > 0;
    proceedPaymentBtn.disabled = !hasSelection;
    confirmBookingBtn.disabled = !hasSelection;
}

// Handle proceed to payment
function handleProceedPayment() {
    if (selectedSlots.length === 0) {
        alert('Please select at least one time slot!');
        return;
    }

    const selectedPayment = document.querySelector('input[name="payment"]:checked').value;

    if (selectedPayment === 'online') {
        alert('Redirecting to payment gateway...');
    } else {
        alert('Proceed with cash payment at the venue.');
    }
}

// Handle confirm booking
async function handleConfirmBooking(turfID) {
    if (selectedSlots.length === 0) {
        alert('Please select at least one time slot!');
        return;
    }
    
    const dateValue = bookDate.value;
    const slotIndices = selectedSlots.map(slot => parseInt(slot.id) - 1);

    const payload = {
        date: dateValue,
        slot_indices: slotIndices,
        game_type: gameSelect.value,
        payment_method: document.querySelector('input[name="payment"]:checked').value
    };
    if (!validateSlotIndices(slotIndices)) {
        alert('Invalid time slots selected');
        return;
    }
    
    try {
        const resp = await fetch(`/book/${turfID}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            credentials: 'same-origin'
        });

        // Handle non-JSON responses
        const contentType = resp.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await resp.text();
            throw new Error(`Server error: ${resp.status} - ${text}`);
        }

        const data = await resp.json();
        
        if (resp.ok) {
            alert('Booking confirmed!');
            window.location.reload();
        } else {
            alert(`Error: ${data.error || 'Unknown error'}`);
        }
    } catch (err) {
        console.error(err);
        alert(`Booking failed: ${err.message}`);
    }
}

function validateSlotIndices(indices) {
    return indices.every(idx => Number.isInteger(idx) && idx >= 0 && idx < 24);
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark');

    // Save preference to localStorage
    const isDark = document.body.classList.contains('dark');
    localStorage.setItem('darkMode', isDark);
}

// Load dark mode preference on page load
document.addEventListener('DOMContentLoaded', function () {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    if (savedDarkMode) {
        document.body.classList.add('dark');
    }
});
