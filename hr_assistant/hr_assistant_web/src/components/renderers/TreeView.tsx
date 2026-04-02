import React from 'react';

interface TreeViewProps {
  text: string;
}

const TreeView: React.FC<TreeViewProps> = ({ text }) => (
  <div 
    className="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-3 rounded-lg"
    style={{ lineHeight: "1.5" }}
  >
    {text}
  </div>
);

export default TreeView;
