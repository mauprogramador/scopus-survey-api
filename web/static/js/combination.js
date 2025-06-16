import { lang, csrfToken } from './index.js';
import { Button } from './button.js';
import { request } from './request.js';
import { Alerts } from './alerts.js';
import { successMessages } from './translations.js';
import { fieldsValidity } from './validation.js';

// Get elements
const surveyInputs = document.querySelectorAll('.combination-field, .keywords');
const surveySelects = document.querySelectorAll('select');
const surveyFields = document.querySelectorAll(
  '.combination-field, select, .keywords'
);
const keywordsFields = document.querySelectorAll('.keywords');
const surveyButton = new Button('survey-button');
const main = document.querySelector('main');
const tbody = document.getElementById('combination-tbody');
const template = document.getElementById('combination-row');

// Toggle button
surveyInputs.forEach((field) => {
  field.addEventListener('input', () => {
    surveyButton.toggle(fieldsValidity(surveyFields));
  });
});
surveySelects.forEach((field) => {
  field.addEventListener('change', () => {
    surveyButton.toggle(fieldsValidity(surveyFields));
  });
});

// Populate table
function populateTable(combinations) {
  combinations.forEach((combination, index) => {
    let indexNumber = index + 1;
    let clone = template.content.cloneNode(true);

    let id = `combination-choice${indexNumber}`;
    let title = `${indexNumber}th Combination field`;

    let tds = clone.querySelectorAll('td');
    let input = clone.querySelector('input');
    let label = clone.querySelector('label');

    tds[0].innerText = indexNumber;
    tds[1].title = title;
    tds[2].innerText = combination.total;

    label.for = id;
    label.innerText = combination.keyword;

    input.id = id;
    input.value = combination.keyword;
    input.title = title;
    input.ariaLabel = title;

    tbody.appendChild(clone);
  });
}

// Fetch keywords combination
surveyButton.button.addEventListener('click', () => {
  surveyFields.forEach((field) => (field.dataset.checked = 'true'));

  if (!fieldsValidity(surveyFields)) {
    return void 0;
  }
  surveyButton.disable();

  const url = new URL(surveyButton.formAction);
  url.searchParams.set('csrfToken', csrfToken);

  surveyFields.forEach((field) => {
    url.searchParams.set(field.name, field.value);
  });

  const keywords = Array.from(keywordsFields)
    .map((field) => field.value)
    .filter((keyword) => keyword.trim() !== '');

  url.searchParams.set('keywords', keywords.join(','));
  url.searchParams.set(surveyButton.name, surveyButton.value);

  main.dataset.step2 = 'hide';
  tbody.innerHTML = '';

  request(url, (response) => {
    if (response) {
      // let userAPIKey = response.headers.get('X-User-API-Key');

      return response
        .json()
        .then((json) => {
          main.dataset.step2 = 'show';
          populateTable(json['combinations']);
        })
        .then(() => Alerts.success(successMessages[lang].T02));
    }
  });

  surveyButton.enable();
});
