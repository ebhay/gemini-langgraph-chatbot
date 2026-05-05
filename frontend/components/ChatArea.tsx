'use client';

import { useState, useRef, useEffect } from 'react';
import { useStore } from '@/lib/store';
import { chatAPI } from '@/lib/api';
import { Send, Menu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatAreaProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function ChatArea({ sidebarOpen, onToggleSidebar }: ChatAreaProps) {
  const { messages, currentSessionId, addMessage, setIsLoading, isLoading } = useStore();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user' as const,
      text: input,
      created_at: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage({
        user_input: input,
        session_id: currentSessionId,
      });

      const botMessage = {
        role: 'bot' as const,
        text: response.data.response,
        created_at: new Date().toISOString(),
      };

      addMessage(botMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        role: 'bot' as const,
        text: 'Sorry, I encountered an error. Please try again.',
        created_at: new Date().toISOString(),
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen">
      {!sidebarOpen && (
        <div className="p-4 border-b border-border">
          <button
            onClick={onToggleSidebar}
            className="p-2 hover:bg-accent rounded-md"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <h2 className="text-2xl font-bold text-foreground">Welcome to Gemini Chat</h2>
              <p className="text-muted-foreground">Start a conversation by typing a message below</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 max-w-2xl">
                <div className="p-4 border border-border rounded-lg hover:bg-accent/50 cursor-pointer">
                  <p className="text-sm font-medium">Find hospitals in Delhi</p>
                </div>
                <div className="p-4 border border-border rounded-lg hover:bg-accent/50 cursor-pointer">
                  <p className="text-sm font-medium">Remind me to drink water</p>
                </div>
                <div className="p-4 border border-border rounded-lg hover:bg-accent/50 cursor-pointer">
                  <p className="text-sm font-medium">Tell me about yourself</p>
                </div>
                <div className="p-4 border border-border rounded-lg hover:bg-accent/50 cursor-pointer">
                  <p className="text-sm font-medium">I am 25 years old</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-secondary text-secondary-foreground'
                  }`}
                >
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.text}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-secondary rounded-lg p-4">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="p-4 border-t border-border">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message... (Shift+Enter for new line)"
            className="flex-1 px-4 py-3 bg-background border border-input rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none max-h-32"
            rows={1}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
