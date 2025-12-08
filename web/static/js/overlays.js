import { main, currentFocusedEl, errorRawJson } from './index.js';

// Close buttons
document.querySelectorAll('.alert .btn-close').forEach((btnClose) => {
  btnClose.addEventListener('click', () => {
    btnClose.closest('.alert').close();
  });
});

// Close any open dialog
function closeAny() {
  let currentOpen = document.querySelector('dialog[open]');
  if (currentOpen) {
    let alertOpen = new bootstrap.Alert(currentOpen);
    alertOpen.close();
  }
  window.PreviousFocusedEl = currentFocusedEl();
}

// Request loader
const loader = document.getElementById('loader-dialog');

function showLoader() {
  requestAnimationFrame(() => {
    closeAny();
    main.setAttribute('aria-hidden', 'true');
    main.inert = true;
    loader.toggleAttribute('hidden', false);
    loader.focus();
    loader.showModal();
  });
}

function hideLoader() {
  requestAnimationFrame(() => {
    loader.close();
    loader.toggleAttribute('hidden', true);
    main.inert = false;
    main.setAttribute('aria-hidden', 'false');
    window.PreviousFocusedEl.focus();
  });
}

// Warning
const warningAlert = document.getElementById('warning-alert');

warningAlert.addEventListener('close', () => {
  warningAlert.toggleAttribute('hidden', true);
  window.PreviousFocusedEl.focus();
});

function showWarning(event) {
  event.preventDefault();
  event.returnValue = '';

  requestAnimationFrame(() => {
    warningAlert.toggleAttribute('hidden', false);
    warningAlert.focus();
    warningAlert.show();

    setTimeout(() => {
      if (warningAlert.open) {
        warningAlert.close();
      }
    }, 7000);
  });
}

// Success
const successAlert = document.getElementById('success-alert');
const successMessage = document.getElementById('success-alert-msg');

successAlert.addEventListener('close', () => {
  successAlert.toggleAttribute('hidden', true);
  successMessage.innerHTML = '';
  window.PreviousFocusedEl.focus();
});

function showSuccess(message) {
  successMessage.innerText = message;

  requestAnimationFrame(() => {
    closeAny();
    successAlert.toggleAttribute('hidden', false);
    successAlert.focus();
    successAlert.show();

    setTimeout(() => {
      if (successAlert.open) {
        successAlert.close();
      }
    }, 7000);
  });
}

// Error
const errorAlert = document.getElementById('error-alert');
const errorMessage = document.getElementById('error-alert-msg');

errorAlert.addEventListener('close', () => {
  errorAlert.toggleAttribute('hidden', true);
  main.inert = false;
  main.setAttribute('aria-hidden', 'false');

  window.PreviousFocusedEl.focus();
  errorMessage.innerHTML = '';
  errorRawJson.innerHTML = '';
});

function showError(message, rawJson) {
  errorMessage.innerText = message || 'An error occurred';

  let json = null;
  if (typeof rawJson === 'object' && rawJson !== null) {
    json = rawJson;
  } else {
    json = JSON.parse(rawJson);
  }

  let jsonTree = jsonview.create(json);
  jsonview.render(jsonTree, errorRawJson);

  requestAnimationFrame(() => {
    closeAny();
    main.setAttribute('aria-hidden', 'true');
    main.inert = true;

    errorAlert.toggleAttribute('hidden', false);
    errorAlert.focus();
    errorAlert.show();
  });
}

export {
  closeAny,
  showLoader,
  hideLoader,
  showWarning,
  showSuccess,
  showError,
};
