document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chat-messages');
  const chatInput    = document.getElementById('chat-input');
  const sendButton   = document.getElementById('send-message');

  // helper to render a message bubble
  function appendMessage({ username, text, timestamp, isSelf }) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('flex', 'items-start', 'space-x-3');
    if (isSelf) wrapper.classList.add('justify-end');

    const avatarDiv = document.createElement('div');
    avatarDiv.className =
      'w-8 h-8 bg-gradient-to-r from-emerald-400 to-teal-400 ' +
      'rounded-full flex items-center justify-center text-white font-bold text-sm';
    avatarDiv.textContent = username.charAt(0).toUpperCase();

    const messageContainer = document.createElement('div');
    const bubble = document.createElement('div');
    bubble.className = isSelf
      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl px-4 py-2 text-white'
      : 'bg-white/20 dark:bg-gray-700/20 rounded-2xl px-4 py-2';
    bubble.textContent = text;

    const meta = document.createElement('span');
    meta.className = isSelf
      ? 'text-xs text-gray-500 dark:text-gray-400 mt-1 block text-right'
      : 'text-xs text-gray-500 dark:text-gray-400 mt-1';
    meta.textContent = `${isSelf ? 'You' : username} · ${timestamp}`;

    messageContainer.appendChild(bubble);
    messageContainer.appendChild(meta);

    if (isSelf) {
      wrapper.appendChild(messageContainer);
      wrapper.appendChild(avatarDiv);
    } else {
      wrapper.appendChild(avatarDiv);
      wrapper.appendChild(messageContainer);
    }

    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // 1️⃣ Load existing messages on page load
  async function loadMessages() {
    try {
      const response = await fetch(`/api/matches/${matchId}/messages`);
      if (!response.ok) throw new Error('Failed to load messages');
      const messages = await response.json();

      messages.forEach(msg => {
        const ts = new Date(msg.timestamp);
        const timeString = ts.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
        appendMessage({
          username: msg.username,
          text:     msg.text,
          timestamp: timeString,
          isSelf:   msg.username === currentUser
        });
      });
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  }

  // 2️⃣ Send a new message and append it immediately
  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // clear input immediately
    chatInput.value = '';

    // generate a local timestamp for immediate display
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });

    // optimistic append
    appendMessage({
      username:  currentUser,
      text,
      timestamp: timeString,
      isSelf:    true
    });

    try {
      const response = await fetch(`/api/matches/${matchId}/messages`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ text })
      });
      if (!response.ok) throw new Error('Failed to send message');
      const data = await response.json();
      console.log('Message sent and stored:', data);
      // (Optionally) you could update that bubble’s timestamp if your server adds a slightly different one,
      // or just leave the optimistic timestamp.
    } catch (error) {
      console.error('Error sending message:', error);
      // Optionally: remove the optimistic bubble or show a warning
    }
  }

  // wire up UI events
  sendButton.addEventListener('click', sendMessage);
  chatInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  });

  // initialize
  loadMessages();
});
