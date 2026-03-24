import { showErrorAlert } from './overlays.js';

window.addEventListener('error', (event) => {
  let rawJson = {
    message: event.error.message || 'Unknown Error',
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    type: event.error.name || 'Error',
    stack: event.error.stack || null,
    repr: event.error.toString(),
    timestamp: new Date().toISOString(),
  };
  showErrorAlert(event.message, rawJson);
});

window.addEventListener('unhandledrejection', (event) => {
  let rawJson = {
    message: 'Unknown Rejection',
    type: 'UnhandledRejection',
    reason: null,
    timestamp: new Date().toISOString(),
  };

  if (typeof event.reason === 'object' && event.reason !== null) {
    rawJson['reason'] = event.reason;
  } else {
    try {
      rawJson['reason'] = JSON.stringify(event.reason);
    } catch (e) {
      console.error('Failed to parse rejection reason:', e);
    }
  }
  showErrorAlert('Unhandled Async Rejection', rawJson);
});
