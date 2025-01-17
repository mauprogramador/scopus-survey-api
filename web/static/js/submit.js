import { lang, token } from './index.js';
import { ShowAlert } from './alerts.js';
import { searchButton } from './validation.js';
import { storeData } from './data.js';

const loader = document.getElementById('loader-dialog');
const form = document.getElementById('search-params-form');

const downloadLink = document.getElementById('download-link');
const downloadButton = document.getElementById('download-button');

const linkTable = document.getElementsByClassName('link-table');
const tableUrl = `/v2/scopus-survey/api/${lang}/articles-table`;

// Download CSV

downloadButton.addEventListener('click', () => downloadLink.click());

// Headers

const headers = {
  Accept: 'text/csv',
  'Content-Type': 'text/csv; charset=utf-8',
  'Access-Control-Allow-Origin': '*',
  'X-Access-Token': token,
};

// Submit search

form.addEventListener('submit', (event) => {
  event.preventDefault();
  const controller = new AbortController();

  requestAnimationFrame(() => loader.showModal());

  searchButton.toggleAttribute('disabled', true);
  downloadButton.toggleAttribute('disabled', true);

  searchButton.ariaDisabled = 'true';
  downloadButton.ariaDisabled = 'true';

  const searchURL = new URL(form.action);
  const formData = new FormData(form);
  const keywords = formData
    .getAll('keywords')
    .filter((keyword) => keyword.trim() !== '');

  searchURL.searchParams.set('apikey', formData.get('apikey'));
  searchURL.searchParams.set('keywords', keywords.join(','));

  const request = new Request(searchURL, {
    method: 'GET',
    headers: headers,
    signal: controller.signal,
    cache: 'no-store'
  });

  window.addEventListener('beforeunload', ShowAlert.info);

  fetch(request)
    .then((response) => {
      window.removeEventListener('beforeunload', ShowAlert.info);
      requestAnimationFrame(() => loader.close());

      searchButton.toggleAttribute('disabled', false);
      searchButton.ariaDisabled = 'false';

      if (response.ok) {
        downloadButton.toggleAttribute('disabled', false);
        downloadButton.ariaDisabled = 'false';

        let csvFilename = response.headers.get('X-CSV-Filename');
        let userAPIKey = response.headers.get('X-User-API-Key');

        response.blob().then((blob) => {
          window.csvBlob = blob;
          downloadLink.download = csvFilename;

          downloadLink.href = window.URL.createObjectURL(blob);
          downloadLink.click();

          downloadLink.href = `/v2/scopus-survey/api/csv?apikey=${userAPIKey}`;
        });

        let url = `${tableUrl}?apikey=${userAPIKey}`;

        for (let element of linkTable) {
          element.href = url;
        }

        ShowAlert.success();
        storeData();
      } else {
        response.json().then((json) => {
          console.error(json);
          ShowAlert.error(json['message']);
        });
      }
    })
    .catch((error) => {
      searchButton.toggleAttribute('disabled', false);
      downloadButton.toggleAttribute('disabled', false);

      searchButton.ariaDisabled = 'false';
      downloadButton.ariaDisabled = 'false';

      requestAnimationFrame(() => loader.close());

      console.error(error);
      ShowAlert.error(error);
    });
});
