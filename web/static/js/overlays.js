import { survCombDetailsBtn, survDocsDetailsBtn } from './index.js';
import { Button } from './button.js';

// Tooltips and Btn-Close
document
  .querySelectorAll('[data-bs-toggle="tooltip"]')
  .forEach((tooltipEl) => new bootstrap.Tooltip(tooltipEl));

document.querySelectorAll('.btn-close').forEach((btnClose) => {
  btnClose.addEventListener('click', (event) => {
    event.target.blur();
  });
});

// Handle dropdown translate menu
const translateButton = new Button('#translate-button');
const translateDropdown = document.getElementById('translate-dropdown');

translateButton.button.addEventListener('shown.bs.dropdown', () => {
  translateDropdown.focus();
  translateDropdown.ariaExpanded = 'true';
  translateButton.ariaActive();
});

translateButton.button.addEventListener('hidden.bs.dropdown', () => {
  translateButton.button.focus();
  translateDropdown.ariaExpanded = 'false';
  translateButton.ariaInactive();
});

// Handle accordion
const accordionJsonButton = new Button('#accordion-json-button');
const jsonTreeCollapse = document.getElementById('json-tree-collapse');
const errorRawJson = document.getElementById('error-raw-json');

jsonTreeCollapse.addEventListener('shown.bs.collapse', () => {
  jsonTreeCollapse.ariaExpanded = 'true';
  accordionJsonButton.ariaActive();
  errorRawJson.focus();
});

jsonTreeCollapse.addEventListener('hidden.bs.collapse', () => {
  accordionJsonButton.button.focus();
  accordionJsonButton.ariaInactive();
  jsonTreeCollapse.ariaExpanded = 'false';
});

// Focused element state
const main = document.getElementById('main-content');
var previousFocusedEl = main;

function currentFocusedEl() {
  if (document.activeElement && document.activeElement !== document.body) {
    document.activeElement.blur();
    return document.activeElement;
  } else {
    main.blur();
    return main;
  }
}

// Handle warning modal
const warningModal = document.getElementById('warning-modal');
const warningBSModal = new bootstrap.Modal('#warning-modal');
const warningsNumber = document.getElementById('warnings-number');
const warningMessages = document.getElementById('warnings-messages');

warningModal.addEventListener('show.bs.modal', () => {
  previousFocusedEl = currentFocusedEl();
  main.setAttribute('aria-hidden', 'true');
  main.inert = true;

  warningModal.toggleAttribute('hidden', false);
  warningModal.ariaExpanded = 'true';
  warningModal.focus();
});

warningModal.addEventListener('hidden.bs.modal', () => {
  warningModal.toggleAttribute('hidden', true);
  warningModal.ariaExpanded = 'false';

  main.setAttribute('aria-hidden', 'false');
  main.inert = false;
  previousFocusedEl.focus();
});

function showWarning(warnings) {
  warningsNumber.innerText = warnings.length;
  warningMessages.innerHTML = '';

  warnings.forEach((warning) => {
    let liWarning = document.createElement('li');
    liWarning.classList.add('list-group-item');
    liWarning.classList.add('fw-bold');
    liWarning.innerText = warning;
    warningMessages.appendChild(liWarning);
  });

  warningBSModal.show();
}

// Handle details modal
const detailsModal = document.getElementById('details-modal');

detailsModal.addEventListener('show.bs.modal', () => {
  previousFocusedEl = currentFocusedEl();
  main.setAttribute('aria-hidden', 'true');
  main.inert = true;

  detailsModal.toggleAttribute('hidden', false);
  detailsModal.ariaExpanded = 'true';
  detailsModal.focus();

  survCombDetailsBtn.ariaActive();
  survDocsDetailsBtn.ariaActive();
});

detailsModal.addEventListener('hidden.bs.modal', () => {
  detailsModal.toggleAttribute('hidden', true);
  detailsModal.ariaExpanded = 'false';

  main.setAttribute('aria-hidden', 'false');
  main.inert = false;

  survCombDetailsBtn.ariaInactive();
  survDocsDetailsBtn.ariaInactive();
  previousFocusedEl.focus();
});

// Close all open dialog
function closeAll() {
  let currentOpen = document.querySelector('dialog[open]');
  if (currentOpen) {
    new bootstrap.Alert(currentOpen).close();
    currentOpen.blur();
  }
  previousFocusedEl = currentFocusedEl();
}

// Loader
const loader = document.getElementById('loader-dialog');

function showLoader() {
  requestAnimationFrame(() => {
    closeAll();
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
    previousFocusedEl.focus();
  });
}

// Warning Alert
const warningAlert = document.getElementById('warning-alert');
const warningBSAlert = new bootstrap.Alert('#warning-alert');

warningAlert.addEventListener('closed.bs.alert', () => {
  warningAlert.toggleAttribute('hidden', true);
  previousFocusedEl.focus();
});

function showWarningAlert(event) {
  event.preventDefault();
  event.returnValue = '';

  requestAnimationFrame(() => {
    warningAlert.toggleAttribute('hidden', false);
    warningAlert.focus();
    warningAlert.show();

    setTimeout(() => {
      if (warningAlert.open) {
        warningBSAlert.close();
      }
    }, 7000);
  });
}

// Success Alert
const successAlert = document.getElementById('success-alert');
const successBSAlert = new bootstrap.Alert('#success-alert');
const successMessage = document.getElementById('success-alert-msg');

successAlert.addEventListener('closed.bs.alert', () => {
  successAlert.toggleAttribute('hidden', true);
  successMessage.innerHTML = '';
  previousFocusedEl.focus();
});

function showSuccessAlert(message) {
  successMessage.innerText = message;

  requestAnimationFrame(() => {
    closeAll();
    successAlert.toggleAttribute('hidden', false);
    successAlert.querySelector('.btn-close').focus();
    successAlert.show();

    setTimeout(() => {
      if (successAlert.open) {
        successBSAlert.close();
      }
    }, 7000);
  });
}

// Error Alert
const errorAlert = document.getElementById('error-alert');
const errorMessage = document.getElementById('error-alert-msg');

errorAlert.addEventListener('closed.bs.alert', () => {
  errorAlert.toggleAttribute('hidden', true);
  main.inert = false;
  main.setAttribute('aria-hidden', 'false');

  previousFocusedEl.focus();
  errorMessage.innerHTML = '';
  errorRawJson.innerHTML = '';
});

function showErrorAlert(message, rawJson) {
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
    closeAll();
    main.setAttribute('aria-hidden', 'true');
    main.inert = true;

    errorAlert.toggleAttribute('hidden', false);
    errorAlert.focus();
    errorAlert.show();
  });
}

export {
  closeAll,
  showLoader,
  hideLoader,
  showWarningAlert,
  showSuccessAlert,
  showErrorAlert,
  showWarning,
};
