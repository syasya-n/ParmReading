// import smoothscroll from 'smoothscroll-polyfill';

// // kick off the polyfill!
// smoothscroll.polyfill();

const PageTopBtn = document.getElementById('js-scroll-top');
PageTopBtn.addEventListener('click', () =>{
  window.scrollTo({
    scrollTo(0, 0)
  });
});
