const form = document.getElementById('scopus-api-form-data');
const downloadLink = document.getElementById('download-link');

const token = document.getElementById('token').innerText;
document.getElementById('token').remove();

const successFeedback = document.getElementById('success-feedback');
const errorFeedback = document.getElementById('error-feedback');

const loader = document.getElementById('loader');
const buttonSelector = '.submit-button.language.show';

const headers = {
  'Accept': 'text/csv',
  'Content-Type': 'text/csv; charset=utf-8',
  'X-Access-Token': token
};


document.querySelectorAll('.banner-close').forEach(element => {
  element.addEventListener('click', () => {
    element.parentElement.classList.remove('visible');
  });
});


form.addEventListener('submit', (event) => {
  event.preventDefault();

  const submitButton = document.querySelector(buttonSelector);
  loader.classList.toggle('show');

  submitButton.toggleAttribute('disabled');
  submitButton.classList.toggle('disable-button');

  const baseURL = `${window.location.href}/search-articles`;
  const myUrl = new URL(baseURL);
  const formData = new FormData(form);

  const keywords = formData
    .getAll('keywords')
    .filter(keyword => keyword.trim() !== "");

  myUrl.searchParams.append('apikey', formData.get('apikey'));
  myUrl.searchParams.append('keywords', keywords.join(','));

  const request = new Request(myUrl.toString(), {
    method: 'GET',
    headers: headers
  });

  document.querySelectorAll('.banner.visible').forEach((banner) => {
    banner.classList.remove('visible');
  });

  fetch(request).then((response) => {
    submitButton.toggleAttribute('disabled');
    submitButton.classList.toggle('disable-button');
    loader.classList.toggle('show');

    if (response.ok) {

      response.blob().then((blob) => {
        downloadLink.href = window.URL.createObjectURL(blob);
        downloadLink.setAttribute('download', 'articles.csv');
        downloadLink.click();
      });

      requestAnimationFrame(() => {
        successFeedback.classList.add('visible');
        setTimeout(() => {
          successFeedback.classList.remove('visible');
        }, 5000);
      });

    } else {
      response.json().then(json => {

        console.error(json);
        let message = json[ 'message' ];

        if (json.hasOwnProperty('detail')) {
          let detail = json[ 'detail' ];

          if (Array.isArray(detail)) {
            let details = detail.map(item => item.msg);
            message = `${message}, ${details.join('; ')}`;

          } else {
            message = `${message}, ${detail}`;
          }
        }
        requestAnimationFrame(() => {
          errorFeedback.children.item(1).innerText = message;
          errorFeedback.classList.add('visible');
        });
      })
    }

  }).catch((error) => {
    requestAnimationFrame(() => {
      errorFeedback.children.item(1).innerText = 'Something went wrong!';
      errorFeedback.classList.add('visible');
    });
    console.error(error);
  })
});
