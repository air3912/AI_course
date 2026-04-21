export interface ApiMessage {
  message: string;
}

export interface UploadProcessResponse {
  filename: string;
  file_type: string;
  saved_path: string;
  upload_status: string;
  parse_status: string;
  graph_status: string;
  text_length: number;
  extracted_text_preview: string;
  document_id: number;
  graph_snapshot_id: number;
  keywords: string[];
  entities: string[];
  nodes: Array<{ id: string; label: string; type?: string; score?: number }>;
  edges: Array<{ source: string; target: string; weight?: number; relation?: string }>;
}
