
export const EVENT_ASKED_QUESTION = 'asked_question';

export const EVENT_ASKED_QUESTION_NO_CACHE = 'asked_question_with_cache_override';

export const EVENT_FEELING_LUCKY = 'feeling_lucky';

export const EVENT_SUBMIT_URL = 'submit_url';

export const EVENT_GOTO_LECTURE = 'goto_lecture';

export const EVENT_GOTO_COURSE = 'goto_course';

export const ACTION_NONE = '_';


export const registerPageLoad = async () => {
  if (!window._paq) return;

  const _paq = window._paq || [];

  _paq.push(['setCustomUrl', window.location.pathname]);
  _paq.push(['trackPageView']);
};

export const emitEvent = async (event: string, action: string) => {
  if (!window._paq) return;

  var _paq = window._paq || [];

  _paq.push(['trackEvent', 'kthgpt', event, action]);
};
