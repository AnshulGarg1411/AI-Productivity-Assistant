import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Bot, Send, Sparkles, User } from "lucide-react";

import { useChat } from "../hooks/useChat";

const SUGGESTIONS = [
  "What are my pending tasks?",
  "What meetings do I have coming up?",
  "What should I focus on today?",
  "Any unread important emails?",
];

const AIAssistant = () => {
  const { mutate, isPending } = useChat();
  const queryClient = useQueryClient();

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I can look up your tasks, meetings, and emails, or take actions like creating a task or scheduling a meeting. What do you need?",
      toolCalls: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [unavailable, setUnavailable] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = (text) => {
    if (!text.trim() || isPending) return;

    const nextMessages = [...messages, { role: "user", content: text, toolCalls: [] }];
    setMessages(nextMessages);
    setInput("");

    mutate(
      {
        message: text,
        history: nextMessages.map((m) => ({ role: m.role, content: m.content })),
      },
      {
        onSuccess: (data) => {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: data.reply, toolCalls: data.tool_calls || [] },
          ]);
          if (data.tool_calls?.length) {
            // The agent may have created/completed/deleted tasks or
            // meetings -- make sure those pages reflect it immediately.
            queryClient.invalidateQueries({ queryKey: ["tasks"] });
            queryClient.invalidateQueries({ queryKey: ["meetings"] });
            queryClient.invalidateQueries({ queryKey: ["dashboard"] });
            queryClient.invalidateQueries({ queryKey: ["taskAnalytics"] });
            queryClient.invalidateQueries({ queryKey: ["meetingAnalytics"] });
          }
        },
        onError: (error) => {
          if (error?.response?.status === 503) {
            setUnavailable(true);
          } else {
            setMessages((prev) => [
              ...prev,
              {
                role: "assistant",
                content: "Something went wrong. Please try again.",
                toolCalls: [],
              },
            ]);
          }
        },
      }
    );
  };

  return (
    <div className="max-w-5xl mx-auto px-10 py-8 flex flex-col h-[calc(100vh-3rem)]">
      <div className="text-3xl mb-3 leading-none">🤖</div>
      <h1 className="text-2xl font-semibold text-ink tracking-tight mb-6">
        AI Assistant
      </h1>

      {unavailable ? (
        <div className="border border-dashed border-border-strong rounded-lg flex flex-col items-center justify-center flex-1 text-center px-6">
          <div className="w-11 h-11 rounded-md bg-surface flex items-center justify-center mb-4">
            <Bot className="text-ink-faint" size={20} />
          </div>
          <h2 className="text-sm font-medium text-ink">AI assistant unavailable</h2>
          <p className="text-sm text-ink-faint mt-1.5 max-w-sm">
            This needs a GEMINI_API_KEY configured in the backend's .env
            file. Everything else in the app works without one.
          </p>
        </div>
      ) : (
        <div className="flex-1 flex flex-col border border-border rounded-lg overflow-hidden min-h-0">
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex gap-2.5 ${m.role === "user" ? "flex-row-reverse" : ""}`}
              >
                <div
                  className={`w-7 h-7 rounded-md flex items-center justify-center shrink-0 ${
                    m.role === "user"
                      ? "bg-accent-soft text-accent"
                      : "bg-surface text-ink-muted"
                  }`}
                >
                  {m.role === "user" ? <User size={14} /> : <Bot size={14} />}
                </div>

                <div className={`max-w-[75%] ${m.role === "user" ? "items-end" : ""} flex flex-col gap-1`}>
                  <div
                    className={`rounded-lg px-3.5 py-2 text-sm whitespace-pre-wrap ${
                      m.role === "user"
                        ? "bg-accent text-white"
                        : "bg-surface text-ink"
                    }`}
                  >
                    {m.content}
                  </div>

                  {m.toolCalls?.length > 0 && (
                    <div className="flex items-center gap-1 flex-wrap">
                      {m.toolCalls.map((tool, ti) => (
                        <span
                          key={ti}
                          className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium bg-[var(--color-tag-yellow-bg)] text-[var(--color-tag-yellow-text)]"
                        >
                          <Sparkles size={9} />
                          {tool}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isPending && (
              <div className="flex gap-2.5">
                <div className="w-7 h-7 rounded-md bg-surface text-ink-muted flex items-center justify-center shrink-0">
                  <Bot size={14} />
                </div>
                <div className="rounded-lg px-3.5 py-2 text-sm bg-surface text-ink-faint">
                  Thinking...
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          <div className="border-t border-border p-3 flex flex-wrap gap-1.5">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                className="text-xs px-2.5 py-1 rounded-full bg-surface text-ink-muted hover:bg-surface-hover transition-colors"
              >
                {s}
              </button>
            ))}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="border-t border-border p-3 flex gap-2"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your tasks, meetings, or emails..."
              className="flex-1 border border-border rounded-md px-3 py-2 text-sm bg-canvas text-ink focus:outline-none focus:ring-2 focus:ring-accent/40"
            />
            <button
              type="submit"
              disabled={isPending}
              className="bg-accent text-white px-3 py-2 rounded-md hover:bg-accent-hover disabled:opacity-50"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;
