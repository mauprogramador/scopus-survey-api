import { lang, csrfToken, downloadLink } from './index.js';
import { Button } from './button.js';
import { request } from './request.js';
import { Alerts } from './alerts.js';
import { successMessages } from './translations.js';
import { fieldsValidity } from './validation.js';

// Get elements
const searchInputs = document.querySelectorAll('input:not([type="radio"])');
const searchSelects = document.querySelectorAll('select, input[type="radio"]');
const allFields = document.querySelectorAll('input, select');
const keywordsFields = document.querySelectorAll('.keywords');
const combinationFields = document.querySelectorAll('.combination');
const searchButton = new Button('search-button');
const downloadButton = new Button('download-button');

// Toggle button
searchInputs.forEach((field) => {
  field.addEventListener('input', () => {
    searchButton.toggle(fieldsValidity(allFields));
  });
});
searchSelects.forEach((field) => {
  field.addEventListener('change', () => {
    searchButton.toggle(fieldsValidity(allFields));
  });
});

// Fetch search
searchButton.button.addEventListener('click', () => {
  allFields.forEach((field) => (field.dataset.checked = 'true'));

  if (!fieldsValidity(allFields)) {
    return void 0;
  }

  searchButton.disable();
  downloadButton.disable();

  const url = new URL(searchButton.formAction);
  url.searchParams.set('csrfToken', csrfToken);

  allFields.forEach((field) => {
    url.searchParams.set(field.name, field.value);
  });

  const keywords = Array.from(keywordsFields)
    .map((field) => field.value)
    .filter((keyword) => keyword.trim() !== '');

  url.searchParams.set('keywords', keywords.join(','));
  const combination = Array.from(combinationFields).filter(
    (field) => field.checked
  )[0];

  url.searchParams.set(combination.name, combination.value);
  url.searchParams.set(searchButton.name, searchButton.value);

  request(url, (response) => {
    if (response.ok) {
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
        .then(() => Alerts.success(successMessages[lang].T03));
    }
  });

  searchButton.enable();
  downloadButton.enable();
});
