import React from 'react';
import type { ChatResponse } from '../../types/response';
import TextView from './TextView';
import TreeView from './TreeView';
import TableView from './TableView';
import MetricView from './MetricView';

interface ChatRendererProps {
  response: ChatResponse;
}

const ChatRenderer: React.FC<ChatRendererProps> = ({ response }) => {
  const { type, data, meta } = response;

  return (
    <div className="space-y-2">
      {meta?.title && (
        <div className="text-sm font-semibold text-gray-700">
          {meta.title}
        </div>
      )}
      
      {meta?.description && (
        <div className="text-xs text-gray-500">
          {meta.description}
        </div>
      )}

      {type === "text" && <TextView text={data} />}
      {type === "tree" && <TreeView data={data} />}
      {type === "table" && <TableView data={data} />}
      {type === "metric" && <MetricView data={data} />}
    </div>
  );
};

export default ChatRenderer;
