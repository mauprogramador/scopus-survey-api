import { Button } from './button.js';

// Insert Btn group
const hbtngp = document.getElementById('hbtngp');
const vbtngp = document.getElementById('vbtngp');

const template = document.getElementById('buttons-group');
const clone = template.content.cloneNode(true);

hbtngp.appendChild(clone);
vbtngp.appendChild(clone);

// Parse JSON into textarea
const jsonResponse = document.getElementById('json-response');
const rawJson = jsonResponse.innerHTML;

try {
  const data = JSON.parse(rawJson);
  console.log(data);

  const json = jsonview.create(data);
  jsonResponse.innerHTML = '';
  jsonview.render(json, jsonResponse);
} catch (err) {
  jsonResponse.innerHTML = rawJson;
  console.error(err);
}

// Copy to clipboard
const copyButton = document.getElementById('copy-button');
copyButton.addEventListener('click', () => {
  navigator.clipboard
    .writeText(rawJson)
    .then(() => console.log('Copied to clipboard'))
    .catch((err) => console.error('Failed to copy text: ', err));
});

// Handle aria attrs
const jsonButton = new Button('#json-button');

jsonResponse.addEventListener('shown.bs.collapse', () => {
  jsonResponse.ariaExpanded = 'true';
  jsonButton.ariaActive();
  jsonResponse.focus();
});

jsonResponse.addEventListener('hidden.bs.collapse', () => {
  jsonResponse.ariaExpanded = 'false';
  jsonButton.ariaInactive();
  jsonButton.button.focus();
});
