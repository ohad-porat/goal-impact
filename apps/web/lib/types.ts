export interface League {
  id: number
  name: string
  country: string
  gender: string
  tier: string
  available_seasons: string
}

export interface ApiResponse<T> {
  data?: T
  error?: string
  loading?: boolean
}
