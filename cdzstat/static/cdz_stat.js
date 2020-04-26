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

function sendData(data) {
    const XHR = new XMLHttpRequest();

    let urlEncodedData = "",
        urlEncodedDataPairs = [],
        name;

    for (name in data) {
        urlEncodedDataPairs.push(encodeURIComponent(name) + '=' + encodeURIComponent(data[name]))
    }
    urlEncodedData = urlEncodedDataPairs.join('&').replace(/%20/g, '+');
    XHR.open('GET', 'http://127.0.0.1:8000/cdzstat/collect_statistic?' + urlEncodedData);
    XHR.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    XHR.send();
    console.log(urlEncodedData)
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
data['platform'] = getOsVersion();

(function () {
    sendData(data);
})();
