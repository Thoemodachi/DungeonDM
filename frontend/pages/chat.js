import { useState } from "react";

export default function ChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input) return;

    const userMessage = { role: "user", text: input };
    setMessages([...messages, userMessage]);

    setInput("");

    const res = await fetch("http://127.0.0.1:8000/play_turn", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: "test_player", input_text: input }),
    });

    const data = await res.json();
    setMessages((prev) => [...prev, { role: "dm", text: data.narration }]);
  };

  return (
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">DungeonDM Chat</h1>
      <div className="border rounded p-4 h-80 overflow-y-auto mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === "user" ? "text-right" : "text-left"}>
            <p className={msg.role === "user" ? "bg-blue-200 inline-block p-2 rounded" : "bg-gray-200 inline-block p-2 rounded"}>
              {msg.text}
            </p>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="border p-2 flex-1"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your action..."
        />
        <button className="bg-blue-500 text-white px-4 rounded" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}
