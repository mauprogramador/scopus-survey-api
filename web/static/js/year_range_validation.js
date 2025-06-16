const startYearField = document.getElementById('start-year');
const endYearField = document.getElementById('end-year');

// Set Min/Max Years

let currentYear = new Date().getFullYear();
startYearField.setAttribute('max', (currentYear - 1).toString());
endYearField.setAttribute('max', currentYear.toString());

let lastDecade = currentYear - 10;
startYearField.setAttribute('min', lastDecade.toString());
endYearField.setAttribute('min', (lastDecade + 1).toString());

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
