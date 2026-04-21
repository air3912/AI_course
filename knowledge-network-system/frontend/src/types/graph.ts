export interface GraphNode {
  id: string;
  label: string;
  type?: string;
  score?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight?: number;
  relation?: string;
}

export interface GraphBuildResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  keywords?: string[];
  entities?: string[];
  stats?: {
    node_count: number;
    edge_count: number;
    keyword_count: number;
    entity_count: number;
  };
}
