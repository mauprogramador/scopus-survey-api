import {
  lang,
  prevSurveyBtn,
  survCombBtn,
  survDocsBtn,
  combTbody,
  startYearField,
  endYearField,
  apiKeyField,
  allCombFields,
  keywordsFields,
  allFreshFields,
} from './index.js';
import { errorFeedbacks } from './translations.js';

const form = document.getElementById('survey-form');

// Fields Validity
function fieldsValidity(fields) {
  return Array.from(fields).every((field) => field.validity.valid);
}

// Toggle prevSurveyBtn
apiKeyField.addEventListener('input', () => {
  prevSurveyBtn.toggle(apiKeyField.validity.valid);
});

// Reactive SurvDocsBtn
function toggleSurvDocsBtn() {
  let validity = fieldsValidity(allFreshFields.get());
  let hasRadios = combTbody.childElementCount > 0;
  survDocsBtn.toggle(validity && hasRadios);
}

// Checked, report validity, toggle buttons on Input
form.addEventListener('input', (event) => {
  if (event.target.matches('input.combfield, .keywords')) {
    survCombBtn.toggle(fieldsValidity(allCombFields));
  }
  if (event.target.matches('input:not([type="radio"])')) {
    event.target.dataset.checked = 'true';
    event.target.reportValidity();
    toggleSurvDocsBtn();
  }
});

// Checked, report validity, toggle buttons on Change
form.addEventListener('change', (event) => {
  if (event.target.matches('select')) {
    survCombBtn.toggle(fieldsValidity(allCombFields));
  }
  if (event.target.matches('select, input[type="radio"]')) {
    event.target.dataset.checked = 'true';
    event.target.reportValidity();
    toggleSurvDocsBtn();
  }
});

// Show error feedback
document.querySelectorAll('input, select').forEach((field) => {
  field.addEventListener('invalid', () => {
    let fieldFeedback = field
      .closest('.field-container')
      .querySelector('.field-feedback');
    let feedbacks = [];

    Object.entries(errorFeedbacks[lang]).forEach(([error, feedback]) => {
      if (field.validity[error]) {
        feedbacks.push(feedback);
      }
    });

    if (feedbacks.length > 0) {
      field.setCustomValidity(feedbacks[0]);
      field.ariaInvalid = true;

      console.error(`${field.name}: ${feedbacks[0]}`);
      fieldFeedback.innerText = feedbacks[0];
      fieldFeedback.toggleAttribute('hidden', false);
    } else {
      field.setCustomValidity('');
      field.ariaInvalid = false;

      fieldFeedback.toggleAttribute('hidden', true);
      fieldFeedback.innerHTML = '';
    }
  });
});

// Year Range
const dateFeedback = document.getElementById('date-feedback');

Array.from([startYearField, endYearField]).forEach((yearField) => {
  yearField.addEventListener('input', () => {
    let startYearChange = startYearField.value !== startYearField.defaultValue;
    let endYearChange = endYearField.value !== endYearField.defaultValue;

    let yearDifference = Math.abs(endYearField.value - startYearField.value);
    let startYearValid = startYearChange && startYearField.validity.valid;
    let endYearValid = endYearChange && endYearField.validity.valid;

    if (!startYearValid || !endYearValid) {
      return void 0;
    }

    if (startYearField.value > endYearField.value) {
      let feedback = errorFeedbacks.year[yearField.name];

      yearField.setCustomValidity(feedback);
      yearField.ariaInvalid = true;

      console.error(`year: ${feedback}`);
      dateFeedback.innerText = feedback;
    } else if (yearDifference === 0) {
      let feedback = errorFeedbacks.year.noInterval;

      yearField.setCustomValidity(feedback);
      yearField.ariaInvalid = true;

      console.error(`year: ${feedback}`);
      dateFeedback.innerText = feedback;
    } else {
      yearField.setCustomValidity('');
      yearField.ariaInvalid = false;
      dateFeedback.innerHTML = '';
    }
  });
});

// Keywords Operators
keywordsFields.forEach((field) => {
  field.addEventListener('input', () => {
    let fieldChange = field.value !== field.defaultValue;
    let fieldValid = fieldChange && field.validity.valid;

    if (!fieldValid || !field.value.trim()) {
      return void 0;
    }

    let text = field.value.trim();
    let errors = [];

    let wildcardMatches = text.match(/[?*]/g);
    if (wildcardMatches) {
      wildcardMatches.forEach((wildcard, index) => {
        let wildcardPos = text.indexOf(wildcard);

        if (wildcardPos === 0 && text.length === 1) {
          errors.push(`Wildcard '${wildcard}' must have text after it`);
        } else if (wildcardPos === text.length - 1 && text.length === 1) {
          errors.push(`Wildcard '${wildcard}' must have text before it`);
        } else if (wildcardPos > 0 && wildcardPos < text.length - 1) {
          let beforeChar = text[wildcardPos - 1];
          let afterChar = text[wildcardPos + 1];

          if (!/\w/.test(beforeChar) && !/\w/.test(afterChar)) {
            errors.push(
              `Wildcard '${wildcard}' must have text before or after it`
            );
          }
        }
      });
    }

    let quoteCount = (text.match(/"/g) || []).length;
    if (quoteCount > 0) {
      if (quoteCount % 2 !== 0) {
        errors.push('Unmatched double quotation marks');
      } else {
        if (text.match(/""/g)) {
          errors.push('Quoted text cannot be empty');
        }

        if (text.match(/"\s+"/g)) {
          errors.push('Quoted text cannot contain only spaces');
        }
      }
    }

    let openBraceCount = (text.match(/{/g) || []).length;
    let closeBraceCount = (text.match(/}/g) || []).length;
    if (openBraceCount > 0 || closeBraceCount > 0) {
      if (openBraceCount !== closeBraceCount) {
        errors.push('Unmatched curly braces');
      } else {
        if (text.match(/{}/g)) {
          errors.push('Braced text cannot be empty');
        }

        if (text.match(/{\s+}/g)) {
          errors.push('Braced text cannot contain only spaces');
        }
      }
    }

    let fieldFeedback = field
      .closest('.field-container')
      .querySelector('.field-feedback');

    if (errors.length > 0) {
      field.setCustomValidity(errors[0]);
      field.ariaInvalid = true;

      console.error(`${field.name}: ${errors[0]}`);
      fieldFeedback.innerText = errors[0];
    } else {
      field.setCustomValidity('');
      fieldFeedback.innerHTML = '';
      field.ariaInvalid = false;
    }
  });
});

export { fieldsValidity };
