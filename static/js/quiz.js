// Quiz form — city autocomplete + form submission state

document.addEventListener('DOMContentLoaded', function () {
  const cityInput = document.getElementById('birth_city');
  const countryInput = document.getElementById('country_code');
  const dropdown = document.getElementById('city-suggestions');
  const form = document.getElementById('quiz-form');
  const submitBtn = document.getElementById('submit-btn');
  const loadingMsg = document.getElementById('loading-msg');

  // ── City autocomplete via Open-Meteo geocoding (no key required) ──────
  let debounceTimer;

  if (cityInput) {
    cityInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      const q = cityInput.value.trim();
      if (q.length < 2) {
        dropdown.style.display = 'none';
        return;
      }
      debounceTimer = setTimeout(function () {
        fetch(
          'https://geocoding-api.open-meteo.com/v1/search?name=' +
            encodeURIComponent(q) +
            '&count=6&language=en&format=json'
        )
          .then(function (r) { return r.json(); })
          .then(function (data) {
            dropdown.innerHTML = '';
            if (!data.results || !data.results.length) {
              dropdown.style.display = 'none';
              return;
            }
            data.results.forEach(function (place) {
              var item = document.createElement('div');
              item.className = 'autocomplete-item';
              var display =
                place.name +
                (place.admin1 ? ', ' + place.admin1 : '') +
                (place.country ? ', ' + place.country : '');
              item.textContent = display;
              item.addEventListener('click', function () {
                cityInput.value = place.name;
                countryInput.value = place.country_code || 'US';
                dropdown.style.display = 'none';
              });
              dropdown.appendChild(item);
            });
            dropdown.style.display = 'block';
          })
          .catch(function () { dropdown.style.display = 'none'; });
      }, 300);
    });

    document.addEventListener('click', function (e) {
      if (!cityInput.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
      }
    });
  }

  // ── Form submission state ──────────────────────────────────────────────
  if (form) {
    form.addEventListener('submit', function () {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Reading the sky…';
      if (loadingMsg) loadingMsg.style.display = 'block';

      if (typeof fbq === 'function') fbq('track', 'Lead');
      if (typeof ttq !== 'undefined') ttq.track('SubmitForm');
    });
  }
});
