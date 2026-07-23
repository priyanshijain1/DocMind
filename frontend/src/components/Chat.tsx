"use client";

import { useState, useRef, useEffect } from "react";
import { streamChat } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: { page: number; doc_id: string; text: string; score: number }[];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    let assistantMsg = "";
    let sources: Message["sources"] = [];

    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      for await (const chunk of streamChat(question)) {
        if (chunk.token) {
          assistantMsg += chunk.token;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: "assistant", content: assistantMsg };
            return updated;
          });
        }
        if (chunk.sources) {
          sources = chunk.sources;
        }
      }
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "assistant", content: assistantMsg, sources };
        return updated;
      });
    } catch {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "assistant", content: "Error connecting to backend." };
        return updated;
      });
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">DocMind</h1>
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`p-3 rounded-lg ${msg.role === "user" ? "bg-blue-100 ml-auto" : "bg-gray-100"} max-w-[80%]`}>
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-2 text-xs text-gray-500 border-t pt-2">
                {msg.sources.map((s, j) => (
                  <div key={j}>[{j + 1}] Page {s.page} (score: {s.score.toFixed(3)})</div>
                ))}
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-lg px-3 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          onClick={send}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
