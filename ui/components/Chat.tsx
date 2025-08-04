"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import type { Message } from "@/lib/types";
import ReactMarkdown from "react-markdown";
import { SeatMap } from "./seat-map";

interface ChatProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onEditMessage: (messageIndex: number, newContent: string) => void;
  onRegenerateMessage: (messageIndex: number) => void;
  /** Whether waiting for assistant response */
  isLoading?: boolean;
}

export function Chat({ messages, onSendMessage, onEditMessage, onRegenerateMessage, isLoading }: ChatProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputText, setInputText] = useState("");
  const [isComposing, setIsComposing] = useState(false);
  const [showSeatMap, setShowSeatMap] = useState(false);
  const [selectedSeat, setSelectedSeat] = useState<string | undefined>(undefined);
  const [editingMessageIndex, setEditingMessageIndex] = useState<number | null>(null);
  const [editingText, setEditingText] = useState("");
  const [copiedMessageIndex, setCopiedMessageIndex] = useState<number | null>(null);

  // Auto-scroll to bottom when messages or loading indicator change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "instant" });
  }, [messages, isLoading]);

  // Watch for special seat map trigger message (anywhere in list) and only if a seat has not been picked yet
  useEffect(() => {
    const hasTrigger = messages.some(
      (m) => m.role === "assistant" && m.content === "DISPLAY_SEAT_MAP"
    );
    // Show map if trigger exists and seat not chosen yet
    if (hasTrigger && !selectedSeat) {
      setShowSeatMap(true);
    }
  }, [messages, selectedSeat]);

  const handleSend = useCallback(() => {
    if (!inputText.trim()) return;
    onSendMessage(inputText);
    setInputText("");
  }, [inputText, onSendMessage]);

  const handleSeatSelect = useCallback(
    (seat: string) => {
      setSelectedSeat(seat);
      setShowSeatMap(false);
      onSendMessage(`I would like seat ${seat}`);
    },
    [onSendMessage]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey && !isComposing) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend, isComposing]
  );

  const handleEditStart = useCallback((messageIndex: number, currentContent: string) => {
    setEditingMessageIndex(messageIndex);
    setEditingText(currentContent);
  }, []);

  const handleEditCancel = useCallback(() => {
    setEditingMessageIndex(null);
    setEditingText("");
  }, []);

  const handleEditSend = useCallback(() => {
    if (editingMessageIndex !== null && editingText.trim()) {
      onEditMessage(editingMessageIndex, editingText);
      setEditingMessageIndex(null);
      setEditingText("");
    }
  }, [editingMessageIndex, editingText, onEditMessage]);

  const handleEditKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleEditSend();
      } else if (e.key === "Escape") {
        e.preventDefault();
        handleEditCancel();
      }
    },
    [handleEditSend, handleEditCancel]
  );

  const handleRegenerateClick = useCallback((messageIndex: number) => {
    onRegenerateMessage(messageIndex);
  }, [onRegenerateMessage]);

  const handleCopyClick = useCallback(async (content: string, messageIndex: number) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageIndex(messageIndex);
      // Reset the copied state after 2 seconds
      setTimeout(() => setCopiedMessageIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  }, []);

  return (
    <div className="flex flex-col h-full flex-1 bg-white shadow-sm border border-gray-200 border-t-0 rounded-xl">
      <div className="bg-blue-600 text-white h-12 px-4 flex items-center rounded-t-xl">
        <h2 className="font-semibold text-sm sm:text-base lg:text-lg">
          Customer View
        </h2>
      </div>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto min-h-0 md:px-4 pt-4 pb-20">
        {messages.map((msg, idx) => {
          if (msg.content === "DISPLAY_SEAT_MAP") return null; // Skip rendering marker message
          
          const isEditing = editingMessageIndex === idx;
          const isUserMessage = msg.role === "user";
          const isAssistantMessage = msg.role === "assistant";
          const canEdit = isUserMessage;
          const canRegenerate = isAssistantMessage;
          const canCopy = true; // Both user and assistant messages can be copied
          const isCopied = copiedMessageIndex === idx;
          
          return (
            <div
              key={idx}
              className={`group flex mb-5 text-sm ${isUserMessage ? "justify-end" : "justify-start"}`}
            >
              <div className={`relative ${isUserMessage ? "ml-4 md:ml-24" : "mr-4 md:mr-24"} max-w-[80%]`}>
                {isEditing ? (
                  <div className="rounded-[16px] px-4 py-2 bg-white border-2 border-blue-300">
                    <textarea
                      value={editingText}
                      onChange={(e) => setEditingText(e.target.value)}
                      onKeyDown={handleEditKeyDown}
                      className="w-full resize-none border-0 focus:outline-none text-sm bg-transparent"
                      rows={3}
                      autoFocus
                    />
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={handleEditSend}
                        className="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-1"
                      >
                        Send ↗
                      </button>
                      <button
                        onClick={handleEditCancel}
                        className="px-3 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className={`rounded-[16px] px-4 py-2 font-light ${
                      isUserMessage 
                        ? "rounded-br-[4px] bg-black text-white" 
                        : "rounded-bl-[4px] text-zinc-900 bg-[#ECECF1]"
                    }`}>
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                    
                    {/* Action buttons */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 absolute -top-2 -right-2 flex gap-1">
                      {canCopy && (
                        <button
                          onClick={() => handleCopyClick(msg.content, idx)}
                          className={`p-1.5 rounded-md text-xs transition-all duration-200 border shadow-sm active:scale-95 ${
                            isCopied
                              ? "bg-green-100 hover:bg-green-200 text-green-700 border-green-200"
                              : "bg-gray-100 hover:bg-gray-200 text-gray-600 border-gray-200"
                          }`}
                          title={isCopied ? "Copied!" : "Copy message"}
                        >
                          {isCopied ? (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M20 6 9 17l-5-5"/>
                            </svg>
                          ) : (
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
                              <path d="m4 16c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2h8c1.1 0 2 .9 2 2"/>
                            </svg>
                          )}
                        </button>
                      )}
                      {canEdit && (
                        <button
                          onClick={() => handleEditStart(idx, msg.content)}
                          className="p-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-md text-xs transition-all duration-200 border border-gray-200 shadow-sm active:scale-95 active:bg-gray-300"
                          title="Edit and resend message"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                        </button>
                      )}
                      {canRegenerate && (
                        <button
                          onClick={() => handleRegenerateClick(idx)}
                          className="p-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-md text-xs transition-all duration-200 border border-gray-200 shadow-sm active:scale-95 active:bg-gray-300"
                          title="Regenerate response"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                            <path d="M21 3v5h-5"/>
                            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
                            <path d="M3 21v-5h5"/>
                          </svg>
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          );
        })}
        {showSeatMap && (
          <div className="flex justify-start mb-5">
            <div className="mr-4 rounded-[16px] rounded-bl-[4px] md:mr-24">
              <SeatMap
                onSeatSelect={handleSeatSelect}
                selectedSeat={selectedSeat}
              />
            </div>
          </div>
        )}
        {isLoading && (
          <div className="flex mb-5 text-sm justify-start">
            <div className="h-3 w-3 bg-black rounded-full animate-pulse" />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-2 md:px-4">
        <div className="flex items-center">
          <div className="flex w-full items-center pb-4 md:pb-1">
            <div className="flex w-full flex-col gap-1.5 rounded-2xl p-2.5 pl-1.5 bg-white border border-stone-200 shadow-sm transition-colors">
              <div className="flex items-end gap-1.5 md:gap-2 pl-4">
                <div className="flex min-w-0 flex-1 flex-col">
                  <textarea
                    id="prompt-textarea"
                    tabIndex={0}
                    dir="auto"
                    rows={2}
                    placeholder="Message..."
                    className="mb-2 resize-none border-0 focus:outline-none text-sm bg-transparent px-0 pb-6 pt-2"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onCompositionStart={() => setIsComposing(true)}
                    onCompositionEnd={() => setIsComposing(false)}
                  />
                </div>
                <button
                  disabled={!inputText.trim()}
                  className="flex h-8 w-8 items-end justify-center rounded-full bg-black text-white hover:opacity-70 disabled:bg-gray-300 disabled:text-gray-400 transition-colors focus:outline-none"
                  onClick={handleSend}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="32"
                    height="32"
                    fill="none"
                    viewBox="0 0 32 32"
                    className="icon-2xl"
                  >
                    <path
                      fill="currentColor"
                      fillRule="evenodd"
                      d="M15.192 8.906a1.143 1.143 0 0 1 1.616 0l5.143 5.143a1.143 1.143 0 0 1-1.616 1.616l-3.192-3.192v9.813a1.143 1.143 0 0 1-2.286 0v-9.813l-3.192 3.192a1.143 1.143 0 1 1-1.616-1.616z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
