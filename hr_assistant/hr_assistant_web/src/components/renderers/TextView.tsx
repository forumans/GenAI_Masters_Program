import React from 'react';

interface TextViewProps {
  text: string;
}

const TextView: React.FC<TextViewProps> = ({ text }) => (
  <div className="prose prose-sm max-w-none">
    {text}
  </div>
);

export default TextView;
