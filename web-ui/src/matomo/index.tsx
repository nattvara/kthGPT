
export const registerPageLoad = () => {
  if (!window._paq) return;

  const _paq = window._paq || [];

  _paq.push(['setCustomUrl', window.location.pathname]);
  _paq.push(['trackPageView']);
};
