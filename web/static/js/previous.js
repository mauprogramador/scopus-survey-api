import { lang, csrfToken, downloadLink } from './index.js';
import { Button } from './button.js';
import { request } from './request.js';
import { Alerts } from './alerts.js';
import { successMessages } from './translations.js';

// Get elements
const apiKeyField = document.getElementById('api-key');
const previousButton = new Button('previous-button');

// Toggle button
apiKeyField.addEventListener('input', () => {
  previousButton.toggle(apiKeyField.validity.valid);
});

// Fetch previous CSV
previousButton.button.addEventListener('click', () => {
  apiKeyField.dataset.checked = 'true';

  if (!apiKeyField.validity.valid) {
    return void 0;
  }
  previousButton.disable();

  const url = new URL(previousButton.formAction);
  url.searchParams.set('csrfToken', csrfToken);

  url.searchParams.set(apiKeyField.name, apiKeyField.value);
  url.searchParams.set(previousButton.name, previousButton.value);

  request(url, (response) => {
    if (response) {
      let csvFilename = response.headers.get('X-CSV-Filename');
      // let userAPIKey = response.headers.get('X-User-API-Key');

      return response
        .blob()
        .then((blob) => {
          const blobUrl = window.URL.createObjectURL(blob);
          downloadLink.download = csvFilename;
          downloadLink.href = blobUrl;

          downloadLink.click();
          URL.revokeObjectURL(blobUrl);
        })
        .then(() => Alerts.success(successMessages[lang].T01));
    }
  });

  previousButton.enable();
});
