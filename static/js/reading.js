// Reading page — track upgrade clicks, animate chart strip

document.addEventListener('DOMContentLoaded', function () {
  // Track upgrade CTA clicks
  document.querySelectorAll('a[href*="/subscribe"]').forEach(function (el) {
    el.addEventListener('click', function () {
      if (typeof fbq === 'function') fbq('track', 'AddToCart', { value: 17, currency: 'USD' });
      if (typeof ttq !== 'undefined') ttq.track('AddToCart');
    });
  });

  // Animate chart pills in on load
  var pills = document.querySelectorAll('.chart-pill');
  pills.forEach(function (pill, i) {
    pill.style.opacity = '0';
    pill.style.transform = 'translateY(8px)';
    setTimeout(function () {
      pill.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      pill.style.opacity = '1';
      pill.style.transform = 'translateY(0)';
    }, 80 * i);
  });

  // Track ViewContent pixel
  if (typeof fbq === 'function') fbq('track', 'ViewContent');
  if (typeof ttq !== 'undefined') ttq.track('ViewContent');
});
