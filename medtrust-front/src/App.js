import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (input.trim() === '') return;

    // Añadir el mensaje del usuario
    const userMessage = { role: 'user', content: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');

    try {
      // Enviar el mensaje al backend
      const response = await fetch('http://127.0.0.1:8000/enviar-mensaje', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mensaje: input }),
      });
      const data = await response.json();

      // Añadir la respuesta del asistente
      const assistantMessage = { role: 'assistant', content: data.respuesta };
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Chatbot con Amazon Bedrock</h1>
      <div className="chat-box bg-white mb-4 p-4 border border-gray-300 rounded h-96 overflow-y-auto">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chat-bubble ${message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'} mb-2`}
          >
            {message.content}
          </div>
        ))}
      </div>
      <div className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') sendMessage();
          }}
          className="w-full p-2 border rounded"
          placeholder="Escribe un mensaje..."
        />
        <button onClick={sendMessage} className="ml-2 p-2 bg-blue-500 text-white rounded">
          Enviar
        </button>
      </div>
    </div>
  );
}

export default App;
