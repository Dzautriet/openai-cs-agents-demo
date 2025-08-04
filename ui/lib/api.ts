// Helper to call the server
export async function callChatAPI(message: string, conversationId: string) {
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: conversationId, message }),
    });
    if (!res.ok) throw new Error(`Chat API error: ${res.status}`);
    return res.json();
  } catch (err) {
    console.error("Error sending message:", err);
    return null;
  }
}

// Helper to re-run conversation from a specific message index
export async function rerunFromMessageAPI(
  conversationId: string, 
  messageIndex: number, 
  newMessage?: string
) {
  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        conversation_id: conversationId, 
        message: newMessage || "",
        rerun_from_message_index: messageIndex
      }),
    });
    if (!res.ok) throw new Error(`Rerun API error: ${res.status}`);
    return res.json();
  } catch (err) {
    console.error("Error re-running conversation:", err);
    return null;
  }
}
