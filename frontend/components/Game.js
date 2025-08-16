'use client';
import { useState, useRef, useEffect } from 'react';
import { audioController } from '../components/AudioController';
import styles from '@/styles/Home.module.css';

// Split narration into coherent chunks without breaking quotes
function splitNarration(text, maxChars = 200) {
  const chunks = [];
  let currentChunk = '';
  const sentences = text.match(/[^.!?]+[.!?]+["']?|.+$/g) || [];

  for (let sentence of sentences) {
    sentence = sentence.trim();
    if ((currentChunk + ' ' + sentence).length > maxChars) {
      if (currentChunk) chunks.push(currentChunk.trim());
      currentChunk = sentence;
    } else {
      currentChunk = currentChunk ? currentChunk + ' ' + sentence : sentence;
    }
  }
  if (currentChunk) chunks.push(currentChunk.trim());
  return chunks;
}

// Animate DM narration letter-by-letter
async function addNarrationAnimated(setMessages, narration, setTyping) {
  const chunks = splitNarration(narration, 200);

  for (let chunk of chunks) {
    setTyping(true);
    setMessages((msgs) => [...msgs, { role: 'dm', text: '' }]);
    let displayedText = '';

    for (let i = 0; i < chunk.length; i++) {
      displayedText += chunk[i];
      setMessages((msgs) => {
        const newMsgs = [...msgs];
        newMsgs[newMsgs.length - 1].text = displayedText;
        return newMsgs;
      });
      await new Promise((r) => setTimeout(r, 50)); // typing speed
    }

    await new Promise((r) => setTimeout(r, 1500)); // pause between chunks
  }
  setTyping(false);
}

export function ChatGame() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [playerId, setPlayerId] = useState(null);
  const [stage, setStage] = useState('askName');
  const [isTyping, setIsTyping] = useState(false);
  const [sending, setSending] = useState(false);
  const historyRef = useRef(null);

  // Initial DM message
  useEffect(() => {
    addNarrationAnimated(
      setMessages,
      "Welcome, adventurer! Type your name to start your journey.",
      setIsTyping
    );
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [messages]);

  const sendNameAndStart = async () => {
    if (!input.trim() || sending) return;
    setSending(true);
    try {
      const res = await fetch('http://localhost:8000/start_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: input }),
      });
      const data = await res.json();
      setPlayerId(data.player_id);
      setInput('');
      audioController.play(data.scene_audio || 'exploration_travel');
      setStage('play');
      await addNarrationAnimated(setMessages, data.narration, setIsTyping);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const sendTurn = async () => {
    if (!input.trim() || sending) return;
    setSending(true);
    const playerMessage = input;
    setMessages((msgs) => [...msgs, { role: 'player', text: playerMessage }]);
    setInput('');
    try {
      const res = await fetch('http://localhost:8000/play_turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_id: playerId, input_text: playerMessage }),
      });
      const data = await res.json();
      audioController.play(data.scene_audio || 'exploration_travel');
      await addNarrationAnimated(setMessages, data.narration, setIsTyping);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    stage === 'askName' ? sendNameAndStart() : sendTurn();
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>DungeonDM</div>
      <div className={styles.chatHistory} ref={historyRef}>
        {messages.map((m, i) => (
          <div
            key={i}
            className={`${styles.message} ${m.role === 'dm' ? styles.dm : styles.user}`}
          >
            <span className={styles.avatar}>
              {m.role === 'dm' ? '📜' : '🧝'}
            </span>
            <strong>{m.role === 'dm' ? 'DM' : 'You'}:</strong> {m.text}
          </div>
        ))}
        {isTyping && (
          <div className={`${styles.message} ${styles.dm}`}>
            <span className={styles.avatar}>📜</span>
            <strong>DM:</strong> <em>is typing...</em>
          </div>
        )}
      </div>
      <form className={styles.chatInput} onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={stage === 'askName' ? 'Enter your name...' : 'What do you do?'}
          disabled={isTyping || sending}
        />
        <button type="submit" disabled={isTyping || sending}>➤</button>
      </form>
    </div>
  );
}
