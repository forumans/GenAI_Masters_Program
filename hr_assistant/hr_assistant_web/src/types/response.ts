export type ResponseType = "text" | "table" | "tree" | "metric";

export interface BaseResponse {
  type: ResponseType;
  meta?: {
    title?: string;
    description?: string;
  };
}

export interface TextResponse extends BaseResponse {
  type: "text";
  data: string;
}

export interface TreeResponse extends BaseResponse {
  type: "tree";
  data: string;
}

export interface TableData {
  columns: string[];
  rows: string[][];
}

export interface TableResponse extends BaseResponse {
  type: "table";
  data: TableData;
}

export interface MetricData {
  label: string;
  value: number;
}

export interface MetricResponse extends BaseResponse {
  type: "metric";
  data: MetricData;
}

export type ChatResponse = TextResponse | TreeResponse | TableResponse | MetricResponse;
