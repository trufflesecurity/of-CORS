const redirectAway = () => {
    setTimeout(() => {
        window.location.replace("{{ redirect_url }}");
    }, {{ redirect_ms }})
}

const emitDebug = (toPrint) => {
    {% if print_debug %}
    if (typeof toPrint === "string") {
        console.log("[DEBUG] - ", toPrint);
    } else {
        console.log(toPrint);
    }
    {% endif %}
}

const reportSuccess = (url, content, duration, status) => {
    return fetch("{% url 'cors_success' %}", {
        method: "POST",
        mode: "same-origin",
        headers: {
            "Content-Type": "application/json",
        },
        redirect: "manual",
        referrerPolicy: "no-referrer",
        body: JSON.stringify({
            "url": url,
            "content": content,
            "duration": duration,
            "status": status,
        })
    })
}

const reportErr = (url, location, err, duration) => {
    emitDebug("Got error at URL " + url + " (location '" + location + "'). Error was '" + err + "'");
    return fetch("{% url 'cors_failure' %}", {
        method: "POST",
        mode: "same-origin",
        headers: {
            "Content-Type": "application/json",
        },
        redirect: "manual",
        referrerPolicy: "no-referrer",
        body: JSON.stringify({
            "url": url,
            "location": location,
            "err_msg": "" + err,
            "duration": duration,
        })
    })
}

const reportErrAndRedirect = (url, location, err, duration) => {
    reportErr(url, location, err, duration).then(redirectAway);
}