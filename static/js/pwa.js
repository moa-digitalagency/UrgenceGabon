document.addEventListener('DOMContentLoaded', () => {
    // Check if PWA is enabled
    if (!window.pwaEnabled) return;

    // Register Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(reg => console.log('SW registered'))
            .catch(err => console.log('SW registration failed', err));
    }

    let deferredPrompt;
    const isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;

    // Don't show if already installed
    if (isStandalone) return;

    // Android/Desktop: Listen for beforeinstallprompt
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault();
        // Stash the event so it can be triggered later.
        deferredPrompt = e;
        // Show the prompt
        showInstallPrompt();
    });

    // iOS: Show instruction if not standalone
    if (isIos && !isStandalone) {
        // Only show once per session or use localStorage to limit frequency
        if (!localStorage.getItem('pwa_prompt_dismissed')) {
             showIosPrompt();
        }
    }

    function showInstallPrompt() {
        const modal = document.getElementById('pwa-install-modal');
        if (modal) {
             modal.classList.remove('hidden');
             modal.classList.add('flex');

             const btn = document.getElementById('pwa-install-btn');
             btn.onclick = () => {
                 modal.classList.add('hidden');
                 modal.classList.remove('flex');

                 if (deferredPrompt) {
                     deferredPrompt.prompt();
                     deferredPrompt.userChoice.then((choiceResult) => {
                         if (choiceResult.outcome === 'accepted') {
                             console.log('User accepted the install prompt');
                         }
                         deferredPrompt = null;
                     });
                 }
             };

             document.getElementById('pwa-dismiss-btn').onclick = () => {
                 modal.classList.add('hidden');
                 modal.classList.remove('flex');
             };
        }
    }

    function showIosPrompt() {
         const toast = document.getElementById('pwa-ios-toast');
         if (toast) {
             toast.classList.remove('hidden');

             document.getElementById('pwa-ios-dismiss-btn').onclick = () => {
                 toast.classList.add('hidden');
                 localStorage.setItem('pwa_prompt_dismissed', 'true');
             };
         }
    }
});
