
export const EVENT_ASKED_QUESTION = 'asked question';

export const EVENT_ASKED_QUESTION_NO_CACHE = 'asked question, with cache-override';

export const EVENT_FEELING_LUCKY = 'feeling lucky';

export const EVENT_SUBMIT_URL = 'submit url';

export const EVENT_GOTO_LECTURE = 'goto lecture';


export const registerPageLoad = () => {
  if (!window._paq) return;

  const _paq = window._paq || [];

  _paq.push(['setCustomUrl', window.location.pathname]);
  _paq.push(['trackPageView']);
};

export const emitEvent = (event: string) => {
  if (!window._paq) return;

  var _paq = window._paq || [];

  _paq.push(['trackEvent', event, '', '']);
};
