import React from "react";
import ChatInterface from "../components/ChatInterface";

const ChatPage: React.FC = () => {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">HR Assistant Chat</h1>
        <p className="text-sm text-gray-500">
          Ask any question about HR policies, leave entitlements, expenses, benefits, or onboarding.
        </p>
      </div>
      <ChatInterface />
    </div>
  );
};

export default ChatPage;
