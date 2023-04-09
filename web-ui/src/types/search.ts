import { Lecture } from './lecture';

export interface Image {
  id: string;
  created_at: Date;
  modified_at: Date;
  text_content: null | string;
  title: null | string;
  description_en: null | string;
  description_sv: null | string;
  subjects: string[];
  can_ask_question: boolean;
  parse_image_upload_complete: boolean;
  classify_subjects_ok: null | boolean;
  create_search_queries_sv_ok: null | boolean;
  create_search_queries_en_ok: null | boolean;
  create_description_en_ok: null | boolean;
  create_description_sv_ok: null | boolean;
  create_title_ok: null | boolean;
  parse_image_content_ok: null | boolean;
}

export interface Hit {
  id: string;
  answer: string;
  relevance: string;
  lecture: Lecture;
}

export interface Question {
  id: string;
  hits: Hit[];
}
