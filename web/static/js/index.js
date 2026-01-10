import { Button } from './button.js';
import { translationTexts } from './translations.js';

// Get context data
const downloadLink = document.getElementById('download-link');
const contextData = document.getElementById('context-data');
const lang = contextData.dataset.lang;
const csrfToken = contextData.dataset.csrfToken;
contextData.remove();

// Focused element state
const main = document.getElementById('main-content');
// var previousFocusedEl = main;
window.previousFocusedEl = main;

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
// - Scopus Search and Abstract Retrieval APIs weekly quota
//   https://dev.elsevier.com/api_key_settings.html
const detailsTbody = document.getElementById('details-tbody');
const detailsCache = {
  'x-api-key': null,
  'x-search-limit': 20000,
  'x-search-remaining': 20000,
  'x-search-reset': null,
  'x-search-els-status': null,
  'x-abstract-limit': 10000,
  'x-abstract-remaining': 10000,
  'x-abstract-reset': null,
  'x-abstract-els-status': null,
  'x-keywords': null,
  'x-combination': null,
  'x-total': null,
  'x-results': null,
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
    'x-results': 'Results',
    'x-pages-count': 'Pages count',
    'x-items-per-page': 'Items per page',
    'x-average-found': 'Average found',
    'x-loss': 'Loss',
    'x-process-time': 'Process time',
    'x-csv-filename': 'CSV filename',
  },
};
const apiKeyQuota = [
  'x-api-key',
  'x-search-remaining',
  'x-search-reset',
  'x-abstract-remaining',
  'x-abstract-reset',
];

function updateDetails(headers) {
  detailsCache['x-total'] = null;
  detailsCache['x-pages-count'] = null;
  detailsCache['x-items-per-page'] = null;
  detailsCache['x-average-found'] = null;
  detailsCache['x-loss'] = null;
  detailsCache['x-csv-filename'] = null;

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

  let apiKeyQuotaData = Object.entries(detailsCache).filter(([key, value]) =>
    apiKeyQuota.includes(key)
  );
  sessionStorage.setItem(
    detailsCache['x-api-key'],
    JSON.stringify(apiKeyQuotaData)
  );
}

// API Key quota, limitation, and warnings
const highResults = 300;
const pagination = 25;
const noResults = 0;

function noRemainingQuota() {
  return (
    detailsCache['x-search-remaining'] === noResults ||
    detailsCache['x-abstract-remaining'] === noResults
  );
}

function remainingQuota(total) {
  let pages_count = Math.ceil(total / pagination);
  let has_search_quota = detailsCache['x-search-remaining'] >= pages_count;
  let has_abstract_quota = detailsCache['x-abstract-remaining'] >= total;
  return has_search_quota && has_abstract_quota;
}

const searchQuotasTd = document.getElementById('search-quotas-td');
const abstractQuotasTd = document.getElementById('abstract-quotas-td');
const retrievableResultsTd = document.getElementById('retrievable-results-td');

function updateWarningsSummary(
  total = 0,
  retrievableResults = 0,
  searchQuotas = detailsCache['x-search-remaining'],
  abstractQuotas = detailsCache['x-abstract-remaining']
) {
  searchQuotasTd.innerText = `${searchQuotas.toLocaleString()} /\
    ${detailsCache['x-search-remaining'].toLocaleString()}`;
  abstractQuotasTd.innerText = `${abstractQuotas.toLocaleString()} /\
    ${detailsCache['x-abstract-remaining'].toLocaleString()}`;
  retrievableResultsTd.innerText = `${retrievableResults.toLocaleString()} /\
    ${total.toLocaleString()}`;
}

function loadApiKeyQuota(apiKey) {
  if (!sessionStorage.hasOwnProperty(apiKey)) {
    let apiKeyQuotaData = Object.entries(detailsCache).filter(([key, value]) =>
      apiKeyQuota.includes(key)
    );
    sessionStorage.setItem(apiKey, JSON.stringify(apiKeyQuotaData));
  } else {
    let storedData = JSON.parse(sessionStorage.getItem(apiKey));
    storedData.forEach(([key, value]) => {
      detailsCache[key] = value;
    });
  }
  updateWarningsSummary();
  return noRemainingQuota() ? [translationTexts[lang].W02] : [];
}

function verifyQuota(total) {
  let warnings = [];
  if (total === noResults) {
    return warnings;
  }
  if (noRemainingQuota()) {
    updateWarningsSummary(total, 0, 0, 0);
    warnings.push(translationTexts[lang].W02);
    return warnings;
  }
  let used = Math.ceil(total / pagination) + total;
  warnings.push(translationTexts[lang].W04(used.toLocaleString()));
  if (remainingQuota(total)) {
    updateWarningsSummary(total, total, Math.ceil(total / pagination), total);
    if (total >= highResults) {
      warnings.push(translationTexts[lang].W03);
      return warnings;
    }
    return warnings;
  }
  warnings.push(translationTexts[lang].W01);
  warnings.push(translationTexts[lang].W05);
  let possibleSearches = detailsCache['x-search-remaining'] * pagination;
  let allowedRequests = Math.min(
    possibleSearches,
    detailsCache['x-abstract-remaining']
  );
  let searchQuotas = 0;
  let abstractQuotas = 0;
  if (allowedRequests === possibleSearches) {
    searchQuotas = detailsCache['x-search-remaining'];
    abstractQuotas = possibleSearches;
  } else {
    searchQuotas = Math.floor(allowedRequests / pagination);
    abstractQuotas = detailsCache['x-abstract-remaining'];
  }
  updateWarningsSummary(total, allowedRequests, searchQuotas, abstractQuotas);
  if (allowedRequests >= highResults) {
    warnings.push(translationTexts[lang].W03);
  }
  return warnings;
}

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
    let totalNumber = Number(item.total);
    input.dataset.total = totalNumber;
    let totalLocale = totalNumber.toLocaleString();

    if (totalNumber === noResults || noRemainingQuota()) {
      input.disabled = true;
      tdTotal.innerText = totalLocale;
    } else if (!remainingQuota(totalNumber)) {
      tdTotal.classList.add('text-danger');
      tdTotal.ariaLabel = translationTexts[lang].W01;
      tdTotal.title = translationTexts[lang].W01;

      new bootstrap.Tooltip(tdTotal);
      tdTotal.dataset.bsToggle = 'tooltip';
      tdTotal.dataset.bsPlacement = 'top';
      tdTotal.dataset.bsTitle = translationTexts[lang].W01;

      let beyondQuota = document.createElement('s');
      beyondQuota.innerText = totalLocale;
      tdTotal.appendChild(beyondQuota);
    } else {
      tdTotal.innerText = totalLocale;
    }

    let tr = document.createElement('tr');
    tr.role = 'radio';
    tr.ariaChecked = 'false';
    tr.tabIndex = '0';
    tr.appendChild(thIndex);
    tr.appendChild(tdFormCheck);
    tr.appendChild(tdTotal);

    combTbody.appendChild(tr);
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
  combTbody,
  apiKeyField,
  allCombFields,
  keywordsFields,
  allFreshFields,
  currentFocusedEl,
  noRemainingQuota,
  remainingQuota,
  loadApiKeyQuota,
  updateWarningsSummary,
  verifyQuota,
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
  highResults,
  noResults,
  pagination,
  detailsCache,
};
