export interface Image {
  id: string;
  created_at: Date;
  modified_at: Date;
  text_content: null | string;
  description: null | string;
  create_search_queries_sv_ok: null | boolean;
  create_search_queries_en_ok: null | boolean;
  create_description_ok: null | boolean;
  parse_image_content_ok: null | boolean;
}
