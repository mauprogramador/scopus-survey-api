import { inputs, handleSearchButton } from './validation.js';

const messages = {
  save: 'entered data has been saved to local storage',
  askPopulate: 'Would you like to populate input fields with stored values?',
}

// Save entered data to local storage

function storeData() {
  let hasFieldsChanged = Array.from(inputs).filter(
    (input) => input.value !== input.defaultValue
  );

  if (hasFieldsChanged.length > 0) {
    hasFieldsChanged.forEach((input) => {
      localStorage.setItem(input.id, input.value);
    });

    console.log(messages.save);
  }
}

// Save data before reload

window.addEventListener('beforeunload', (event) => {
  event.preventDefault();
  storeData();
});

// Retrieve data from local storage

window.addEventListener(
  'load',
  () => {
    window.setTimeout(() => {

      let populated = confirm(messages.askPopulate);

      Array.from(inputs).forEach((input) => {
        let storedValue = localStorage.getItem(input.id);

        if (!storedValue) {
          return void 0;
        }

        if (populated) {
          input.value = storedValue;

          input.dataset.checked = 'true';
          input.reportValidity();

          handleSearchButton();
        }

        let listId = `${input.id}-list`;
        let datalist = document.createElement('datalist');
        datalist.id = listId;

        let option = document.createElement('option');
        option.value = storedValue;
        datalist.appendChild(option);

        let formField = input.closest('.form-field');
        formField.appendChild(datalist);
        input.setAttribute('list', listId);
      });
    }, 500);
  },
  { once: true }
);

export { storeData };
