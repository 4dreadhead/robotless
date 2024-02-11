const DOCUMENT_DETECTION_KEYS = [
    "__webdriver_evaluate",
    "__selenium_evaluate",
    "__webdriver_script_function",
    "__webdriver_script_func",
    "__webdriver_script_fn",
    "__fxdriver_evaluate",
    "__driver_unwrapped",
    "__webdriver_unwrapped",
    "__driver_evaluate",
    "__selenium_unwrapped",
    "__fxdriver_unwrapped",
]
const WINDOW_DETECTION_KEYS = [
    "_phantom",
    "__nightmare",
    "_selenium",
    "callPhantom",
    "callSelenium",
    "_Selenium_IDE_Recorder",
]
function windowConstructorAliasTest(window) {
    for (const prop of window.Object.getOwnPropertyNames(window)) {
        if (/^cdc_[a-zA-Z0-9]{22}_(Array|Promise|Symbol)$/.test(prop)) return true;
    }
    function hasConstructorAlias(window, constructor) {
        for (const prop of window.Object.getOwnPropertyNames(window)) {
            if (prop === constructor.name || prop === 'token' || prop === 'getAsyncToken') continue;
            if (window[prop] === constructor) return true;
        }
        return false;
    }
    return hasConstructorAlias(window, window.Array) &&
           hasConstructorAlias(window, window.Promise) &&
           hasConstructorAlias(window, window.Symbol);
}
function cdpRuntimeDomainTest(window) {
    let stackLookup = false;
    const e = new window.Error();
    window.Object.defineProperty(e, 'stack', {
        configurable: false,
        enumerable: false,
        get: function() {
            stackLookup = true;
            return '';
        }
    });
    window.console.debug(e);
    return stackLookup;
}
function runBotDetection(obj, keys) {
    for (let automationKey of keys) {
        if (obj[automationKey]) return true;
    }
    return false;
}
function detectWebdriver() {
    if (window.navigator.webdriver) return true;
    if (window['external'] && window['external'].toString() &&
       (window['external'].toString()['indexOf']('Sequentum') !== -1)) return true;
    if (window['document']['documentElement']['getAttribute']('selenium')) return true;
    if (window['document']['documentElement']['getAttribute']('webdriver')) return true;
    if (window['document']['documentElement']['getAttribute']('driver')) return true;
    return false;
}
function detectAutomations() {
    const iframe = document.createElement('iframe')
    iframe.style = 'display: none';
    document.body.appendChild(iframe);
    const detections = {
        "webdriver_detected": detectWebdriver(),
        "window_automations_detected": runBotDetection(window, WINDOW_DETECTION_KEYS),
        "document_automations_detected": runBotDetection(document, DOCUMENT_DETECTION_KEYS),
        "cdp_detected": cdpRuntimeDomainTest(window),
        "cdc_detected": windowConstructorAliasTest(window) || windowConstructorAliasTest(iframe.contentWindow)
    }
    let successEvent = new Event('automationDetectionCompleted');
    successEvent.automation = detections;
    window.dispatchEvent(successEvent);
}

window.addEventListener('detectAutomations', detectAutomations)
