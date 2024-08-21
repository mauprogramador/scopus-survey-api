const totalColspan = document.getElementById('total-colspan');
const theadTr = document.querySelector('thead tr');


if (document.querySelector('table')) {

  function setColspan() {
    let columns = document.querySelectorAll('col');
    let visible = Array.from(columns).filter((column) => {
      let display = window.getComputedStyle(column, null).display;
      let visibility = column.checkVisibility();
      return display !== 'none' && visibility;
    });
    totalColspan.setAttribute('colspan', visible.length - 1);
  }


  window.addEventListener('load', setColspan);
  window.addEventListener('resize', setColspan);


  new IntersectionObserver(
    ([e]) => {
      e.target.toggleAttribute('data-stuck', e.intersectionRatio < 1)
    },
    {threshold: [1]}
  ).observe(theadTr);
}
