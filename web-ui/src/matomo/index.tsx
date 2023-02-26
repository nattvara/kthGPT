
export const CATEGORY_SELECTOR = 'selector';

export const CATEGORY_ANALYSE = 'analyse';

export const CATEGORY_QUESTIONS = 'questions';

export const CATEGORY_PREVIEW = 'preview';

export const CATEGORY_ADDER = 'adder';

export const CATEGORY_COURSE_BROWSER = 'course_browser';

export const EVENT_ASKED_QUESTION = 'asked_question';

export const EVENT_ASKED_QUESTION_NO_CACHE = 'asked_question_with_cache_override';

export const EVENT_FEELING_LUCKY = 'feeling_lucky';

export const EVENT_SUBMIT_URL = 'submit_url';

export const EVENT_GOTO_LECTURE = 'goto_lecture';

export const EVENT_GOTO_CONTENT = 'goto_content';

export const EVENT_GOTO_COURSE = 'goto_course';

export const ACTION_NONE = '_';


export const registerPageLoad = async () => {
  const _paq = window._paq || [];

  _paq.push(['setCustomUrl', window.location.pathname]);
  _paq.push(['trackPageView']);
};

export const emitEvent = async (category: string, event: string, action: string) => {
  const _paq = window._paq || [];

  _paq.push(['trackEvent', category, event, action]);
};
