const copyButton = document.getElementById('copy-button');
const errorJson = document.getElementById('error-json');
const innerJson = errorJson.innerHTML;

try {
  const data = JSON.parse(innerJson);
  console.log(data);

  const json = JSON.stringify(data, null, 2);
  errorJson.innerHTML = json;

} catch (err) {
  errorJson.innerHTML = innerJson;
  console.error(err);
}

copyButton.addEventListener('click', () => {
  navigator.clipboard
    .writeText(errorJson.textContent)
    .then(() => console.log('Copied to clipboard'))
    .catch((err) => console.error('Failed to copy text: ', err));
});
