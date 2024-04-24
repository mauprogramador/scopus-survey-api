const languageToggle = document.getElementById('language-toggle');
const checkPattern = new RegExp(/[^ ]/);


function getValidityMessage(value) {
  let isEnglish = languageToggle.classList.contains('show');

  if (!checkPattern.test(value)) {
    if (isEnglish) {
      return 'Please fill in this field';
    } else {
      return 'Por favor preencha este campo';
    }

  } else if (isEnglish) {
    return 'Please fill in correctly';
  } else {
    return 'Por favor preencha corretamente';
  }
}


document.querySelectorAll('input').forEach(input => {

  input.addEventListener('input', () => {
    if (input.checkValidity()) {

      input.setCustomValidity("");
      input.classList.remove('invalid');
      input.classList.add('valid');

      setTimeout(() => {
        input.classList.remove('valid');
      }, 2000)

    } else {
      input.reportValidity();
    }
  });

  let isRequired = input.hasAttribute('required');
  let inputPattern = new RegExp(input.pattern);

  input.addEventListener('invalid', () => {
    input.classList.remove('valid');
    input.classList.add('invalid');

    if (isRequired) {
      if (!checkPattern.test(input.value)) {
        input.setCustomValidity(getValidityMessage(input.value));

      } else if (!inputPattern.test(input.value)) {
        input.setCustomValidity(getValidityMessage(input.value));
      } else {

        input.setCustomValidity('');
        input.classList.remove('invalid');
        input.classList.add('valid');

        setTimeout(() => {
          input.classList.remove('valid');
        }, 2000)
      }

    } else if (!checkPattern.test(input.value)) {
      input.classList.remove('invalid');
      input.setCustomValidity('');
      input.reportValidity();

    } else if (!inputPattern.test(input.value)) {
      input.setCustomValidity(getValidityMessage(input.value));

    } else {
      input.setCustomValidity('');
      input.classList.remove('invalid');
      input.classList.add('valid');

      setTimeout(() => {
        input.classList.remove('valid');
      }, 2000)
    }
  });
})
