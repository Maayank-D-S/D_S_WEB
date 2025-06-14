import React, { useState, useEffect, useRef } from "react";
import { MessageCircle, X, Send, RefreshCw } from "lucide-react";

const PROJECTS = ["Krupal Habitat", "Ramvan Villas", "Firefly Homes"];
const API_BASE = "http://localhost:5000";

const getUserId = () => {
  let id = localStorage.getItem("user_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("user_id", id);
  }
  return id;
};

const newSessionId = () => {
  const id = crypto.randomUUID();
  localStorage.setItem("session_id", id);
  return id;
};

const getSessionId = () => {
  return localStorage.getItem("session_id") || newSessionId();
};

const getStoredProject = () => {
  return localStorage.getItem("project_name");
};

const setStoredProject = (projectName) => {
  localStorage.setItem("project_name", projectName);
};

const Chat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [project, setProject] = useState(getStoredProject());
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(getSessionId());
  const userId = getUserId();
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (project) {
      fetch(`${API_BASE}/ai/get_messages/${userId}/${sessionId}`)
        .then((res) => res.json())
        .then((data) => {
          const normalized = data.map((m) => ({ ...m, role: m.role || m.sender }));
          if (normalized.length === 0) {
            const welcome = {
              id: Date.now(),
              role: "ai",
              message: `Hello! Ask me anything about ${project}.`,
              timestamp: new Date().toISOString(),
            };
            setMessages([welcome]);
          } else {
            setMessages(normalized);
          }
        })
        .catch((err) => console.error("History load failed", err));
    }
  }, [project, sessionId]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const sendMessage = async () => {
    if (!inputText.trim() || !project) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      message: inputText.trim(),
      timestamp: new Date().toISOString(),
    };

    const botMessageId = Date.now() + 1;
    const placeholderBot = {
      id: botMessageId,
      role: "ai",
      message: "",
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, placeholderBot]);
    setInputText("");
    setIsTyping(true);

    try {
      const res = await fetch(`${API_BASE}/ai/new_query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId,
          message: userMessage.message,
          project_name: project,
        }),
      });

      if (res.ok) {
        const { ai, image_url } = await res.json();
        console.log("image_url", image_url);
        
        const aiText = ai.message;
        let current = "";
        const delay = 20;

        const stream = (i = 0) => {
          if (i <= aiText.length) {
            const current = aiText.slice(0, i);
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === botMessageId
                  ? { ...msg, message: current }
                  : msg
              )
            );
            setTimeout(() => stream(i + 1), delay);
          } else {
            // After stream finishes, add image_url (if any)
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === botMessageId
                  ? { ...msg, image_url: image_url || null }
                  : msg
              )
            );
            setIsTyping(false);
          }
        };

        stream();
      } else {
        console.error(await res.text());
        setIsTyping(false);
      }
    } catch (err) {
      console.error("Error sending message", err);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleNewChat = () => {
    const newId = newSessionId();
    setSessionId(newId);
    localStorage.removeItem("project_name");
    setMessages([]);
    setProject(null);
  };

  return (
    <>
      <button onClick={() => setIsOpen(true)} className="fixed bottom-6 right-6 bg-white/10 hover:bg-gray-800 text-white p-4 rounded-full shadow-xl z-50">
        <MessageCircle className="w-6 h-6" />
      </button>

      {isOpen && (
        <div className="fixed bottom-4 right-4 w-[95%] max-w-[700px] h-[90vh] bg-black text-white rounded-xl shadow-2xl z-50 flex flex-col border border-gray-700">

          <div className="bg-gray-950 p-4 rounded-t-xl flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageCircle className="w-5 h-5 text-green-500" />
              <span className="font-semibold">Chatbot</span>
              <span className="text-xs text-gray-400">Support Agent</span>
            </div>
            <button onClick={() => setIsOpen(false)}>
              <X className="w-5 h-5 text-white" />
            </button>
          </div>

          {!project && (
            <div className="p-4 text-sm">
              <p className="mb-2">Select a project:</p>
              <div className="flex flex-col gap-2">
                {PROJECTS.map((name) => (
                  <button key={name} className="bg-gray-700 hover:bg-gray-600 text-sm px-3 py-1 rounded text-left" onClick={() => { setStoredProject(name); setProject(name); }}>
                    {name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {project && (
            <>
              <div className="px-4 pt-2 text-xs text-right">
                <button className="flex items-center gap-1 text-blue-400 hover:underline" onClick={handleNewChat}>
                  <RefreshCw className="w-3 h-3" /> Start new chat
                </button>
              </div>

              <div ref={chatContainerRef} className="flex-1 p-4 overflow-y-auto space-y-4">
                {messages.map((m) => (
                  <div key={m.id} className={`flex ${m.role?.toLowerCase() === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] p-3 rounded-lg ${m.role?.toLowerCase() === "user" ? "bg-gray-800 text-white" : "bg-white/5 text-white"}`}>
                      <p className="text-sm whitespace-pre-line">{m.message}</p>
                      {m.image_url && m.role?.toLowerCase() === "ai" && (
                        <img src={`${m.image_url}`} alt="AI Attachment" className="mt-2 rounded-lg max-w-full max-h-60" />
                      )}
                      <p className="text-[10px] opacity-50 mt-1 text-right">
                        {new Date(m.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-gray-800 p-3 rounded-lg">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-gray-700">
                <div className="flex space-x-2">
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Write a message"
                    rows={2}
                    className="flex-1 border border-gray-600 bg-gray-600 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-white"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputText.trim()}
                    className="bg-gray-800 hover:bg-gray-700 disabled:bg-gray-600 text-white p-2 rounded-lg"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default Chat;
