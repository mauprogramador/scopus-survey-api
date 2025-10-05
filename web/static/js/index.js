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

// Handle dropdown translate menu
const translateButton = new Button('#translate-button');
const translateDropdown = document.getElementById('translate-dropdown');

translateButton.button.addEventListener('shown.bs.dropdown', () => {
  translateDropdown.focus();
  translateDropdown.ariaExpanded = 'true';
  translateButton.ariaActive();
});

translateButton.button.addEventListener('hidden.bs.dropdown', () => {
  translateButton.button.focus();
  translateDropdown.ariaExpanded = 'false';
  translateButton.ariaInactive();
});

// Set Min/Max Years
const startYearField = document.getElementById('startyear');
const endYearField = document.getElementById('endyear');

let currentYear = new Date().getFullYear();
startYearField.setAttribute('max', (currentYear - 1).toString());
endYearField.setAttribute('max', currentYear.toString());

let lastDecade = currentYear - 10;
startYearField.setAttribute('min', lastDecade.toString());
endYearField.setAttribute('min', (lastDecade + 1).toString());

// Populate Combinations
const combTbody = document.getElementById('combination-tbody');
const template = document.getElementById('combination-row-opt');

function populateTable(combinations) {
  combinations.forEach((item) => {
    let clone = template.content.cloneNode(true);
    let id = `combination-opt${item.index}`;

    let input = clone.querySelector('input');
    input.id = id;
    input.value = item.combination;

    let label = clone.querySelector('label');
    label.htmlFor = id;
    label.innerText = item.combination;

    let thIndex = document.createElement('th');
    thIndex.scope = 'row';
    thIndex.innerText = item.index;

    let tdFormCheck = document.createElement('td');
    tdFormCheck.appendChild(clone);

    let tdTotal = document.createElement('td');
    tdTotal.innerText = Number(item.total).toLocaleString();

    let tr = document.createElement('tr');
    tr.appendChild(thIndex);
    tr.appendChild(tdFormCheck);
    tr.appendChild(tdTotal);

    combTbody.appendChild(tr);
  });
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
  'x-keywords-combination': null,
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
    'x-keywords-combination': 'Keywords combination',
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

// Handle modal
const detailsModal = document.getElementById('details-modal');
detailsModal.querySelector('.btn-close').addEventListener('click', (event) => {
  event.target.blur();
});

detailsModal.addEventListener('show.bs.modal', () => {
  window.PreviousFocusedEl = currentFocusedEl();
  main.setAttribute('aria-hidden', 'true');
  main.inert = true;

  detailsModal.toggleAttribute('hidden', false);
  detailsModal.ariaExpanded = 'true';
  detailsModal.focus();

  survCombDetailsBtn.ariaActive();
  survDocsDetailsBtn.ariaActive();
});

detailsModal.addEventListener('hidden.bs.modal', () => {
  detailsModal.toggleAttribute('hidden', true);
  detailsModal.ariaExpanded = 'false';

  main.setAttribute('aria-hidden', 'false');
  main.inert = false;

  survCombDetailsBtn.ariaInactive();
  survDocsDetailsBtn.ariaInactive();
  window.PreviousFocusedEl.focus();
});

// Handle accordion
const accordionJsonButton = new Button('#accordion-json-button');
const jsonTreeCollapse = document.getElementById('json-tree-collapse');
const errorRawJson = document.getElementById('error-raw-json');

jsonTreeCollapse.addEventListener('shown.bs.collapse', () => {
  jsonTreeCollapse.ariaExpanded = 'true';
  accordionJsonButton.ariaActive();
  errorRawJson.focus();
});

jsonTreeCollapse.addEventListener('hidden.bs.collapse', () => {
  accordionJsonButton.button.focus();
  accordionJsonButton.ariaInactive();
  jsonTreeCollapse.ariaExpanded = 'false';
});

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
