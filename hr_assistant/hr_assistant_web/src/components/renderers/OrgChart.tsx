import React, { useState } from 'react';
import type { TreeNode } from '../../types/response';

interface TreeNodeComponentProps {
  node: TreeNode;
  level?: number;
}

const TreeNodeComponent: React.FC<TreeNodeComponentProps> = ({ node, level = 0 }) => {
  const [expanded, setExpanded] = useState(level < 2); // Expand first 2 levels by default

  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="select-none">
      <div
        className={`flex items-center py-1 px-2 rounded hover:bg-gray-100 cursor-pointer ${
          level === 0 ? 'font-semibold' : level === 1 ? 'font-medium' : ''
        }`}
        style={{ paddingLeft: `${level * 20}px` }}
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren && (
          <span className="mr-1 text-gray-500">
            {expanded ? '▼' : '▶'}
          </span>
        )}
        {!hasChildren && (
          <span className="mr-1 text-gray-400">•</span>
        )}
        <span className="text-gray-800">{node.name}</span>
      </div>

      {expanded && hasChildren && (
        <div>
          {node.children?.map((child, index) => (
            <TreeNodeComponent key={index} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

interface OrgChartProps {
  data: TreeNode;
}

const OrgChart: React.FC<OrgChartProps> = ({ data }) => {
  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
      <TreeNodeComponent node={data} />
    </div>
  );
};

export default OrgChart;
