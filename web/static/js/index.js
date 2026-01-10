import { Button } from './button.js';

// Get context data
const downloadLink = document.getElementById('download-link');
const contextData = document.getElementById('context-data');
const lang = contextData.dataset.lang;
const csrfToken = contextData.dataset.csrfToken;
contextData.remove();

// Focused element state
const main = document.getElementById('main-content');
window.PreviousFocusedEl = main;

function currentFocusedEl() {
  if (document.activeElement && document.activeElement !== document.body) {
    document.activeElement.blur();
    return document.activeElement;
  } else {
    main.blur();
    return main;
  }
}

// Populate Details
const detailsTbody = document.getElementById('details-tbody');
const detailsCache = {
  'x-api-key': null,
  'x-search-limit': null,
  'x-search-remaining': null,
  'x-search-reset': null,
  'x-search-els-status': null,
  'x-abstract-limit': null,
  'x-abstract-remaining': null,
  'x-abstract-reset': null,
  'x-abstract-els-status': null,
  'x-keywords': null,
  'x-combination': null,
  'x-total': null,
  'x-pages-count': null,
  'x-items-per-page': null,
  'x-average-found': null,
  'x-loss': null,
  'x-process-time': null,
  'x-csv-filename': null,
};
const detailsGroupLabels = {
  'API Key': {
    'x-api-key': 'API Key',
    'x-search-limit': 'Search limit',
    'x-search-remaining': 'Search remaining',
    'x-search-reset': 'Search reset',
    'x-search-els-status': 'Search ELS status',
    'x-abstract-limit': 'Abstract limit',
    'x-abstract-remaining': 'Abstract remaining',
    'x-abstract-reset': 'Abstract reset',
    'x-abstract-els-status': 'Abstract ELS status',
  },
  Survey: {
    'x-keywords': 'Keywords',
    'x-combination': 'Combination',
    'x-total': 'Total',
    'x-pages-count': 'Pages count',
    'x-items-per-page': 'Items per page',
    'x-average-found': 'Average found',
    'x-loss': 'Loss',
    'x-process-time': 'Process time',
    'x-csv-filename': 'CSV filename',
  },
};

function updateDetails(headers) {
  for (let key in detailsCache) {
    detailsCache[key] = null;
  }
  detailsTbody.innerHTML = '';

  headers.forEach((headerValue, headerName) => {
    if (detailsCache.hasOwnProperty(headerName)) {
      detailsCache[headerName] = headerValue;
    }
  });

  Object.entries(detailsGroupLabels).forEach(([groupName, groupLabels]) => {
    let thGroupLabel = document.createElement('th');
    thGroupLabel.classList.add('group-header');
    thGroupLabel.scope = 'row';
    thGroupLabel.colSpan = '2';
    thGroupLabel.innerText = groupName;

    let trGroupLabel = document.createElement('tr');
    trGroupLabel.appendChild(thGroupLabel);
    detailsTbody.appendChild(trGroupLabel);

    Object.entries(groupLabels)
      .filter((item) => detailsCache[item[0]] !== null)
      .forEach(([headerName, headerLabel]) => {
        let tdHeaderName = document.createElement('td');
        tdHeaderName.innerText = headerLabel;

        let tdHeaderValue = document.createElement('td');
        tdHeaderValue.innerText = detailsCache[headerName];

        let tr = document.createElement('tr');
        tr.appendChild(tdHeaderName);
        tr.appendChild(tdHeaderValue);
        detailsTbody.appendChild(tr);
      });
  });
}

// Buttons
const prevSurveyBtn = new Button('#prevsurvey-button');
const survCombBtn = new Button('#survcomb-button');
const survCombDetailsBtn = new Button('#survcombdetls-button');
const survDocsBtn = new Button('#survdocs-button');
const downloadBtn = new Button('#download-button');
const survDocsDetailsBtn = new Button('#survdocsdetls-button');

// Fields
const apiKeyField = document.getElementById('apikey');
const allCombFields = document.querySelectorAll('.combfield, .keywords');
const keywordsFields = document.querySelectorAll('.keywords');
const allFreshFields = {
  elements: document.querySelectorAll('input:not(template input), select'),
  get() {
    if (combTbody.childElementCount === 0) {
      return this.elements;
    }
    this.elements = document.querySelectorAll(
      'input:not(template input), select'
    );
    return this.elements;
  },
};

// Final step
const combTableSection = document.getElementById('combination-table-section');
const formStep3 = document.getElementById('form-step-3');
const thresholdField = document.getElementById('threshold');
const inputEvent = new InputEvent('input', {
  bubbles: true,
  inputType: 'deleteContent',
  data: null,
});

function hideFinalStep() {
  combTableSection.toggleAttribute('hidden', true);
  formStep3.toggleAttribute('hidden', true);
  combTbody.innerHTML = '';

  thresholdField.value = '';
  thresholdField.dispatchEvent(inputEvent);
  thresholdField.dataset.checked = 'false';
  thresholdField.ariaInvalid = 'false';
  thresholdField.setCustomValidity('');

  let fieldFeedback = thresholdField
    .closest('.field-container')
    .querySelector('.field-feedback');
  fieldFeedback.toggleAttribute('hidden', true);
  fieldFeedback.innerHTML = '';
  // Include Max Count in future

  survDocsBtn.disable();
  downloadBtn.disable();
  survDocsDetailsBtn.disable();
}

function showFinalStep() {
  combTableSection.toggleAttribute('hidden', false);
  formStep3.toggleAttribute('hidden', false);
}

export {
  lang,
  main,
  csrfToken,
  downloadLink,
  startYearField,
  endYearField,
  errorRawJson,
  combTbody,
  apiKeyField,
  allCombFields,
  keywordsFields,
  allFreshFields,
  currentFocusedEl,
  updateDetails,
  populateTable,
  hideFinalStep,
  showFinalStep,
  prevSurveyBtn,
  survCombBtn,
  survCombDetailsBtn,
  survDocsBtn,
  downloadBtn,
  survDocsDetailsBtn,
};
