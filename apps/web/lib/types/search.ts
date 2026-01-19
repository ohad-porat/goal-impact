export type SearchResultType = "Player" | "Club" | "Competition" | "Nation";

export interface SearchResult {
  id: number;
  name: string;
  type: SearchResultType;
}

export interface SearchResponse {
  results: SearchResult[];
}
