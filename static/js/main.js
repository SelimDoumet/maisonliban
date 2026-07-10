// ─── CHAT WIDGET ───
let chatHistory = [];

function toggleChat() {
  const win = document.getElementById('chatWindow');
  win.classList.toggle('open');
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const messages = document.getElementById('chatMessages');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';

  // User bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-msg user';
  userBubble.textContent = text;
  messages.appendChild(userBubble);
  chatHistory.push({ role: 'user', content: text });

  // Typing indicator
  const typing = document.createElement('div');
  typing.className = 'chat-msg assistant typing';
  typing.textContent = 'Thinking...';
  messages.appendChild(typing);
  messages.scrollTop = messages.scrollHeight;

  try {
    const res = await fetch('/ai-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, history: chatHistory })
    });
    const data = await res.json();
    const reply = data.reply || 'Sorry, something went wrong.';
    typing.remove();

    const botBubble = document.createElement('div');
    botBubble.className = 'chat-msg assistant';
    botBubble.textContent = reply;
    messages.appendChild(botBubble);
    chatHistory.push({ role: 'assistant', content: reply });
  } catch {
    typing.textContent = 'Connection error. Please try again.';
  }

  messages.scrollTop = messages.scrollHeight;
}

// Auto-dismiss flash messages after 4s
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => el.remove(), 4000);
});
