import { inputs, handleSearchButton } from './validation.js';

const message = 'Input fields have been populated with stored values';

// Save all entered data to local storage

window.addEventListener('beforeunload', (event) => {
  event.preventDefault();

  let hasFieldsChanged = Array.from(inputs).filter(
    (input) => input.value !== input.defaultValue
  );

  if (hasFieldsChanged.length > 0) {
    hasFieldsChanged.forEach((input) => {
      localStorage.setItem(input.id, input.value);
    });
  }
});

// Retrieve data from local storage

let populated = confirm('Populate input fields with stored values?');
let wasFilled = false;

Array.from(inputs).forEach((input) => {
  let storedValue = localStorage.getItem(input.id);

  if (!storedValue) {
    return void 0;
  }

  if (populated) {
    wasFilled = true;
    input.value = storedValue;

    input.dataset.checked = 'true';
    input.reportValidity();
    handleSearchButton();
  }

  let listId = `${input.name}-list`;
  let datalist = document.createElement('datalist');
  datalist.id = listId;

  let option = document.createElement('option');
  option.value = storedValue;
  datalist.appendChild(option);

  let formField = input.closest('.form-field');
  formField.appendChild(datalist);
  input.setAttribute('list', listId);
});

if (wasFilled) {
  console.log(message);
  setTimeout(() => alert(message), 100);
}
