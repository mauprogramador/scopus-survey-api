import { lang } from './index.js';

const startYearField = document.getElementById('start-year');
const endYearField = document.getElementById('end-year');
const searchButton = document.getElementById('search-button');
const inputs = document.querySelectorAll('input');

// Set Min/Max Years

let currentYear = new Date().getFullYear();
startYearField.setAttribute('max', (currentYear - 1).toString());
endYearField.setAttribute('max', currentYear.toString());

let lastDecade = currentYear - 10;
startYearField.setAttribute('min', lastDecade.toString());
endYearField.setAttribute('min', (lastDecade + 1).toString());

// Inputs checked

inputs.forEach((input) => {
  input.addEventListener('input', () => (input.dataset.checked = 'true'), {
    once: true,
  });
  input.addEventListener('input', () => {
    input.reportValidity();
    handleSearchButton();
  });
});

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

// Error Feedbacks

const errorFeedbacks = {
  'en-US': {
    valueMissing: 'Fill in this required field',
    patternMismatch: 'Value with invalid pattern',
    typeMismatch: 'Value with invalid type',
    tooLong: 'Value too long',
    tooShort: 'Value too short',
    rangeOverflow: 'Value greater than maximum',
    rangeUnderflow: 'Value less than minimum',
  },
  'pt-BR': {
    valueMissing: 'Preencha este campo obrigatório',
    patternMismatch: 'Valor com padrão inválido',
    typeMismatch: 'Valor com tipo inválido',
    tooShort: 'Valor muito curto',
    tooLong: 'Valor muito longo',
    rangeOverflow: 'Valor maior que o máximo',
    rangeUnderflow: 'Valor menor que o mínimo',
  },
  year: {
    noInterval: 'Interval must be at least one year',
    'start-year': 'Start Year must be less than End Year',
    'end-year': 'End Year must be greater than Start Year',
  }
};

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

// Year Range Validation

for (let yearField of [startYearField, endYearField]) {
  yearField.addEventListener('input', () => {
    let feedbackSpan = startYearField
      .closest('.form-field')
      .querySelector('.input-feedback');

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

      console.error(`year: ${feedback}`);
      yearField.setCustomValidity(feedback);

      feedbackSpan.innerHTML = feedback;
      yearField.ariaInvalid = true;
    } else if (yearDifference === 0) {
      let feedback = errorFeedbacks.year.noInterval;

      console.error(`year: ${feedback}`);
      yearField.setCustomValidity(feedback);

      feedbackSpan.innerHTML = feedback;
      yearField.ariaInvalid = true;
    } else {
      yearField.setCustomValidity('');
      feedbackSpan.innerHTML = '';
      yearField.ariaInvalid = false;
    }
  });
}

export { searchButton, handleSearchButton, inputs };
