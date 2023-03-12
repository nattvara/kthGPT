export const CATEGORY_SELECTOR = 'selector';

export const CATEGORY_ANALYSE = 'analyse';

export const CATEGORY_QUESTIONS = 'questions';

export const CATEGORY_PREVIEW = 'preview';

export const CATEGORY_URL = 'submit_url';

export const CATEGORY_LECTURE_ADDER = 'lecture_adder';

export const CATEGORY_COURSE_BROWSER = 'course_browser';

export const CATEGORY_COURSE_SELECTOR = 'course_selector';

export const CATEGORY_QUEUE_TABLE = 'queue_table';

export const CATEGORY_FAILURE_TABLE = 'failure_table';

export const CATEGORY_DENIED_TABLE = 'denied_table';

export const EVENT_ASKED_QUESTION = 'asked_question';

export const EVENT_RECEIVED_QUESTION_ANSWER = 'received_question_response';

export const EVENT_ASKED_QUESTION_NO_CACHE =
  'asked_question_with_cache_override';

export const EVENT_FEELING_LUCKY = 'feeling_lucky';

export const EVENT_SUBMIT_URL_KTH = 'url_kth';

export const EVENT_SUBMIT_URL_YOUTUBE = 'url_youtube';

export const EVENT_SUBMIT_URL_UNKNOWN = 'url_unknown';

export const EVENT_GOTO_LECTURE = 'goto_lecture';

export const EVENT_GOTO_CONTENT = 'goto_content';

export const EVENT_GOTO_COURSE = 'goto_course';

export const EVENT_ERROR_RESPONSE = 'error_response';

export const ACTION_NONE = '_';

export const registerPageLoad = async () => {
  const _paq = window._paq || [];

  _paq.push(['setCustomUrl', window.location.pathname]);
  _paq.push(['trackPageView']);
};

export const emitEvent = async (
  category: string,
  event: string,
  action: string
) => {
  const _paq = window._paq || [];

  _paq.push(['trackEvent', category, event, action]);
};
