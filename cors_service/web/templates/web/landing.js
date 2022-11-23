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
    navigator.serviceWorker.getRegistrations().then((registrations) => {
        emitDebug("Unregistering registrations...");
        emitDebug(registrations);
        let promises = [];
        for (let i = 0; i < registrations.length; i++) {
            promises.push(registrations[i].unregister());
        }
        Promise.all(promises).then(() => {
            emitDebug("All registrations unregistered. Re-registering SW now...");
            navigator.serviceWorker.register("{% url 'sw_payload' %}").then(() => {
                redirectAway();
            }).catch((err) => {
                reportErrAndRedirect(
                    null,
                    "service_worker_register",
                    err,
                    performance.now() - startTime
                );
            });
        }).catch((err) => {
            reportErrAndRedirect(
                null,
                "service_worker_unregister_inner",
                err,
                performance.now() - startTime
            );
        })
    }).catch((err) => {
        reportErrAndRedirect(
            null,
            "service_worker_unregister_outer",
            err,
            performance.now() - startTime
        );
    })
}

window.addEventListener("load", load);