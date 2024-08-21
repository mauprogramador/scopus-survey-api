import { token, infoAlert } from './index.js';


// Headers
const headers = {
  'Accept': 'text/csv',
  'Content-Type': 'text/csv; charset=utf-8',
  'Access-Control-Allow-Origin': '*',
  'X-Access-Token': token.innerText
};
token.remove();


// Set alerts close event
document.querySelectorAll('.alert-close').forEach(element => {
  element.addEventListener('click', () => {
    element.parentElement.close();
  });
});


function interuptSearching(event) {
  event.preventDefault();
  infoAlert.show();

  setTimeout(() => {
    infoAlert.close();
  }, 5000);
}


export { headers, interuptSearching };
