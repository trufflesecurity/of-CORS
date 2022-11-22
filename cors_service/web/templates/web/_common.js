const redirectAway = () => {
    setTimeout(() => {
        window.location.replace("{{ redirect_url }}");
    }, {{ redirect_ms }})
}

const reportSuccess = (url, content, duration) => {
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
        })
    })
}

const reportErr = (url, location, err, duration) => {
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
            "err_msg": err,
            "duration": duration,
        })
    })
}

const reportErrAndRedirect = (url, location, err, duration) => {
    reportErr(url, location, err, duration).then(redirectAway);
}