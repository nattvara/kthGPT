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
