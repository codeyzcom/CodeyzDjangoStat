const serverAddress = 'http://127.0.0.1:8000/'

function getOsVersion() {
    let nAgt = navigator.userAgent;
    let os;
    let clientStrings = [
        {s: 'Windows 10', r: /(Windows 10.0|Windows NT 10.0)/},
        {s: 'Windows 8.1', r: /(Windows 8.1|Windows NT 6.3)/},
        {s: 'Windows 8', r: /(Windows 8|Windows NT 6.2)/},
        {s: 'Windows 7', r: /(Windows 7|Windows NT 6.1)/},
        {s: 'Windows Vista', r: /Windows NT 6.0/},
        {s: 'Windows Server 2003', r: /Windows NT 5.2/},
        {s: 'Windows XP', r: /(Windows NT 5.1|Windows XP)/},
        {s: 'Windows 2000', r: /(Windows NT 5.0|Windows 2000)/},
        {s: 'Windows ME', r: /(Win 9x 4.90|Windows ME)/},
        {s: 'Windows 98', r: /(Windows 98|Win98)/},
        {s: 'Windows 95', r: /(Windows 95|Win95|Windows_95)/},
        {s: 'Windows NT 4.0', r: /(Windows NT 4.0|WinNT4.0|WinNT|Windows NT)/},
        {s: 'Windows CE', r: /Windows CE/},
        {s: 'Windows 3.11', r: /Win16/},
        {s: 'Android', r: /Android/},
        {s: 'Open BSD', r: /OpenBSD/},
        {s: 'Sun OS', r: /SunOS/},
        {s: 'Chrome OS', r: /CrOS/},
        {s: 'Linux', r: /(Linux|X11(?!.*CrOS))/},
        {s: 'iOS', r: /(iPhone|iPad|iPod)/},
        {s: 'Mac OS X', r: /Mac OS X/},
        {s: 'Mac OS', r: /(MacPPC|MacIntel|Mac_PowerPC|Macintosh)/},
        {s: 'QNX', r: /QNX/},
        {s: 'UNIX', r: /UNIX/},
        {s: 'BeOS', r: /BeOS/},
        {s: 'OS/2', r: /OS\/2/},
        {
            s: 'Search Bot',
            r: /(nuhk|Googlebot|Yammybot|Openbot|Slurp|MSNBot|Ask Jeeves\/Teoma|ia_archiver)/
        }
    ];
    for (let id in clientStrings) {
        let cs = clientStrings[id];
        if (cs.r.test(nAgt)) {
            os = cs.s;
            break;
        }
    }
    return os;
}

function getBrowser() {
    let ua = navigator.userAgent, tem,
        M = ua.match(/(opera|chrome|yabrowser|safari|firefox|msie|trident(?=\/))\/?\s*(\S+)/i) || [];
    if (/trident/i.test(M[1])) {
        tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
        return tem[1] || '';
    }
    if (M[1] === 'Chrome') {
        tem = ua.match(/\b(OPR|Edge|YaBrowser?)\/(\S+)/);
        if (tem != null) return tem.slice(1).join(' ').replace('OPR', 'Opera').replace('Edg ', 'Edge ').replace('YaBrowser', 'YaBrowser');
    }
    M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
    if ((tem = ua.match(/version\/(\S+)/i)) != null) M.splice(1, 1, tem[1]);
    return M.join(' ');
}


function measure_speed() {

    let t = window.performance.timing;
    let domLoading = t.domLoading;
    let domComplete = t.domComplete;
    let responseStart = t.responseStart;
    let responseEnd = t.responseEnd;

    let processing = domComplete - domLoading;
    let loadingTime = responseEnd - responseStart;

    console.log('DOM ', processing)
    console.log('DUR ', loadingTime)

}

let data = {};
data['screen_height'] = screen.height;
data['screen_width'] = screen.width;
data['screen_color_depth'] = screen.colorDepth;
data['screen_pixel_depth'] = screen.pixelDepth;
data['window_height'] = window.innerHeight;
data['window_width'] = window.innerWidth;
data['doc_ref'] = document.referrer;
data['doc_url'] = document.URL;
data['tz_info'] = Intl.DateTimeFormat().resolvedOptions().timeZone;
data['user_lang'] = navigator.language || navigator.userLanguage;
data['platform'] = navigator.platform;
data['os_version'] = getOsVersion();
data['browser'] = getBrowser();


function sendData(data) {
    const XHR = new XMLHttpRequest();

    let urlEncodedData = "",
        urlEncodedDataPairs = [],
        name;

    for (name in data) {
        urlEncodedDataPairs.push(encodeURIComponent(name) + '=' + encodeURIComponent(data[name]))
    }
    urlEncodedData = urlEncodedDataPairs.join('&').replace(/%20/g, '+');
    XHR.open('GET', serverAddress + 'cdzstat/collect_statistic?' + urlEncodedData);
    XHR.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    XHR.send();
    console.log(urlEncodedData)
}

function sendPost(data) {
    let xhr = new XMLHttpRequest();
    xhr.open("POST", serverAddress + 'cdzstat/collect_statistic', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        value: data
    }));
}

(function () {
    sendData(data);
})();


window.onload = function () {

}

