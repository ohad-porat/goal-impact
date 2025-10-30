export interface Nation {
  id: number
  name: string
  country_code: string
  governing_body: string
  player_count: number
}

export interface NationsResponse {
  nations: Nation[]
}
