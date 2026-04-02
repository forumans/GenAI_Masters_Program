import React from 'react';
import OrgChart from './OrgChart';
import type { TreeNode } from '../../types/response';

interface TreeViewProps {
  data: TreeNode | string; // Support both old and new format for backward compatibility
}

const TreeView: React.FC<TreeViewProps> = ({ data }) => {
  // Check if data is new JSON format or old string format
  if (typeof data === 'object' && data.name) {
    // New interactive format
    return <OrgChart data={data} />;
  } else {
    // Old plain text format - fallback
    return (
      <div 
        className="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-3 rounded-lg"
        style={{ lineHeight: "1.5" }}
      >
        {data}
      </div>
    );
  }
};

export default TreeView;
