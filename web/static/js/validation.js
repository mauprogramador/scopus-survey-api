import { lang } from './index.js';

// Turn on checked & validity
document.querySelectorAll('input:not([type="radio"])').forEach((field) => {
  field.addEventListener('input', () => (field.dataset.checked = 'true'), {
    once: true,
  });
  field.addEventListener('input', () => field.reportValidity());
});
document.querySelectorAll('select, input[type="radio"]').forEach((field) => {
  field.addEventListener('change', () => (field.dataset.checked = 'true'), {
    once: true,
  });
  field.addEventListener('change', () => field.reportValidity());
});

// Check all fields validity
function fieldsValidity(fields) {
  return Array.from(fields).every((field) => field.validity.valid);
}

const searchButton = document.getElementById('search-button');
const inputs = document.querySelectorAll('input');

// Search Button

searchButton.addEventListener('click', () => {
  inputs.forEach((input) => (input.dataset.checked = 'true'));
});

function handleSearchButton() {
  let fieldsValid = Array.from(inputs).every((input) => input.validity.valid);
  if (fieldsValid) {
    searchButton.toggleAttribute('disabled', false);
    searchButton.ariaDisabled = 'false';
  } else {
    searchButton.toggleAttribute('disabled', true);
    searchButton.ariaDisabled = 'true';
  }
}

// Inputs checked

inputs.forEach((input) => {
  input.addEventListener('input', () => {
    handleSearchButton();
  });
});

// Fields Validation

for (let field of inputs) {
  field.addEventListener('invalid', () => {
    let feedbackSpan = field
      .closest('.form-field')
      .querySelector('.input-feedback');
    let feedbacks = [];

    Object.entries(errorFeedbacks[lang]).forEach(([error, feedback]) => {
      if (field.validity[error]) {
        feedbacks.push(feedback);
      }
    });

    if (feedbacks.length > 0) {
      console.error(`${field.name}: ${feedbacks[0]}`);
      field.setCustomValidity(feedbacks[0]);

      feedbackSpan.innerHTML = feedbacks[0];
      field.ariaInvalid = true;
    } else {
      field.setCustomValidity('');
      feedbackSpan.innerHTML = '';
      field.ariaInvalid = false;
    }

    handleSearchButton();
  });
}

export { searchButton, handleSearchButton, inputs, fieldsValidity };
