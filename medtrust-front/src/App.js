import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const chatBoxRef = useRef(null);  


  const sendMessage = async () => {
    if (input.trim() === '') return;
  
    setError(null);
    const userMessage = { role: 'user', content: input };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
  
    setLoading(true);
  
    try {
      const body = JSON.stringify({ question: input, token: process.env.REACT_APP_API_TOKEN });
      console.log('Enviando:', body);
  
      const response = await fetch('https://vudsgttv4tdevdn4ogx4kc5lb40cmbsg.lambda-url.us-east-1.on.aws/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: body,
      });
  
      console.log('Respuesta recibida:', response);
  
      if (!response.ok) {
        throw new Error(`Error en la respuesta: ${response.status}`);
      }
  
      const data = await response.json();
      const assistantMessage = { role: 'assistant', content: data.response };
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
      setError('Hubo un problema al procesar la respuesta del asistente. Inténtalo de nuevo.');
    } finally {
      setLoading(false);
    }
  };
  

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="container mx-auto p-4">
      {/* Logo */}
      <div className="flex justify-center mb-4">
        <img src={`${process.env.PUBLIC_URL}/logoMed.png`} alt="MedTrust Logo" className="w-32 h-auto" />
      </div>

      {/* Título */}
      <h1 className="text-3xl font-bold text-center text-[#074854] mb-6">Bienvenido a MedTrust</h1>

      {/* Chat Box */}
      <div ref={chatBoxRef} className="chat-box bg-white mb-4 p-4 border border-gray-300 rounded h-96 overflow-y-auto shadow-lg">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chat-bubble ${message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'} mb-2`}
          >
            {message.content}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble chat-bubble-assistant mb-2 italic text-gray-500">
            El asistente está escribiendo...
          </div>
        )}
      </div>

      {error && (
        <div className="text-red-500 mb-4">
          {error}
        </div>
      )}

      {/* Input y Botón */}
      <div className="flex">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') sendMessage();
          }}
          className="w-full p-2 border rounded focus:outline-none focus:border-[#28cfbb]"
          placeholder="Escribe un mensaje..."
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          className="ml-2 p-2 bg-[#28cfbb] text-white rounded hover:bg-[#074854]"
          disabled={loading}
        >
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
}

export default App;
