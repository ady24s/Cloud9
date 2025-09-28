// src/components/ChatbotUI.jsx
import React, { useState } from "react";
import axios from "../api";

const ChatbotUI = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await axios.post("/chat", { question: input });
      const botMsg = { sender: "bot", text: res.data.response };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Chat error:", err);
    } finally {
      setInput("");
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-window">
        {messages.map((m, idx) => (
          <div key={idx} className={`message ${m.sender}`}>
            {m.text}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatbotUI;
