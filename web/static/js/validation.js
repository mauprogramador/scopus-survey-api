import {
  lang,
  prevSurveyBtn,
  survCombBtn,
  survDocsBtn,
  combTbody,
  allCombFields,
  allFreshFields,
  loadApiKeyQuota,
  verifyQuota,
} from './index.js';
import { translationTexts, errorFeedbacks } from './translations.js';
import { showWarning } from './overlays.js';

// Multi-Step Form
const form = document.getElementById('survey-form');

// Set Min/Max Years
const startYearField = document.getElementById('startyear');
const endYearField = document.getElementById('endyear');

const currentYear = new Date().getFullYear();
startYearField.setAttribute('max', (currentYear - 1).toString());
endYearField.setAttribute('max', currentYear.toString());

const maxRecentPublications = 15;
const publicationsPastTimeLimit = currentYear - maxRecentPublications;
startYearField.setAttribute('min', publicationsPastTimeLimit.toString());
endYearField.setAttribute('min', (publicationsPastTimeLimit + 1).toString());

// Fields Validity
function fieldsValidity(fields) {
  return Array.from(fields).every(
    (field) => field.validity.valid && field.ariaInvalid === 'false'
  );
}

// Year Range
function validateYearRange(field) {
  console.log(field);

  let startYearChange = startYearField.value === startYearField.defaultValue;
  let endYearChange = endYearField.value === endYearField.defaultValue;

  console.log(startYearChange, endYearChange);

  if (startYearChange && endYearChange) {
    return '';
  }
  if (startYearField.value > endYearField.value) {
    return errorFeedbacks[lang][field.name];
  }
  let yearDifference = Math.abs(endYearField.value - startYearField.value);
  if (yearDifference === 0) {
    return errorFeedbacks[lang].noInterval;
  }
  return '';
}

// Keywords Operators
function validateKeywordsOperators(field) {
  if (field.value === field.defaultValue) {
    return '';
  }
  let text = field.value.trim();

  let wildcardMatches = text.match(/[?*]/g);
  if (wildcardMatches) {
    wildcardMatches.forEach((wildcard, index) => {
      let wildcardPos = text.indexOf(wildcard);

      if (wildcardPos === 0 && text.length === 1) {
        return translationTexts[lang].E01(wildcard);
      }
      if (wildcardPos === text.length - 1 && text.length === 1) {
        return translationTexts[lang].E02(wildcard);
      }
      if (wildcardPos > 0 && wildcardPos < text.length - 1) {
        let beforeChar = text[wildcardPos - 1];
        let afterChar = text[wildcardPos + 1];

        if (!/\w/.test(beforeChar) && !/\w/.test(afterChar)) {
          return translationTexts[lang].E03(wildcard);
        }
      }
    });
  }

  let quoteCount = (text.match(/"/g) || []).length;
  if (quoteCount > 0) {
    if (quoteCount % 2 !== 0) {
      return translationTexts[lang].E04;
    }
    if (text.match(/""/g)) {
      return translationTexts[lang].E05;
    }
    if (text.match(/"\s+"/g)) {
      return translationTexts[lang].E06;
    }
  }

  let openBraceCount = (text.match(/{/g) || []).length;
  let closeBraceCount = (text.match(/}/g) || []).length;
  if (openBraceCount > 0 || closeBraceCount > 0) {
    if (openBraceCount !== closeBraceCount) {
      return translationTexts[lang].E07;
    }
    if (text.match(/{}/g)) {
      return translationTexts[lang].E08;
    }
    if (text.match(/{\s+}/g)) {
      return translationTexts[lang].E09;
    }
  }
  return '';
}

// Check for Extra Spaces
function validateExtraSpaces(field) {
  if (field.value === field.defaultValue) {
    return '';
  }
  if (/\s{2,}/.test(field.value)) {
    return errorFeedbacks.multipleSpaces;
  }
  return '';
}

// Show Error Feedback
function showErrorFeedback(field, feedback = '') {
  let fieldFeedback = field
    .closest('.field-container')
    .querySelector('.field-feedback');

  if (feedback.trim() === '') {
    for (const [key, value] of Object.entries(errorFeedbacks[lang])) {
      if (field.validity[key]) {
        feedback = errorFeedbacks[lang][key];
        break;
      }
    }
  }
  if (feedback.length > 0) {
    field.setCustomValidity(feedback);
    field.ariaInvalid = 'true';

    console.error(`${field.name}: ${feedback}`);
    fieldFeedback.innerText = feedback;
    fieldFeedback.toggleAttribute('hidden', false);
  } else {
    field.setCustomValidity('');
    field.ariaInvalid = 'false';

    fieldFeedback.toggleAttribute('hidden', true);
    fieldFeedback.innerHTML = '';
  }
}

// Check validity and toggle buttons
function toggleValidity(field) {
  let feedback = '';

  if (field.matches('#apikey')) {
    prevSurveyBtn.toggle(field.validity.valid);
    if (field.validity.valid) {
      let warnings = loadApiKeyQuota(field.value);
      if (warnings.length > 0) {
        showWarning(warnings);
      }
    }
  } else if (field.matches('#startyear, #endyear')) {
    feedback = validateYearRange(field);
  } else if (field.matches('#language, .keywords')) {
    if (field.matches('.keywords')) {
      feedback = validateKeywordsOperators(field);
    }
    feedback = validateExtraSpaces(field);
  }
  showErrorFeedback(field, feedback);

  if (field.matches('.combfield, .keywords')) {
    survCombBtn.toggle(fieldsValidity(allCombFields));
  }
  if (field.matches('select, input:not([type="radio"]:disabled)')) {
    field.dataset.checked = 'true';
    field.reportValidity();

    let validity = fieldsValidity(allFreshFields.get());
    let hasRadios = combTbody.childElementCount > 0;
    survDocsBtn.toggle(validity && hasRadios);
  }
}

form.addEventListener('input', (event) => {
  if (event.target.matches('input:not([type="radio"])')) {
    toggleValidity(event.target);
  }
});
form.addEventListener('change', (event) => {
  if (
    event.target.matches(
      'input[type="number"], select, input[type="radio"]:not(:disabled)'
    )
  ) {
    toggleValidity(event.target);
  }
});

combTbody.addEventListener('change', (event) => {
  if (event.target.matches('input[type="radio"]:not(:disabled)')) {
    let total = event.target.dataset.total;
    let warnings = verifyQuota(Number(total));

    if (warnings.length > 0) {
      showWarning(warnings);
    }
  }
});

// No remaining quota
function noRadios() {
  let radios = combTbody.querySelectorAll('input[type="radio"]');
  let allDisable = Array.from(radios).every(radio => radio.disabled);
  if (allDisable) {
    survDocsBtn.disable();
    showWarning(translationTexts[lang].W06);
  }
}

export { fieldsValidity, noRadios };
