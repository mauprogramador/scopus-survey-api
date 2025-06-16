import { csrfToken } from './index.js';
import { Alerts } from './alerts.js';

// Headers
const headers = {
  Accept: 'text/csv',
  'Content-Type': 'text/csv; charset=utf-8',
  'Access-Control-Allow-Origin': '*',
  'X-CSRF-Token': csrfToken,
};

// Fetch request
function request(url, callback) {
  const controller = new AbortController();

  const request = new Request(url, {
    method: 'GET',
    headers: headers,
    signal: controller.signal,
    cache: 'no-store',
  });

  window.addEventListener('beforeunload', Alerts.info);
  Alerts.startLoader();

  fetch(request)
    .then((response) => {
      window.removeEventListener('beforeunload', Alerts.info);
      Alerts.endLoader();

      if (response.ok) {
        return callback(response);
      } else {
        response
          .json()
          .then((json) => {
            console.error(json);
            Alerts.error(json['message']);
          })
          .catch((error) => console.error(error));
        return void 0;
      }
    })
    .catch((error) => {
      Alerts.endLoader();

      console.error(error);
      Alerts.error(error);

      return void 0;
    });
}

export { request };
