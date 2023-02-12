
export interface Lecture {
  public_id: string
  language: string
  words: number | null
  length: number | null
  state: string
  preview_uri: string | null
  transcript_uri: string | null
  summary_uri: string | null
  content_link: string
  mp4_progress: number
  mp3_progress: number
  transcript_progress: number
  summary_progress: number
  overall_progress: number
}
