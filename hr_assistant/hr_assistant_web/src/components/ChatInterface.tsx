import React, { useState, useRef, useEffect, useCallback } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { chatApi } from "../services/api";
import type { ChatMessage } from "../types";

// Simple markdown parser for tables and basic formatting
const parseMarkdown = (text: string): string => {
  // Check if response is JSON format
  if (text.trim().startsWith('{') && text.trim().endsWith('}')) {
    try {
      const jsonData = JSON.parse(text);
      
      // Check if it's table data
      if (jsonData.columns && Array.isArray(jsonData.columns) && jsonData.rows && Array.isArray(jsonData.rows)) {
        // Build HTML table from JSON
        let html = '<table class="min-w-full border-collapse border border-gray-300 my-2">';
        
        // Add headers
        html += `<tr>${jsonData.columns.map((col: string) => `<th class="border border-gray-300 px-2 py-1 text-left bg-gray-100">${col}</th>`).join('')}</tr>`;
        
        // Add rows
        for (const row of jsonData.rows) {
          if (Array.isArray(row)) {
            html += `<tr>${row.map((cell: string) => `<td class="border border-gray-300 px-2 py-1 text-left">${cell || ''}</td>`).join('')}</tr>`;
          }
        }
        
        html += '</table>';
        return html;
      }
    } catch (e) {
      // Not valid JSON, continue with markdown parsing
    }
  }
  
  // Original markdown parsing logic for non-JSON responses
  if (text.includes('|')) {
    let html = '';
    
    // Check if it's the malformed single-line format with separators
    if (text.includes('|--------------|') || text.includes('|----------------|') || text.includes('|------------|') || text.includes('|---------|')) {
      // Extract all content between pipes
      const matches = text.match(/([^|]+)/g) || [];
      const allData = matches.map(item => item.trim()).filter(item => item);
      
      // Find TableColumn markers to determine column structure
      const columnMarkers = allData.filter(item => item.startsWith('TableColumn-'));
      const numColumns = columnMarkers.length;
      
      if (numColumns > 0) {
        // Extract column names from markers
        const columnNames = columnMarkers.map(marker => marker.replace('TableColumn-', ''));
        
        // Find where actual data starts (after column markers and separators)
        const dataStartIndex = allData.findIndex(item => 
          !item.startsWith('TableColumn-') && 
          !item.match(/^[\s\-\:]+$/) &&
          item.length > 0
        );
        
        // Get only the actual data
        let dataOnly = allData.slice(dataStartIndex);
        
        // Special handling: If we have only one TableColumn marker but mixed data (holidays and dates)
        if (numColumns === 1 && dataOnly.length > 2) {
          // Check if data contains both holidays and dates
          const datePatterns = [
            /^(January|February|March|April|May|June|July|August|September|October|November|December)/,
            /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/,
            /\d{1,2}\/\d{1,2}/,
            /\d{1,2}-\d{1,2}/
          ];
          
          const holidayPatterns = [
            /(?:New Year|Martin Luther|President|Memorial|Independence|Labor|Columbus|Veteran|Thanksgiving|Christmas)/i,
            /Holiday/i,
            /Vacation/i,
            /Break/i
          ];
          
          const dateItems = dataOnly.filter(item => datePatterns.some(p => p.test(item)));
          const holidayItems = dataOnly.filter(item => 
            holidayPatterns.some(p => p.test(item)) || 
            (item && !datePatterns.some(p => p.test(item)) && item.length > 2)
          );
          
          // If we can separate holidays from dates, create proper 2-column structure
          if (dateItems.length > 0 && holidayItems.length > 0) {
            columnNames.push('Date');
            
            // Try to pair holidays with dates
            const pairedData: [string, string][] = [];
            let dateIndex = 0;
            
            for (const holiday of holidayItems) {
              const date = dateItems[dateIndex] || '';
              pairedData.push([holiday, date]);
              dateIndex++;
            }
            
            // Build table with paired data
            html += '<table class="min-w-full border-collapse border border-gray-300 my-2">';
            html += `<tr>${columnNames.map(name => `<th class="border border-gray-300 px-2 py-1 text-left bg-gray-100">${name}</th>`).join('')}</tr>`;
            
            for (const [holiday, date] of pairedData) {
              html += `<tr><td class="border border-gray-300 px-2 py-1 text-left">${holiday}</td><td class="border border-gray-300 px-2 py-1 text-left">${date}</td></tr>`;
            }
            
            html += '</table>';
          } else {
            // Can't separate, just show as single column
            html += '<table class="min-w-full border-collapse border border-gray-300 my-2">';
            html += `<tr><th class="border border-gray-300 px-2 py-1 text-left bg-gray-100">${columnNames[0]}</th></tr>`;
            
            for (const item of dataOnly) {
              html += `<tr><td class="border border-gray-300 px-2 py-1 text-left">${item}</td></tr>`;
            }
            
            html += '</table>';
          }
        } else {
          // Normal case: we have proper column markers or need to infer
          
          // If we have fewer column markers than expected, infer the missing ones
          if (numColumns === 1 && dataOnly.length > 1) {
            // Check if this looks like holiday data (first half are names, second half are dates)
            const datePatterns = [
              /^(January|February|March|April|May|June|July|August|September|October|November|December)/,
              /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/,
              /\d{1,2}\/\d{1,2}/,
              /\d{1,2}-\d{1,2}/
            ];
            
            const dateIndices = dataOnly.map((item, idx) => datePatterns.some(p => p.test(item)) ? idx : -1).filter(idx => idx !== -1);
            
            if (dateIndices.length > 0 && dateIndices[0] > 0) {
              // This looks like 2-column data
              columnNames.push('Date');
            } else {
              // Default to second column as "Details"
              columnNames.push('Details');
            }
          }
          
          // Calculate number of rows based on actual column count
          const actualNumColumns = columnNames.length;
          const numRows = Math.ceil(dataOnly.length / actualNumColumns);
          
          // Transpose the data from columns to rows
          const transposedData: string[][] = [];
          
          for (let row = 0; row < numRows; row++) {
            const rowData: string[] = [];
            for (let col = 0; col < actualNumColumns; col++) {
              const index = row + (col * numRows);
              rowData.push(dataOnly[index] || '');
            }
            transposedData.push(rowData);
          }
          
          // Build proper table
          html += '<table class="min-w-full border-collapse border border-gray-300 my-2">';
          
          // Add headers with actual column names
          html += `<tr>${columnNames.map(name => `<th class="border border-gray-300 px-2 py-1 text-left bg-gray-100">${name}</th>`).join('')}</tr>`;
          
          // Add rows
          for (const row of transposedData) {
            if (row.some(cell => cell.length > 0)) { // Skip empty rows
              html += `<tr>${row.map(cell => `<td class="border border-gray-300 px-2 py-1 text-left">${cell}</td>`).join('')}</tr>`;
            }
          }
          
          html += '</table>';
        }
      } else {
        // Fallback to old logic if no TableColumn markers found
        const commonHeaders = ['Holiday Name', 'Date', 'Holiday', 'Name', 'Day', 'Type', 'Days', 'Description', 'Details', 'Policy', 'Amount', 'Eligibility'];
        const dataOnly = allData.filter(item => 
          !commonHeaders.includes(item) && 
          !item.match(/^[\s\-\:]+$/) &&
          item.length > 0
        );
        
        if (dataOnly.length > 2) {
          // Try to determine columns by patterns (fallback logic)
          const datePatterns = [
            /^(January|February|March|April|May|June|July|August|September|October|November|December)/,
            /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/,
            /\d{1,2}\/\d{1,2}/,
            /\d{1,2}-\d{1,2}/
          ];
          
          const dateIndices = dataOnly.map((item, idx) => datePatterns.some(p => p.test(item)) ? idx : -1).filter(idx => idx !== -1);
          
          let numColumns = 2;
          if (dateIndices.length > 0) {
            const firstDateIndex = dateIndices[0];
            if (firstDateIndex > 0) {
              const numRows = firstDateIndex;
              numColumns = Math.ceil(dataOnly.length / numRows);
            }
          }
          
          const numRows = Math.ceil(dataOnly.length / numColumns);
          const transposedData: string[][] = [];
          
          for (let row = 0; row < numRows; row++) {
            const rowData: string[] = [];
            for (let col = 0; col < numColumns; col++) {
              const index = row + (col * numRows);
              rowData.push(dataOnly[index] || '');
            }
            transposedData.push(rowData);
          }
          
          html += '<table class="min-w-full border-collapse border border-gray-300 my-2">';
          const headers = numColumns === 2 ? ['Item', 'Details'] :
                         numColumns === 3 ? ['Item', 'Details', 'Additional'] :
                         ['Column 1', 'Column 2', 'Column 3', 'Column 4'];
          
          html += `<tr>${headers.map(h => `<th class="border border-gray-300 px-2 py-1 text-left bg-gray-100">${h}</th>`).join('')}</tr>`;
          
          for (const row of transposedData) {
            if (row.some(cell => cell.length > 0)) {
              html += `<tr>${row.map(cell => `<td class="border border-gray-300 px-2 py-1 text-left">${cell}</td>`).join('')}</tr>`;
            }
          }
          
          html += '</table>';
        } else {
          html += '<table class="min-w-full border-collapse border border-gray-300 my-2">';
          html += '<tr><th class="border border-gray-300 px-2 py-1 text-left bg-gray-100">Item</th><th class="border border-gray-300 px-2 py-1 text-left bg-gray-100">Details</th></tr>';
          
          for (let i = 0; i < dataOnly.length; i += 2) {
            const item = dataOnly[i] || '';
            const details = dataOnly[i + 1] || '';
            html += `<tr><td class="border border-gray-300 px-2 py-1 text-left">${item}</td><td class="border border-gray-300 px-2 py-1 text-left">${details}</td></tr>`;
          }
          
          html += '</table>';
        }
      }
    } else {
      // Standard markdown table processing
      const lines = text.split('\n');
      let inTable = false;
      let isHeader = true;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (line.includes('|')) {
          // Skip separator lines
          if (/^[\|\-\s:]+$/.test(line) || /^\|[\s\-\|:]+\|$/.test(line)) {
            isHeader = false;
            continue;
          }
          
          if (!inTable) {
            html += '<table class="min-w-full border-collapse border border-gray-300 my-2">';
            inTable = true;
            isHeader = true;
          }
          
          // Extract cells
          let cells: string[] = [];
          if (line.startsWith('|') && line.endsWith('|')) {
            cells = line
              .substring(1, line.length - 1)
              .split('|')
              .map(cell => cell.trim())
              .filter(cell => cell);
          } else {
            cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
          }
          
          // Skip separators
          if (cells.length === 0 || cells.every(cell => /^[\s\-\:]+$/.test(cell))) {
            isHeader = false;
            continue;
          }
          
          // Create row
          const tag = isHeader ? 'th' : 'td';
          html += `<tr>${cells.map(cell => `<${tag} class="border border-gray-300 px-2 py-1 text-left">${cell}</${tag}>`).join('')}</tr>`;
          
          if (isHeader) isHeader = false;
        } else {
          if (inTable) {
            html += '</table>';
            inTable = false;
          }
          if (line) {
            html += line + '<br>';
          }
        }
      }
      
      if (inTable) {
        html += '</table>';
      }
    }
    
    // Convert other markdown
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return html;
  }
  
  // No table found
  let html = text.replace(/\n/g, '<br>');
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  
  return html;
};

