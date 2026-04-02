import React from 'react';
import type { MetricData } from '../../types/response';

interface MetricViewProps {
  data: MetricData;
}

const MetricView: React.FC<MetricViewProps> = ({ data }) => (
  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <div className="text-xs text-gray-600">{data.label}</div>
    <div className="text-2xl font-bold">{data.value}</div>
  </div>
);

export default MetricView;
