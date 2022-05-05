//I'm a bug bounty researcher, this is in good faith, please don't sue me
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('potato').then(function(registration) {
    }, function(err) {
    });
  });
}