// Polyfill for crypto.randomUUID for browsers that don't support it
if (typeof window !== 'undefined' && !window.crypto?.randomUUID) {
  (window.crypto as any).randomUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };
}

interface ChatInterfaceProps {
  employeeId?: number;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ employeeId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm your HR Assistant. I can help you with questions about leave policies, expense claims, benefits, onboarding, and more. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMessage: ChatMessage = {
      id: window.crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    // Update messages state and get the new state
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsLoading(true);

    // Add a placeholder assistant message for streaming
    const assistantId = window.crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      {
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: new Date(),
      },
    ]);

    try {
      // Prepare conversation history (exclude welcome message and take last 10 turns)
      const historyForApi = updatedMessages
        .filter(m => m.id !== "welcome")
        .slice(-10)
        .map(m => ({ role: m.role, content: m.content }));
      
      const streamGenerator = chatApi.sendStream({ 
        message: text, 
        employee_id: employeeId,
        conversation_history: historyForApi
      });
      
      for await (const token of streamGenerator) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + token } : m
          )
        );
      }
    } catch (err) {
      // Fall back to non-streaming if SSE fails
      try {
        // Prepare conversation history (exclude welcome message and take last 10 turns)
        const historyForApi = updatedMessages
          .filter(m => m.id !== "welcome")
          .slice(-10)
          .map(m => ({ role: m.role, content: m.content }));
        
        const response = await chatApi.send({ 
          message: text, 
          employee_id: employeeId,
          conversation_history: historyForApi
        });
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: response.response } : m
          )
        );
      } catch {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content:
                    "Sorry, I encountered an error processing your request. Please try again or contact HR directly.",
                }
              : m
          )
        );
      }
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [input, isLoading, employeeId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 bg-primary-600 text-white">
        <Bot className="w-5 h-5" />
        <div>
          <h2 className="font-semibold text-sm">HR Assistant</h2>
          <p className="text-xs text-primary-200">Powered by GPT-4o mini</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-primary-200">Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            {/* Avatar */}
            <div
              className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                msg.role === "user"
                  ? "bg-primary-100 text-primary-600"
                  : "bg-gray-100 text-gray-600"
              }`}
            >
              {msg.role === "user" ? (
                <User className="w-4 h-4" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
            </div>

            {/* Bubble */}
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-primary-600 text-white rounded-tr-sm"
                  : "bg-gray-100 text-gray-800 rounded-tl-sm"
              }`}
            >
              {msg.content ? (
                msg.role === "assistant" ? (
                  <div 
                    dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }}
                    className="prose prose-sm max-w-none"
                  />
                ) : (
                  msg.content
                )
              ) : (
                <span className="flex items-center gap-1 text-gray-400">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Thinking…
                </span>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-3 bg-gray-50">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about HR policies, leave, expenses…"
            rows={1}
            disabled={isLoading}
            className="flex-1 resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 disabled:bg-gray-100 max-h-32 overflow-y-auto"
            style={{ minHeight: "2.5rem" }}
            onInput={(e) => {
              const el = e.currentTarget;
              el.style.height = "auto";
              el.style.height = Math.min(el.scrollHeight, 128) + "px";
            }}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="flex-shrink-0 w-10 h-10 flex items-center justify-center bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1.5 text-center">
          Press Enter to send &middot; Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;
