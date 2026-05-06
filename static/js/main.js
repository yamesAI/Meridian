// Global JS — pixel helpers, utility functions

function trackEvent(eventName, params) {
  if (typeof fbq === 'function') {
    fbq('track', eventName, params || {});
  }
  if (typeof ttq !== 'undefined' && typeof ttq.track === 'function') {
    ttq.track(eventName, params || {});
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // FAQ smooth open/close
  document.querySelectorAll('details.faq__item').forEach(function (el) {
    el.addEventListener('toggle', function () {
      if (el.open) {
        document.querySelectorAll('details.faq__item').forEach(function (other) {
          if (other !== el) other.removeAttribute('open');
        });
      }
    });
  });
});
