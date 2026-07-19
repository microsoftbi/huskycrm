export interface SearchResult {
  id: string
  name: string
}

export interface SearchResults {
  accounts: SearchResult[]
  contacts: SearchResult[]
  opportunities: SearchResult[]
  products: SearchResult[]
  events: SearchResult[]
  custom_objects: Record<string, SearchResult[]>
}