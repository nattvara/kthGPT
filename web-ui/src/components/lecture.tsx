
interface Message {
  id: number
  title: string
  body: string | null
}

interface Analysis {
  id: number
  created_at: Date
  modified_at: Date
  state: string
  mp4_progress: number
  mp3_progress: number
  transcript_progress: number
  summary_progress: number
  overall_progress: number
  last_message: Message | null
}


export interface Lecture {
  public_id: string
  language: string
  words: number | null
  length: number | null
  preview_uri: string | null
  transcript_uri: string | null
  summary_uri: string | null
  content_link: string
  analysis: Analysis | null
}
