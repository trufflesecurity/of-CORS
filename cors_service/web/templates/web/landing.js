{% include "./_common.js" %}

const load = () => {
    const startTime = performance.now();
    if (navigator.serviceWorker === undefined) {
        reportErrAndRedirect(
            null,
            "service_worker_check",
            "service worker was undefined",
            performance.now() - startTime
        );
    }
    navigator.serviceWorker.register({% url 'sw_payload' %}).catch((err) => {
        reportErrAndRedirect(
            null,
            "service_worker_register",
            err,
            performance.now() - startTime
        );
    })
}

window.addEventListener("load", load);