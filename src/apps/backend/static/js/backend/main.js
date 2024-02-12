const storage = {}

async function initial() {
    let sleepTime = 30000
    let response = await initialRequest()
    console.log(response)
    if (response.success) {
        storage.readyToGetToken = false
        window.addEventListener('webglAnalyzed', event => webglAnalyzedCallback(event));
        window.addEventListener('automationDetectionCompleted', event => automationDetectionCompletedCallback(event));
        window.dispatchEvent(new Event('analyzeWebgl'));
        window.dispatchEvent(new Event('detectAutomations'));
    } else {
        console.log(`Failed to init session, retry after ${sleepTime} sec`)
        setTimeout(initial, sleepTime)
    }
}
function initialRequest() {
    return fetch("/backend/v1/initial", {
        headers: {
            'Connection': 'close',
            'Cache-Control': 'no-cache',
        }
    }).
    then(response => response.json()).
    catch(error => new Object({"success": false, "error": {"message": error.toString()}}));
}
async function webglAnalyzedCallback(event) {
    storage.webgl = { "webglRaw": event.fingerprint, "webglHash": event.fingerprintHash }
    if (storage.readyToGetToken) { await getToken() }
    storage.readyToGetToken = true
}
async function automationDetectionCompletedCallback(event) {
    storage.automation = event.automation;
    if (storage.readyToGetToken) { await getToken() }
    storage.readyToGetToken = true
}
async function getToken() {
    let webglBase64 = storage.webgl?.webglRaw || '';
    let webglHash = storage.webgl?.webglHash || '';
    let automation = storage.automation || {};
    let response = await getTokenRequest(webglHash, webglBase64, automation)
    if (response.success) {
        let tokenReadyEvent = new Event('tokenReady');
        tokenReadyEvent.robotlessToken = response.data.token;
        sessionStorage.setItem('robotlessToken', response.data.token);
        window.dispatchEvent(tokenReadyEvent)
    } else {
        let tokenFailedEvent = new Event('tokenFailed');
        tokenFailedEvent.response = response
        window.dispatchEvent(tokenFailedEvent)
    }
}
function getTokenRequest(webglHash, webglBase64, automation) {
    return fetch("/backend/v1/token", {
        method: "POST",
        headers: {
            "Content-Type": "application/json; charset=UTF-8",
            "Connection": "close",
            "Cache-Control": "no-cache",
            "X-CSRFToken": window.getCookie('csrftoken')
        },
        body: JSON.stringify({
            "webgl_hash": webglHash,
            "webgl_raw": webglBase64,
            "automation": automation
        }),
        credentials: 'include'
    }).
    then(response => response.json()).
    catch(error => new Object({"success": false, "error": {"message": error.toString()}}))
}

window.addEventListener('initRobotlessSession', event => initial(event))
