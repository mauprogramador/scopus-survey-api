import { validation as data } from './index.js';


data.searchButton.addEventListener('click', () => {
  data.inputs.forEach(input => input.classList.add('checked'));
});


data.inputs.forEach(input => {

  input.addEventListener('input', () => {
    input.classList.add('checked');

    if (input.checkValidity()) {
      input.setCustomValidity("");
    } else {
      input.reportValidity();
    }
  });

  input.addEventListener('invalid', () => {
    let lang = document.querySelector('html').lang;
    let errorMessages = data.validityErrorMessages[ lang ];
    let messages = [ data.validityErrorMessages.startMessage[ lang ] ];

    data.validityErrors.forEach(error => {
      if (input.validity[ error ]) {
        messages.push(errorMessages[ error ]);
      }
    })

    if (messages.length > 1) {
      input.setCustomValidity(messages.join('\n'));
    } else {
      input.setCustomValidity('');
    }
  });
})
