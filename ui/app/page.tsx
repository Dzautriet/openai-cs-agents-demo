"use client";

import { useEffect, useState } from "react";
import { AgentPanel } from "@/components/agent-panel";
import { Chat } from "@/components/chat";
import type { Agent, AgentEvent, GuardrailCheck, Message } from "@/lib/types";
import { callChatAPI, rerunFromMessageAPI } from "@/lib/api";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>("");
  const [guardrails, setGuardrails] = useState<GuardrailCheck[]>([]);
  const [context, setContext] = useState<Record<string, any>>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  // Loading state while awaiting assistant response
  const [isLoading, setIsLoading] = useState(false);

  // Boot the conversation
  useEffect(() => {
    (async () => {
      const data = await callChatAPI("", conversationId ?? "");
      setConversationId(data.conversation_id);
      setCurrentAgent(data.current_agent);
      setContext(data.context);
      const initialEvents = (data.events || []).map((e: any) => ({
        ...e,
        timestamp: e.timestamp ?? Date.now(),
      }));
      setEvents(initialEvents);
      setAgents(data.agents || []);
      setGuardrails(data.guardrails || []);
      if (Array.isArray(data.messages)) {
        setMessages(
          data.messages.map((m: any) => ({
            id: Date.now().toString() + Math.random().toString(),
            content: m.content,
            role: "assistant",
            agent: m.agent,
            timestamp: new Date(),
          }))
        );
      }
    })();
  }, []);

  // Send a user message
  const handleSendMessage = async (content: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    const data = await callChatAPI(content, conversationId ?? "");

    if (!conversationId) setConversationId(data.conversation_id);
    setCurrentAgent(data.current_agent);
    setContext(data.context);
    if (data.events) {
      const stamped = data.events.map((e: any) => ({
        ...e,
        timestamp: e.timestamp ?? Date.now(),
      }));
      setEvents((prev) => [...prev, ...stamped]);
    }
    if (data.agents) setAgents(data.agents);
    // Update guardrails state
    if (data.guardrails) setGuardrails(data.guardrails);

    if (data.messages) {
      const responses: Message[] = data.messages.map((m: any) => ({
        id: Date.now().toString() + Math.random().toString(),
        content: m.content,
        role: "assistant",
        agent: m.agent,
        timestamp: new Date(),
      }));
      setMessages((prev) => [...prev, ...responses]);
    }

    setIsLoading(false);
  };

  // Edit a user message and re-run from that point
  const handleEditMessage = async (messageIndex: number, newContent: string) => {
    if (!conversationId) return;
    
    // Calculate the user message index (count only user messages before this index)
    let userMessageIndex = 0;
    for (let i = 0; i < messageIndex; i++) {
      if (messages[i].role === "user") {
        userMessageIndex++;
      }
    }
    
    setIsLoading(true);
    
    const data = await rerunFromMessageAPI(conversationId, userMessageIndex, newContent);
    
    if (data) {
      setCurrentAgent(data.current_agent);
      setContext(data.context);
      if (data.events) {
        const stamped = data.events.map((e: any) => ({
          ...e,
          timestamp: e.timestamp ?? Date.now(),
        }));
        setEvents(stamped);
      }
      if (data.agents) setAgents(data.agents);
      if (data.guardrails) setGuardrails(data.guardrails);

      // Replace messages from the edit point onward
      const messagesUpToEdit = messages.slice(0, messageIndex);
      const editedUserMessage: Message = {
        ...messages[messageIndex],
        content: newContent,
      };
      
      const newMessages = [editedUserMessage];
      if (data.messages) {
        const responses: Message[] = data.messages.map((m: any) => ({
          id: Date.now().toString() + Math.random().toString(),
          content: m.content,
          role: "assistant",
          agent: m.agent,
          timestamp: new Date(),
        }));
        newMessages.push(...responses);
      }
      
      setMessages([...messagesUpToEdit, ...newMessages]);
    }
    
    setIsLoading(false);
  };


  return (
    <main className="flex h-screen gap-2 bg-gray-100 p-2">
      <AgentPanel
        agents={agents}
        currentAgent={currentAgent}
        events={events}
        guardrails={guardrails}
        context={context}
      />
      <Chat
        messages={messages}
        onSendMessage={handleSendMessage}
        onEditMessage={handleEditMessage}
        isLoading={isLoading}
      />
    </main>
  );
}
