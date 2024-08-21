
// Get Elements
const form = document.getElementById('search-params-form-data');
const downloadLink = document.getElementById('download-link');

const infoAlert = document.getElementById('info-alert');
const successAlert = document.getElementById('success-alert');
const errorAlert = document.getElementById('error-alert');
const errorDescription = document.getElementById('alert-error-description');

const loader = document.getElementById('loader');
const tableButton = document.getElementById('table-button');
const searchButton = document.getElementById('search-button');

const inputs = document.querySelectorAll('input');
const token = document.getElementById('token');


// Validations
const validityErrorMessages = {
  startMessage: {
    'en-us': 'Please fill in correctly.',
    'pt-br': 'Por favor preencha corretamente.'
  },
  'en-us': {
    valueMissing: 'This field is required.',
    typeMismatch: 'Enter a valid value.',
    patternMismatch: 'Match the requested format.',
    tooLong: 'The value is too long.',
    tooShort: 'The value is too short.',
  },
  'pt-br': {
    valueMissing: 'Este campo é obrigatório.',
    typeMismatch: 'Insira um valor válido.',
    patternMismatch: 'Siga o formato solicitado.',
    tooLong: 'O valor é muito longo.',
    tooShort: 'O valor é muito curto.',
  }
};
const validityErrors = Object.keys(validityErrorMessages[ 'pt-br' ])


// Animation
const keyframes = [
  { boxShadow: 'none', scale: 1 },
  { boxShadow: '3px 3px 5px var(--gray-5)', scale: 1.1 },
  { boxShadow: 'none', scale: 1 }
];
const options = { duration: 500, easing: 'linear' };


// Set page language
document.getElementById('language-select').addEventListener('change', (event) => {
  document.querySelector('html').lang = event.target.value;
  document.getElementById('language-flag').animate(keyframes, options);
});


const validation = {
  searchButton,
  inputs,
  validityErrors,
  validityErrorMessages
};
const submit = {
  form,
  loader,
  searchButton,
  tableButton,
  downloadLink,
  infoAlert,
  successAlert,
  errorAlert,
  errorDescription
};


export { token, infoAlert, validation, submit };
