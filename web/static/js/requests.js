import {
  lang,
  csrfToken,
  downloadLink,
  updateDetails,
  populateTable,
  hideFinalStep,
  showFinalStep,
  prevSurveyBtn,
  survCombBtn,
  survCombDetailsBtn,
  survDocsBtn,
  downloadBtn,
  survDocsDetailsBtn,
  apiKeyField,
  allCombFields,
  keywordsFields,
  allFreshFields,
} from './index.js';
import {
  closeDialog,
  showLoader,
  hideLoader,
  showWarningAlert,
  showSuccessAlert,
  showErrorAlert,
} from './overlays.js';
import { translationTexts } from './translations.js';
import { fieldsValidity, noRadios } from './validation.js';

// Headers
const headers = {
  Accept: 'text/csv',
  'Content-Type': 'text/csv; charset=utf-8',
  'Access-Control-Allow-Origin': '*',
  'X-CSRF-Token': csrfToken,
};

// Error to JSON
function errorToJSON(error) {
  const jsonError = {
    type: error.constructor.name,
    name: error.name,
    message: error.message,
    cause: error.cause,
  };

  if (error.response) {
    jsonError.type = 'HTTPError';
    jsonError.url = error.response.url;
    jsonError.code = error.response.status;
    jsonError.status = error.response.statusText;
    jsonError.data = error.response.data;
    jsonError.headers = Object.fromEntries(
      error.response.headers?.entries() || []
    );
  }

  return JSON.stringify(jsonError, null);
}

// Fetch request
function request(url, callback) {
  const controller = new AbortController();

  const request = new Request(url, {
    method: 'GET',
    headers: headers,
    signal: controller.signal,
    cache: 'no-store',
  });

  window.addEventListener('beforeunload', showWarningAlert);
  showLoader();

  return fetch(request)
    .then((response) => {
      window.removeEventListener('beforeunload', showWarningAlert);
      hideLoader();

      if (response.ok) {
        updateDetails(response.headers);
        try {
          return callback(response);
        } catch (error) {
          console.error(error);
          showErrorAlert(error.message, errorToJSON(error));
          return false;
        }
      } else {
        response
          .json()
          .then((json) => {
            console.error(json);
            showErrorAlert(json['message'], json);

            let isUnauthorized = response.status === 401;
            let missingCSRF = 'Missing CSRF Token Cookie';

            if (isUnauthorized && json['message'] === missingCSRF) {
              setTimeout(() => {
                closeDialog();
                location.reload();
              }, 5000);
            }
          })
          .catch((error) => {
            console.error(error);
            showErrorAlert(error.message, errorToJSON(error));
          });
        return false;
      }
    })
    .catch((error) => {
      window.removeEventListener('beforeunload', showWarningAlert);
      hideLoader();

      console.error(error);
      showErrorAlert(error.message, errorToJSON(error));

      return false;
    });
}

// Fetch Previous Survey CSV
prevSurveyBtn.button.addEventListener('click', () => {
  apiKeyField.dataset.checked = 'true';

  if (!apiKeyField.validity.valid) {
    return void 0;
  }
  prevSurveyBtn.busy();

  const url = new URL(prevSurveyBtn.formAction);
  url.searchParams.set('csrfToken', csrfToken);

  url.searchParams.set(apiKeyField.name, apiKeyField.value);
  url.searchParams.set(prevSurveyBtn.name, prevSurveyBtn.value);

  request(url, (response) => {
    if (response) {
      let csvFilename = response.headers.get('X-CSV-Filename');

      return response.blob().then((blob) => {
        const blobUrl = window.URL.createObjectURL(blob);
        downloadLink.download = csvFilename;
        downloadLink.href = blobUrl;

        downloadLink.click();
        setTimeout(() => URL.revokeObjectURL(blobUrl), 100);

        showSuccessAlert(translationTexts[lang].S01);
      });
    }
  }).then((result) => {
    if (result === false) {
      prevSurveyBtn.free();
    }
  });

  prevSurveyBtn.free();
  prevSurveyBtn.button.focus();
});

