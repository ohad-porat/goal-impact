export interface Club {
  id: number
  name: string
  first_place_finishes: number
}

export interface NationWithClubs {
  nation: {
    id: number
    name: string
    country_code: string
  }
  clubs: Club[]
}

export interface ClubsResponse {
  nations: NationWithClubs[]
}
