import { submit as data } from './index.js';
import { headers, interuptSearching } from './search.js';


data.form.addEventListener('submit', (event) => {
  event.preventDefault();
  const controller = new AbortController();

  data.loader.classList.add('visible');
  data.tableButton.toggleAttribute('disabled', true);
  data.searchButton.toggleAttribute('disabled', true);

  const searchURL = new URL(data.form.action);
  const formData = new FormData(data.form);
  const keywords = formData
    .getAll('keywords')
    .filter(keyword => keyword.trim() !== "");

  searchURL.searchParams.set('apikey', formData.get('apikey'));
  searchURL.searchParams.set('keywords', keywords.join(','));

  const request = new Request(searchURL, {
    method: 'GET',
    headers: headers,
    signal: controller.signal,
  });

  if (document.querySelector('dialog[open]')) {
    document.querySelector('dialog[open]').close();
  }
  window.addEventListener('beforeunload', interuptSearching);

  fetch(request).then((response) => {
    window.removeEventListener('beforeunload', interuptSearching);

    data.searchButton.toggleAttribute('disabled', false);
    data.loader.classList.remove('visible');

    if (response.ok) {

      response.blob().then((blob) => {
        window.csvBlob = blob;
        data.downloadLink.href = window.URL.createObjectURL(blob);
        data.downloadLink.click();
      });

      requestAnimationFrame(() => {
        data.successAlert.show();
        setTimeout(() => {
          data.successAlert.close();
        }, 5000);
      });

      data.tableButton.toggleAttribute('disabled', false);

    } else {
      response.json().then(json => {
        console.error(json);

        requestAnimationFrame(() => {
          data.errorDescription.innerText = json[ 'message' ];
          data.errorAlert.show();
        });
      })
    }

  }).catch((error) => {
    data.searchButton.toggleAttribute('disabled', false);
    data.loader.classList.remove('visible');

    console.error(error);

    requestAnimationFrame(() => {
      data.errorDescription.innerText = error;
      data.errorAlert.show();
    });
  })
});