// Fetch survey combination totals
const combFields = document.querySelectorAll('.combfield');

survCombBtn.button.addEventListener('click', () => {
  allCombFields.forEach((field) => (field.dataset.checked = 'true'));

  if (!fieldsValidity(allCombFields)) {
    return void 0;
  }
  survCombBtn.busy();
  survCombDetailsBtn.disable();

  const url = new URL(survCombBtn.formAction);
  url.searchParams.set('csrfToken', csrfToken);

  combFields.forEach((field) => {
    url.searchParams.set(field.name, field.value);
  });

  const keywords = Array.from(keywordsFields)
    .map((field) => field.value)
    .filter((value) => value.trim() !== '');

  url.searchParams.set('keywords', keywords.join(','));
  url.searchParams.set(survCombBtn.name, survCombBtn.value);
  hideFinalStep();

  request(url, (response) => {
    if (response) {
      return response.json().then((json) => {
        showFinalStep();
        populateTable(json['data']['combinations']);

        showSuccessAlert(translationTexts[lang].S02);
        noRadios();
      });
    }
  }).then((result) => {
    if (result === false) {
      survCombBtn.free();
      survCombDetailsBtn.disable();
    }
  });

  survCombBtn.free();
  survCombDetailsBtn.enable();
});

// Fetch survey documents
let userAPIKey = null;
survDocsBtn.button.addEventListener('click', () => {
  let allFields = allFreshFields.get();
  allFields.forEach((field) => (field.dataset.checked = 'true'));

  if (!fieldsValidity(allFields)) {
    return void 0;
  }

  survDocsBtn.busy();
  downloadBtn.disable();
  survDocsDetailsBtn.disable();

  const url = new URL(survDocsBtn.formAction);
  url.searchParams.set('csrfToken', csrfToken);

  allFields.forEach((field) => {
    url.searchParams.set(field.name, field.value);
  });

  const keywords = Array.from(keywordsFields)
    .map((field) => field.value)
    .filter((value) => value.trim() !== '');

  url.searchParams.set('keywords', keywords.join(','));
  const combination = Array.from(
    document.querySelectorAll('.combination-opt')
  ).filter((field) => field.checked)[0];

  url.searchParams.set(combination.name, combination.value);
  url.searchParams.set(survDocsBtn.name, survDocsBtn.value);

  request(url, (response) => {
    if (response.ok) {
      let csvFilename = response.headers.get('X-CSV-Filename');
      userAPIKey = response.headers.get('X-API-Key');

      return response.blob().then((blob) => {
        const blobUrl = window.URL.createObjectURL(blob);
        downloadLink.download = csvFilename;
        downloadLink.href = blobUrl;

        downloadLink.click();
        URL.revokeObjectURL(blobUrl);

        showSuccessAlert(translationTexts[lang].S03);
      });
    }
  }).then((result) => {
    if (result === false) {
      survDocsBtn.free();
      downloadBtn.disable();
      survDocsDetailsBtn.disable();
    }
  });

  survDocsBtn.free();
  downloadBtn.enable();
  survDocsDetailsBtn.enable();
});

// Download CSV
downloadBtn.button.addEventListener('click', () => {
  downloadBtn.busy();

  const url = new URL(downloadBtn.formAction);
  url.searchParams.set('csrfToken', csrfToken);

  url.searchParams.set(apiKeyField.name, userAPIKey);
  url.searchParams.set(downloadBtn.name, downloadBtn.value);

  request(url, (response) => {
    if (response) {
      let csvFilename = response.headers.get('X-CSV-Filename');

      return response.blob().then((blob) => {
        const blobUrl = window.URL.createObjectURL(blob);
        downloadLink.download = csvFilename;
        downloadLink.href = blobUrl;

        downloadLink.click();
        setTimeout(() => URL.revokeObjectURL(blobUrl), 100);

        showSuccessAlert(translationTexts[lang].S01);
      });
    }
  }).then((result) => {
    if (result === false) {
      downloadBtn.free();
    }
  });

  downloadBtn.free();
});
