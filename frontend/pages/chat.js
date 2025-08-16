// /app/chat/page.js

'use client';

import { useState } from 'react';
import { audioController } from '../components/AudioController';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [playerId, setPlayerId] = useState(null);
  const [stage, setStage] = useState('askName');

  const sendNameAndStart = async () => {
    try {
      const res = await fetch('http://localhost:8000/start_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: input }),
      });
      const data = await res.json();
      console.log('start_game response:', data);

      setPlayerId(data.player_id);
      setMessages([{ role: 'dm', text: data.narration }]);
      setInput('');

      audioController.play(data.scene_audio || 'exploration_travel');
      setStage('play');
    } catch (err) {
      console.error('Error starting game:', err);
    }
  };

  const sendTurn = async () => {
    if (!input.trim()) return;

    try {
      const res = await fetch('http://localhost:8000/play_turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ player_id: playerId, input_text: input }),
      });
      const data = await res.json();
      console.log('play_turn response:', data);

      setMessages((msgs) => [
        ...msgs,
        { role: 'player', text: input },
        { role: 'dm', text: data.narration },
      ]);

      audioController.play(data.scene_audio || 'exploration_travel');
      setInput('');
    } catch (err) {
      console.error('Error playing turn:', err);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    stage === 'askName' ? sendNameAndStart() : sendTurn();
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <div className="border p-4 h-96 overflow-y-scroll bg-gray-50 rounded">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'dm' ? 'text-blue-700' : 'text-green-700'}>
            <strong>{m.role === 'dm' ? 'DM' : 'You'}:</strong> {m.text}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex mt-4">
        <input
          className="flex-grow border rounded p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={stage === 'askName' ? 'Enter your name...' : 'What do you do?'}
        />
        <button className="ml-2 px-4 py-2 bg-blue-600 text-white rounded">
          {stage === 'askName' ? 'Start' : 'Send'}
        </button>
      </form>
    </div>
  );
}
