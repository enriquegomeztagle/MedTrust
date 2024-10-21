import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const chatBoxRef = useRef(null);

  const sendMessage = async () => {
    if (input.trim() === '') return;

    const userMessage = { role: 'user', content: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');

    try {
      const body = JSON.stringify({ message: input });
      console.log('Enviando:', body);

      const response = await fetch('https://3hmryuz7zufnp77t7sweh4imve0lrpuq.lambda-url.us-east-1.on.aws/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: body,
      });

      if (!response.ok) {
        const errorResponse = await response.text();
        console.error('Error en la respuesta:', response.status, errorResponse);
        return;
      }

      const data = await response.json();
      console.log('Respuesta recibida:', data);

      const assistantMessage = { role: 'assistant', content: data.answer };
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
    }
  };

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Chatea con MedTrust</h1>
      <div ref={chatBoxRef} className="chat-box bg-white mb-4 p-4 border border-gray-300 rounded h-96 overflow-y-auto">
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
