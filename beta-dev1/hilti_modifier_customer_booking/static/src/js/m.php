SD = {
    version: "0.9"
};
window["undefined"] = window["undefined"];
SD.apply = function(d, e, b) {
    if (b) {
        SD.apply(d, b)
    }
    if (d && e && typeof e == "object") {
        for (var a in e) {
            d[a] = e[a]
        }
    }
    return d
};
(function() {
    var ua = navigator.userAgent.toLowerCase();
    var isStrict = document.compatMode == "CSS1Compat",
        isOpera = ua.indexOf("opera") > -1,
        isOperaMobile = ua.indexOf("opera") > -1 && ua.indexOf("x11"),
        isSafari = (/webkit|khtml/).test(ua),
        isSafari3 = isSafari && ua.indexOf("webkit/5") != -1,
        isIE = !isOpera && ua.indexOf("msie") > -1,
        isIE6 = !isOpera && ua.indexOf("msie 6") > -1,
        isIE7 = !isOpera && ua.indexOf("msie 7") > -1,
        isIE8 = (isIE && document.documentMode),
        isGecko = !isSafari && ua.indexOf("gecko") > -1,
        isGecko3 = !isSafari && ua.indexOf("rv:1.9") > -1,
        isBorderBox = isIE && !isStrict,
        isWindows = (ua.indexOf("windows") != -1 || ua.indexOf("win32") != -1),
        isMac = (ua.indexOf("macintosh") != -1 || ua.indexOf("mac os x") != -1),
        isAir = (ua.indexOf("adobeair") != -1),
        isLinux = (ua.indexOf("linux") != -1),
        isIphone = ua.indexOf("iphone") != -1 || ua.indexOf("ipad") != -1,
        isAndroid = ua.indexOf("android") != -1 || navigator.platform.indexOf("armv") != -1,
        isWindowsPhone = (ua.indexOf("windows phone") != -1),
        isSecure = window.location.href.toLowerCase().indexOf("https") === 0;
    if (isIE && !isIE7) {
        try {
            document.execCommand("BackgroundImageCache", false, true)
        } catch (e) {}
    }
    if (isIE7 || isIE8) {
        var meta = document.createElement("meta");
        meta.setAttribute("http-equiv", "X-UA-Compatible");
        meta.setAttribute("content", "IE=EmulateIE7");
        var head = document.getElementsByTagName("head")[0];
        head.appendChild(meta)
    }
    var elem = document.createElement("canvas");
    SD.apply(SD, {
        isSvg: (document.createElementNS && ((document.implementation && (document.implementation.hasFeature("org.w3c.svg", "1.0") || document.implementation.hasFeature("http://www.w3.org/TR/SVG11/feature#SVG", "1.1") || document.implementation.hasFeature("http://www.w3.org/TR/SVG11/feature#BasicStructure", "1.1"))) || (window.opera && isOpera && parseInt(ua.substring(ua.indexOf("opera") + 6)) >= 8)) ? true : false),
        isCanvas: !!(elem.getContext && elem.getContext("2d")),
        BASE_URL: "http://beta.streetdirectory.com/dragmap/xg/",
        IMG_URL: "http://beta.streetdirectory.com/dragmap/xg/img/",
        API_URL: "http://beta.streetdirectory.com/",
        MAP_PRE: "maps",
        MAP_URL: "172.16.0.4/data/map/",
        MAP_VERSION: "1.0.15",
        MAP_DIRECT_FILE: true,
        POSITION_TOP_RIGHT: -1,
        POSITION_TOP_LEFT: -2,
        POSITION_BOTTOM_RIGHT: -3,
        POSITION_BOTTOM_LEFT: -4,
        VECTOR_LOADED: false,
        applyIf: function(o, c) {
            if (o && c) {
                for (var p in c) {
                    if (typeof o[p] == "undefined") {
                        o[p] = c[p]
                    }
                }
            }
            return o
        },
        applyProperty: function(o, c) {
            if (o && c) {
                for (var p in c) {
                    if (typeof c[p] != "function") {
                        o[p] = c[p]
                    }
                }
            }
            return o
        },
        extend: function() {
            var io = function(o) {
                for (var m in o) {
                    this[m] = o[m]
                }
            };
            var oc = Object.prototype.constructor;
            return function(sb, sp, overrides) {
                if (typeof sp == "object") {
                    overrides = sp;
                    sp = sb;
                    sb = overrides.constructor != oc ? overrides.constructor : function() {
                        sp.apply(this, arguments)
                    }
                }
                var F = function() {},
                    sbp, spp = sp.prototype;
                F.prototype = spp;
                sbp = sb.prototype = new F();
                sbp.constructor = sb;
                sb.superclass = spp;
                if (spp.constructor == oc) {
                    spp.constructor = sp
                }
                sb.override = function(o) {
                    SD.override(sb, o)
                };
                sbp.override = io;
                SD.override(sb, overrides);
                sb.extend = function(o) {
                    SD.extend(sb, o)
                };
                return sb
            }
        }(),
        isTouchDevice: function() {
            return (isIphone || isAndroid)
        },
        override: function(origclass, overrides) {
            if (overrides) {
                var p = origclass.prototype;
                for (var method in overrides) {
                    p[method] = overrides[method]
                }
            }
        },
        namespace: function() {
            var a = arguments,
                o = null,
                i, j, d, rt;
            for (i = 0; i < a.length; ++i) {
                d = a[i].split(".");
                rt = d[0];
                eval("if (typeof " + rt + ' == "undefined"){' + rt + " = {};} o = " + rt + ";");
                for (j = 1; j < d.length; ++j) {
                    o[d[j]] = o[d[j]] || {};
                    o = o[d[j]]
                }
            }
        },
        removeNode: isIE ? function() {
            var d;
            return function(n) {
                if (n && n.tagName != "BODY") {
                    d = d || document.createElement("div");
                    d.appendChild(n);
                    d.innerHTML = ""
                }
            }
        }() : function(n) {
            if (n && n.parentNode && n.tagName != "BODY") {
                n.parentNode.removeChild(n)
            }
        },
        isOpera: isOpera,
        isOperaMobile: isOperaMobile,
        isSafari: isSafari,
        isSafari3: isSafari3,
        isSafari2: isSafari && !isSafari3,
        isIE: isIE,
        isIE6: isIE6,
        isIE7: isIE7,
        isIE8: isIE8,
        isGecko: isGecko,
        isGecko2: isGecko && !isGecko3,
        isGecko3: isGecko3,
        isBorderBox: isBorderBox,
        isLinux: isLinux,
        isWindows: isWindows,
        isMac: isMac,
        isIphone: isIphone,
        isAndroid: isAndroid,
        isAir: isAir,
        isWindowsPhone: isWindowsPhone,
        useShims: ((isIE && !isIE7) || (isMac && isGecko && !isGecko3))
    });
    SD.ns = SD.namespace
})();
SD.ns("SD", "SD.util", "SD.shape", "SD.drawing", "SD.projection", "SD.genmap");
SD.applyIf(Number.prototype, {
    toFixed: function(a) {
        var b = this;
        b = Math.round(b * Math.pow(10, a)) / Math.pow(10, a);
        return b
    }
});
SD.util = {
    addScript: function(a) {
        var c = document.createElement("script");
        c.setAttribute("type", "text/javascript");
        c.setAttribute("src", a);
        var b = document.getElementsByTagName("head")[0];
        b.appendChild(c);
        return c
    },
    removeScript: function(a) {
        var b = document.getElementsByTagName("head")[0];
        b.removeChild(a)
    },
    defaultIcon: function() {
        var a = new SD.genmap.MarkerImage();
        a.iconSize = new Size(19, 32);
        a.iconAnchor = new Point(9, 34);
        a.infoWindowAnchor = new Point(9, 35);
        a.image = SD.BASE_URL + "/icon.php";
        return a
    },
    debug: function(c, b) {
        str = JSON.stringify(c);
        var a = document.getElementById("debug");
        if (a) {
            if (b) {
                a.innerHTML = str + "<br>"
            } else {
                a.innerHTML += str + "<br>"
            }
        }
    },
    clone: function(b) {
        var a = (b instanceof Array) ? [] : {};
        for (i in b) {
            if (i == "clone") {
                continue
            }
            if (b[i] && b[i].nodeName == "IMG" && b[i].nodeType == 1 && b[i].complete) {
                a[i] = b[i].cloneNode(true)
            } else {
                if (b[i] && b[i].nodeName == "DIV" && b[i].nodeType == 1) {
                    a[i] = b[i].cloneNode(true)
                } else {
                    if (b[i] && typeof b[i] == "object" && !b[i].nodeType) {
                        a[i] = SD.util.clone(b[i])
                    } else {
                        a[i] = b[i]
                    }
                }
            }
        }
        return a
    },
    arrayMin: function(a) {
        if (a.length == 0) {
            return 0
        }
        if (a.length == 1) {
            return 1
        }
        var c = a[0];
        for (var b = 1; b < a.length; b += 1) {
            if (a[b] < c) {
                c = a[b]
            }
        }
        return parseInt(c)
    },
    arrayMax: function(c) {
        for (var b = 0; b < c.length; b += 1) {
            c[b] = c[b] * -1
        }
        var a = SD.util.arrayMin(c);
        a = a * -1;
        return parseInt(a)
    },
    easeInOut: function(d, e, c) {
        var f = Math.abs(d.first - d.latest);
        var a = (Math.pow(((1 / e) * c), 0.5) * f);
        var b = d.first > d.latest ? d.first - a : d.first + a;
        return b
    },
    getDistance: function(a, b) {
        if (isNaN(a.x) || isNaN(a.y) || isNaN(b.x) || isNaN(b.y)) {
            return
        }
        return Math.sqrt((a.x - b.x) * (a.x - b.x) + (b.y - a.y) * (b.y - a.y))
    },
    isDivExist: function(b, d) {
        var c = b.childNodes;
        for (var a = 0; a < c.length; a++) {
            if (d == c[a]) {
                return true
            }
        }
        return false
    },
    isNearBoundary: function(e, b, a) {
        var d = {
                x: 0,
                y: 0
            },
            c = 50;
        e = SD.util.offsetPoint(e, a.x, a.y);
        if (e.x < c) {
            d.x = 10
        } else {
            if (e.x > b.width - c) {
                d.x = -10
            }
        }
        if (e.y < c) {
            d.y = 10
        } else {
            if (e.y > b.height - c) {
                d.y = -10
            }
        }
        if (d.x != 0 || d.y != 0) {
            return d
        }
        return false
    },
    panByOffset: function(a, e, c) {
        var d = parseFloat(a.style.left);
        var b = parseFloat(a.style.top);
        if (!isNaN(d) && !isNaN(b) && a != null) {
            a.style.left = (d + e) + "px";
            a.style.top = (b + c) + "px"
        }
    },
    offsetPoint: function(c, b, d) {
        var a = new Point(b, d);
        a.x = c.x + b;
        a.y = c.y + d;
        return a
    },
    getTopLeft: function(a) {
        if (a == undefined) {
            return {
                x: 0,
                y: 0
            }
        }
        var b = curtop = 0;
        if (a.offsetParent) {
            b = a.offsetLeft;
            curtop = a.offsetTop;
            while (a = a.offsetParent) {
                b += a.offsetLeft;
                curtop += a.offsetTop
            }
        }
        b += (document.documentElement.scrollLeft || document.body.scrollLeft);
        curtop += (document.documentElement.scrollTop || document.body.scrollTop);
        return {
            x: b,
            y: curtop
        }
    },
    fixE: function(a) {
        return (typeof a == "undefined" || !a ? window.event : a)
    },
    cancelEvent: function(b, c, a) {
        b = this.fixE(b);
        if (b.stopPropagation && !a) {
            b.stopPropagation()
        }
        if (b.preventDefault && !a) {
            b.preventDefault()
        }
        b.cancelBubble = true;
        b.cancel = true;
        b.returnValue = false;
        if (!c) {
            if (SD.isIE || SD.isIE7) {
                document.execCommand("Stop")
            } else {
                window.stop()
            }
        }
    },
    getCursorPos: function(g, f) {
        g = this.fixE(g);
        var h = SD.util.getTopLeft(f);
        var d, b, c, a;
        if (SD.isTouchDevice()) {
            if (g.touches && g.touches[0]) {
                d = g.touches[0].pageX;
                b = g.touches[0].pageY
            } else {
                if (g.changedTouches && g.changedTouches[0]) {
                    d = g.changedTouches[0].pageX;
                    b = g.changedTouches[0].pageY
                }
            }
        } else {
            d = (!document.all) ? g.pageX : (event.clientX + (document.documentElement.scrollLeft || document.body.scrollLeft));
            b = (!document.all) ? g.pageY : (event.clientY + (document.documentElement.scrollTop || document.body.scrollTop))
        }
        d -= h.x;
        b -= h.y;
        return {
            x: d,
            y: b,
            vx: c,
            vy: a
        }
    },
    getMouseButton: function(b) {
        b = this.fixE(b);
        var a = "LEFT";
        if (!b) {
            return "LEFT"
        }
        if (b.which == null) {
            a = (b.button < 2) ? "LEFT" : ((b.button == 4) ? "MIDDLE" : "RIGHT")
        } else {
            a = (b.which < 2) ? "LEFT" : ((b.which == 2) ? "MIDDLE" : "RIGHT")
        }
        return a
    },
    createElement: function(c, b, m, k, j, g, l, d, e, h, f) {
        var a = document.createElement(c);
        if (b != undefined && b != "") {
            a.id = b
        }
        if (m != undefined && m != "") {
            a.style.left = m
        }
        if (k != undefined && k != "") {
            a.style.top = k
        }
        if (j != undefined && j != "") {
            a.style.width = j
        }
        if (g != undefined && g != "") {
            a.style.height = g
        }
        if (l != undefined && l != "") {
            a.style.position = l
        }
        if (e != undefined && e != "") {
            a.src = e
        }
        if (d != undefined) {
            a.style.zIndex = d
        }
        if (h != undefined && h != "") {
            a.style.backgroundColor = h
        }
        if (f != undefined && f == true) {
            a.style.overflow = "hidden"
        }
        return a
    },
    createDiv: function(a, j, g, f, d, h, b, e, c) {
        return SD.util.createElement("div", a, j, g, f, d, h, b, "", e, c)
    },
    createImg: function(a, c, k, h, g, f, j, b, d) {
        var e = SD.util.createElement("img", a, k, h, g, f, j, b, c, "", d);
        e.style.filter = "Progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + c + "')";
        return e
    },
    createImgSprite: function(j, s, g, t, a, b, e, k, m, r, q) {
        q = (q == undefined) ? false : true;
        var c, p;
        if (SD.isIE6 && !q) {
            var n = document.createElement("div");
            b = (b == undefined) ? "" : "left:" + b + "px;";
            e = (e == undefined) ? "" : "top:" + (e) + "px;";
            k = (k == undefined) ? "" : k;
            n.style.cssText = "position:absolute; " + b + e + k;
            p = document.createElement("div");
            p.style.cssText = "width:" + s + "px; height:" + g + "px; position: relative; overflow:hidden;";
            var l = document.createElement("div");
            l.className = j;
            m = (m == undefined) ? 1000 : m;
            r = (r == undefined) ? 1000 : r;
            l.style.cssText = "width: " + m + "px; height: " + r + "px; position:absolute; left:" + (-t) + "px; top: " + (-a) + "px;";
            p.appendChild(l);
            n.appendChild(p);
            c = n
        } else {
            p = document.createElement("div");
            b = (b == undefined) ? "" : "left:" + b + "px;";
            e = (e == undefined) ? "" : "top:" + e + "px;";
            p.className = j;
            p.style.cssText = "background-position: " + (-t) + "px " + (-a) + "px;width:" + s + "px; height:" + g + "px; position:absolute;" + b + "" + e + k;
            c = p
        }
        return this.assignSpriteEvent(c, q)
    },
    assignSpriteEvent: function(b, a) {
        if (SD.isIE6 && !a) {
            b.setClassName = function(c) {
                b.childNodes[0].childNodes[0].className = c
            };
            b.setBgPosition = function(d, c) {
                b.childNodes[0].childNodes[0].style.left = -d + "px";
                b.childNodes[0].childNodes[0].style.top = -c + "px"
            };
            b.setWidth = function(c) {
                b.childNodes[0].style.width = c + "px"
            };
            b.setHeight = function(c) {
                b.childNodes[0].style.height = c + "px"
            };
            b.setTopLeft = function(c, d) {
                b.style.top = d + "px";
                b.style.left = c + "px"
            };
            b.getTopLeft = function() {
                return b.style.left + " " + b.style.top
            };
            b.getBgPosition = function() {
                return b.childNodes[0].childNodes[0].style.left + " " + b.childNodes[0].childNodes[0].style.top
            }
        } else {
            b.setClassName = function(c) {
                b.className = c
            };
            b.setBgPosition = function(d, c) {
                b.style.backgroundPosition = (-d) + "px " + (-c) + "px"
            };
            b.setWidth = function(c) {
                b.style.width = c + "px"
            };
            b.setHeight = function(c) {
                b.style.height = c + "px"
            };
            b.setTopLeft = function(c, d) {
                b.style.top = d + "px";
                b.style.left = c + "px"
            };
            b.getBgPosition = function() {
                return b.style.backgroundPosition
            };
            b.getTopLeft = function() {
                return b.style.left + " " + b.style.top
            }
        }
        return b
    },
    createInfoFrame: function(k, f, c, m, b, g, a) {
        var j = SD.util.createDiv("", c + "px", m + "px", k + "px", f + "px", "absolute", 0, "", true);
        var e = SD.util.createImg("", SD.IMG_URL + a, b + "px", g + "px", "", "", "absolute");
        e.style.border = "0px";
        j.appendChild(e);
        return j
    },
    purge: function(f) {
        if (f == null || f == undefined) {
            return
        }
        var c = f.attributes,
            e, b, g;
        if (c) {
            b = c.length;
            for (e = 0; e < b; e += 1) {
                g = c[e].name;
                if (typeof f[g] === "function") {
                    f[g] = null
                }
            }
        }
        c = f.childNodes;
        if (c) {
            b = c.length;
            for (e = 0; e < b; e += 1) {
                this.purge(f.childNodes[e])
            }
        }
    },
    getHttpObject: function() {
        var a;
        try {
            a = new XMLHttpRequest()
        } catch (b) {
            try {
                a = new ActiveXObject("Microsoft.XMLHTTP")
            } catch (b) {
                try {
                    a = new ActiveXObject("Msxml2.XMLHTTP")
                } catch (b) {
                    alert("Your browser does not support AJAX!");
                    return false
                }
            }
        }
        return a
    },
    initVML: function() {
        if (!SD.VECTOR_LOADED) {
            if (SD.isIE8) {
                document.namespaces.add("v", "urn:schemas-microsoft-com:vml");
                var c = document.createStyleSheet();
                var a = ["group", "oval", "stroke", "fill", "polyline", "line", "path", "textpath", "rect", "skew"];
                for (var b = 0; b < a.length; b++) {
                    c.addRule("v\\:" + a[b], "behavior: url(#default#VML);")
                }
            } else {
                if (!document.namespaces.v) {
                    document.namespaces.add("v", "urn:schemas-microsoft-com:vml");
                    document.createStyleSheet().addRule("v\\:*", "behavior: url(#default#VML);")
                }
            }
            SD.VECTOR_LOADED = true
        }
    },
    Ajax: function(b, d) {
        var c = SD.util.getHttpObject();
        c.onreadystatechange = a;

        function a() {
            if (c.readyState == 4) {
                if (c.status == 200) {
                    if (d) {
                        d(c.responseXML)
                    }
                }
            }
        }
        this.doGet = function() {
            c.open("GET", b, true);
            c.send(null)
        };
        this.doPost = function(e, f) {
            c.open("POST", b, true);
            c.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            if (f == true || f != undefined) {
                c.setRequestHeader("Content-Type", "text/xml")
            }
            c.send(e)
        }
    },
    checkMouseLeave: function(b, a) {
        var a = window.event || a;
        if (b.contains && a.toElement) {
            return !b.contains(a.toElement)
        } else {
            if (a.relatedTarget) {
                return !this.containsDOM(b, a.relatedTarget)
            }
        }
    },
    checkMouseEnter: function(b, a) {
        var a = window.event || a;
        if (b.contains && a.fromElement) {
            return !b.contains(a.fromElement)
        } else {
            if (a.relatedTarget) {
                return !this.containsDOM(b, a.relatedTarget)
            }
        }
    },
    containsDOM: function(a, c) {
        var b = false;
        do {
            if ((b = a == c)) {
                break
            }
            try {
                c = c.parentNode
            } catch (d) {
                c = null
            }
        } while (c != null);
        return b
    }
};
SD.drawing.setTilePosition = function(a, e, d, b, h, g, f) {
    if (d.img == null) {
        return
    }
    var c = {
        w: a.mapTileSize.x,
        h: a.mapTileSize.y
    };
    if (SD.isIE || SD.isIE7 || SD.isIphone) {
        c = {
            w: Math.ceil(a.mapTileSize.x),
            h: Math.ceil(a.mapTileSize.y)
        }
    }
    e.left = ((b - g) * c.w) + a.offsetContainer.x;
    e.top = ((h - f) * c.h) + a.offsetContainer.y;
    d.top = e.top;
    d.left = e.left;
    e.setWidth(c.w);
    e.setHeight(c.h);
    d.img.style.position = "absolute";
    d.img.style.width = c.w + "px";
    d.img.style.height = c.h + "px";
    d.img.style.top = e.top + "px";
    d.img.style.left = e.left + "px"
};
SD.drawing.Point = function(a, b) {
    this.x = a;
    this.y = b
};
SD.drawing.GeoPoint = function(a, b) {
    this.lon = a;
    this.lat = b
};
SD.drawing.Size = function(b, a) {
    this.width = b;
    this.height = a
};
SD.drawing.Rectangle = function(d, c, b, a) {
    this.left = d;
    this.top = c;
    this.right = b;
    this.bottom = a;
    this.setWidth = function(e) {
        this.right = this.left + e
    };
    this.setHeight = function(e) {
        this.bottom = this.top + e
    };
    this.offset = function(e, f) {
        this.left = d + e;
        this.top = top + f;
        this.right = b + e;
        this.bottom = a + f
    };
    this.width = function() {
        return Math.abs(this.right - this.left)
    };
    this.height = function() {
        return Math.abs(this.bottom - this.top)
    }
};
SD.genmap.OverlayManager = function() {
    this.node = [];
    this.index = 0
};
SD.genmap.OverlayManager.prototype = {
    _add: function(a) {
        a.index = this.index;
        this.node.push(a);
        this.index++
    },
    _remove: function(c) {
        if (c == undefined || c == null) {
            return
        }
        var a = -1;
        for (var b = 0; b < this.node.length; b++) {
            if (c == this.node[b]) {
                a = b;
                break
            }
        }
        if (a != -1) {
            this.node.splice(a, 1)
        }
    },
    _isExist: function(b) {
        var d = this.node.length;
        if (d > 0) {
            for (var a = 0; a < d; a++) {
                if (b.index == this.node[a].index || (b.guid && this.node[a]._guid && b.guid == this.node[a]._guid)) {
                    return this.node[a]
                }
            }
        }
        return false
    },
    _clear: function() {
        if (this.node.length < 0) {
            return
        }
        var a = 0;
        while (a < this.node.length) {
            this.remove(this.node[a])
        }
        this.node = []
    }
};
var Point = SD.drawing.Point,
    Vertex = SD.drawing.Point,
    GeoPoint = SD.drawing.GeoPoint,
    GLatLng = SD.drawing.GeoPoint,
    Size = SD.drawing.Size,
    Rectangle = SD.drawing.Rectangle;
SD.API_URL = "http://www.streetdirectory.com/";
SD.BASE_URL = "http://x1.sdimgs.com/dragmap/xg/";
SD.IMG_URL = "http://x1.sdimgs.com/dragmap/xg/img/";
SD.MAP_PRE = "cf0";
SD.MAP_URL = "sdimgs.com/map/";
SD.GA_URL = "http://www.streetdirectory.com/sd_ga.php?utmac=MO-15222285-66&utmp=/map_api/replace_this&guid=ON";
SD.MAP_VERSION = "1.0.0.555";
SD.ns("SD.mgr");
SD.mgr.Setup = function(o, m, n) {
    eval("SD.mgr.__" + n + " = {i:0,a:[]};");
    m = function(options) {
        var _o = new o(options);
        var _m = eval("SD.mgr.__" + n);
        _m.a.push(_o);
        _m.i++
    }
};
var EventManager = (function() {
    this.api = null;
    var b = [];

    function i(j) {
        return (j === "mousemove" || j === "DOMMouseScroll" || j === "mousewheel")
    }

    function h(n, m, l, o) {
        if (typeof n[m] != "undefined" && n[m].register) {
            n[m].register(l, n[m]);
            return true
        }
        var k = n;
        if (typeof n.getObject === "function") {
            k = n.getObject()
        }
        if (i(m)) {
            if (k.addEventListener) {
                k.addEventListener(m, l, false)
            } else {
                if (k.attachEvent) {
                    k.attachEvent("on" + m, l)
                } else {
                    k["on" + m] = l
                }
            }
        } else {
            k = c(k, m, l, o)
        }
        var j = "EVENT_SD_" + l.$$guid;
        b[j] = {
            o: k,
            type: m,
            fc: l
        };
        return j
    }

    function c(k, m, l, n) {
        if (typeof(l.$$guid) == "undefined") {
            l.$$guid = c.guid++
        }
        if (!k.events) {
            k.events = {}
        }
        var j = k.events[m];
        if (!j) {
            j = k.events[m] = {};
            if (k["on" + m]) {
                j[0] = k["on" + m]
            }
        }
        j[l.$$guid] = l;
        k["on" + m] = g;
        if (n == undefined && api != null && api.pushEvent) {
            api.pushEvent(el, m, l)
        }
    }
    c.guid = 1;

    function d(j, l, k) {
        if (i(l)) {
            if (j.removeEventListener) {
                j.removeEventListener(l, k, false)
            } else {
                if (j.detachEvent) {
                    j.detachEvent("on" + l, k)
                } else {
                    f(j, l, k)
                }
            }
        }
    }

    function f(j, l, k) {
        if (j.events && j.events[l]) {
            delete j.events[l][k.$$guid]
        }
    }

    function g(m) {
        m = m || a(window.event);
        var l = true;
        var j = this.events[m.type];
        for (var k in j) {
            if (!Object.prototype[k]) {
                this.$$handler = j[k];
                if (this.$$handler(m) === false) {
                    l = false
                }
            }
        }
        if (this.$$handler) {
            this.$$handler = null
        }
        return l
    }

    function e() {
        for (var j in b) {
            if (b[j] == null || typeof b[j] === "function") {
                continue
            }
            d(b[j].o, b[j].type, b[j].fc);
            b[j] = null
        }
    }

    function a(j) {
        j.preventDefault = a.preventDefault;
        j.stopPropagation = a.stopPropagation;
        return j
    }
    a.preventDefault = function() {
        this.returnValue = false
    };
    a.stopPropagation = function() {
        this.cancelBubble = true
    };
    if (!window.addEventListener) {
        document.onreadystatechange = function() {
            if (window.onload && window.onload != g) {
                c(window, "load", window.onload);
                window.onload = g
            }
        }
    }
    return {
        add: h,
        remove: d,
        removeAll: e
    }
})();

function EventDelegates() {
    this.nodes = []
}
EventDelegates.prototype = {
    isAvailable: function() {
        return this.nodes.length > 0 ? true : false
    },
    register: function(b, a) {
        this.nodes.push({
            fn: b,
            obj: a
        })
    },
    triggered: function(b) {
        if (!this.isAvailable()) {
            return
        }
        for (var a = 0; a < this.nodes.length; a++) {
            if (!this.nodes[a]) {
                continue
            }
            this.nodes[a].fn.call(this.nodes[a].obj, b)
        }
    }
};
SD.ns("SD.layer");
SD.layer.StdDiv = function(a) {
    this.div = document.createElement("div");
    if (a) {
        this.div.setAttribute("id", a)
    }
    this.div.style.cssText = "position:absolute; z-Index:0; top:0px; left:0px;";
    this.rect = {
        x: 0,
        y: 0
    };
    this.scale = 1;
    this.cleanAbsolute = function() {
        this.div.style.cssText = ""
    };
    this.add = function(b) {
        this.div.appendChild(b)
    };
    this.remove = function(b) {
        this.div.removeChild(b)
    };
    this.getObject = function() {
        return this.div
    };
    this.clear = function() {
        this.scale = 1;
        if (this.div.hasChildNodes()) {
            while (this.div.firstChild) {
                SD.util.purge(this.div.firstChild);
                this.div.removeChild(this.div.firstChild)
            }
        }
    };
    this.setId = function(b) {
        this.div.setAttribute("id", b)
    };
    this.setOffset = function(b) {
        this.rect.x += b.x;
        this.rect.y += b.y;
        this.div.style.left = this.rect.x + "px";
        this.div.style.top = this.rect.y + "px"
    };
    this.setTopLeft = function(b) {
        this.rect.x = b.x;
        this.rect.y = b.y;
        this.div.style.left = b.x + "px";
        this.div.style.top = b.y + "px"
    };
    this.setTransform = function(c, b) {
        this.scale = c;
        if (SD.isIE) {
            this.div.style.filter = "progid:DXImageTransform.Microsoft.Matrix(FilterType='nearest', M11=" + c + ", M21=0, M12=0, M22=" + c + ", dX=" + b.x + ", dY=" + b.y + ")";
            if (isNaN(parseInt(this.div.style.width))) {
                this.div.style.width = "100%";
                this.div.style.height = "100%"
            }
            this.div.style.transformOrigin = "0pt 0pt";
            this.div.style.transform = "matrix(" + c + ",0,0," + c + "," + b.x + "," + b.y + ")"
        } else {
            if (SD.isOpera) {
                this.div.style.OTransformOrigin = "0 0";
                this.div.style.OTransform = "matrix(" + c + ",0,0," + c + "," + b.x + "," + b.y + ")"
            } else {
                if (SD.isSafari) {
                    this.div.style.WebkitTransformOriginX = "0px";
                    this.div.style.WebkitTransformOriginY = "0px";
                    this.div.style.WebkitTransform = "matrix(" + c + ",0,0," + c + "," + b.x + "," + b.y + ")"
                } else {
                    this.div.style.MozTransformOrigin = "0pt 0pt";
                    this.div.style.MozTransform = "matrix(" + c + ",0,0," + c + "," + b.x + "px," + b.y + "px)"
                }
            }
        }
        this.div.style.whiteSpace = "nowrap";
        this.div.style.lineHeight = "0";
        this.div.style.display = "block"
    };
    this.setUnTransform = function() {
        this.scale = 1;
        this.div.style.filter = "";
        this.div.style.OTransform = "";
        this.div.style.WebkitTransform = "";
        this.div.style.MozTransform = "";
        this.setDisplay(false)
    };
    this.setWidth = function(b) {
        this.div.style.width = b.width + "px";
        this.div.style.height = b.height + "px"
    };
    this.appendToDom = function(c) {
        c = typeof c == "string" ? document.getElementById(c) : c;
        if (c == undefined || c.style == undefined) {
            return
        }
        var b = {
            width: c.clientWidth == 0 ? parseInt(c.style.width) : c.clientWidth,
            height: c.clientHeight == 0 ? parseInt(c.style.height) : c.clientHeight
        };
        this.setWidth(b);
        c.appendChild(this.div)
    };
    this.setDisplay = function(b) {
        var c = "none";
        if (b) {
            c = ""
        }
        this.div.style.display = c
    };
    this.isDisplayed = function() {
        return this.div.style.display == ""
    }
};
SD.layer.StdLayer = function(a) {
    SD.apply(this, new SD.layer.StdDiv(a));
    this.node = [];
    this.enable = true;
    this.setEnable = function(c) {
        this.enable = c;
        this.setDisplay(c);
        if (this.node.length == 0) {
            return
        }
        for (var b = this.node.length - 1; b > -1; b--) {
            if (this.node[b] == undefined) {
                break
            }
            if (this.node[b].setEnable && this.node[b].setDisplay) {
                this.node[b].setEnable(c);
                this.node[b].setDisplay(c)
            }
        }
    };
    this.addNode = function(b) {
        if (!b.div) {
            return
        }
        this.div.appendChild(b.div);
        this.node.push(b)
    };
    this.replaceNode = function(b, c) {
        for (var d = 0; d < this.node.length; d++) {
            if (this.node[d] == b) {
                this.node[d] = c;
                this.div.replaceChild(c.div, b.div)
            }
        }
    };
    this.addBefore = function(d, b) {
        for (var c = 0; c < this.node.length; c++) {
            if (this.node[c] == d) {
                this.div.insertBefore(b.div, d.div);
                this.node.push(b)
            }
        }
    };
    this.removeNode = function(c) {
        var b = -1;
        for (var d = 0; d < this.node.length; d++) {
            if (this.node[d] == c) {
                b = d;
                break
            }
        }
        if (b != -1) {
            this.node.splice(b, 1);
            this.div.removeChild(c.div)
        }
    }
};
SD.layer.SDLayer = function(a) {
    SD.apply(this, new SD.layer.StdLayer(a));
    this.draw = function(b, g, h, e, f) {
        if (!this.enable) {
            return
        }
        for (var d = 0, k = this.node.length; d < k; d++) {
            if (this.node[d].draw) {
                this.node[d].draw(b, g, h, e, f)
            }
        }
    };
    this.update = function(b, g, h, e, f) {
        if (!this.enable) {
            return
        }
        for (var d = 0, k = this.node.length; d < k; d++) {
            if (this.node[d].update) {
                this.node[d].update(b, g, h, e, f)
            }
        }
    }
};
SD.layer.DrawingLayer = function() {
    SD.apply(this, new SD.layer.SDLayer("id_drawing_layer"));
    this.setEnable = function(b) {
        this.enable = b;
        for (var a = 0; a < this.node.length; a++) {
            if (this.node[a].setEnable) {
                this.node[a].setEnable(b);
                this.node[a].setDisplay(b)
            }
        }
        this.setDisplay(b)
    }
};
SD.layer.MarkerStaticLayer = function() {
    SD.apply(this, new SD.layer.StdLayer("id_marker_static_layer"));
    this.setEnable = function(a) {
        this.setDraw(a)
    };
    this.setDraw = function(a) {
        this.enable = a;
        this.setDisplay(a)
    };
    this.draw = function(a, e, f, c, d) {
        if (!this.enable) {
            return
        }
        for (var b = 0; b < this.node.length; b++) {
            if (this.node[b].draw) {
                this.node[b].draw(a, e, f, c, d)
            }
        }
        this.enable = false
    }
};
SD.layer.MapObject = function() {
    SD.apply(this, new SD.layer.StdLayer("id_map_layer"));
    this.r = new Rectangle(0, 0, 0, 0);
    this.bounds = new Rectangle(0, 0, 0, 0);
    this.tiles = new MapRowCols();
    this.cssName = null;
    this.OnCompleted = new EventDelegates();
    var b = 0;
    var a = 0;
    this.draw = function(c, f, g, d, e) {
        if (!this.enable) {
            return
        }
        this.onDraw(c);
        this.tiles = c.mapConfig.createList(g, f, e, d);
        this.setDisplay(true);
        this._draw(c, f, g, d, e)
    };
    this.onDraw = function(c) {};
    this.update = function(r) {
        if (r.mapRowCols == undefined || !this.enable) {
            return
        }
        this.onDraw(r, true);
        var v = r.mapConfig;
        var o = this.tiles.node;
        var h = r.topLeftContainer;
        var n = r.pixelMargin;
        var u = n.width();
        var s = n.height();
        for (var q = 0; q < o.length; q++) {
            var l = o[q].top;
            var e = o[q].left;
            var m = o[q].top + h.y;
            var f = o[q].left + h.x;
            var c = {
                left: f < n.left,
                right: f > n.right
            };
            var t = m > n.bottom || m < n.top;
            var p = c.left || c.right;
            if (t || p) {
                if (t) {
                    l += (m > 0 ? -1 : 1) * s
                }
                if (p) {
                    e += (f > 0 ? -1 : 1) * u
                }
                var g = this.bounds.left + Math.ceil(e / r.mapTileSize.x);
                var k = this.bounds.top + Math.ceil(l / r.mapTileSize.y);
                var d = v.getBoundCol(g);
                o[q].col = g;
                o[q].row = k;
                this.reloadImage(k, d, o[q].img, v);
                if (o[q].img == null) {
                    continue
                }
                o[q].img.style.position = "absolute";
                o[q].img.style.width = r.mapTileSize.x + "px";
                o[q].img.style.height = r.mapTileSize.y + "px";
                o[q].img.style.top = l + "px";
                o[q].img.style.left = e + "px";
                o[q].top = l;
                o[q].left = e
            }
        }
    };
    this.reloadImage = function(g, f, d, e) {
        if (d == null) {
            return
        }
        d.removeAttribute("src");
        d.style.display = "none";
        d.onCompleted = this.OnCompleted;
        var c = this;
        d.onload = function() {
            this.style.display = "";
            b++;
            if (b == a) {
                c.OnCompleted.triggered();
                b = 0
            }
        };
        if (g > 0 && f > 0) {
            d.setAttribute("src", this.getTileUrl(g, f, e))
        }
    };
    this.appendImage = function(d, f, c, e) {
        if (d && d.img == null) {
            d.img = document.createElement("img");
            this.div.appendChild(d.img);
            if (this.cssName != null) {
                d.img.className = this.cssName
            }
            this.reloadImage(f, c, d.img, e)
        }
    };
    this.getTileUrl = function(e, d, c) {
        return c.getTileUrl(e, d)
    };
    this.cleanUp = function(g, h) {
        var d = this.tiles.getIntersectionRect(g, this.tiles.getBounds()),
            f;
        if (d.length > 0) {
            for (var e = 0, k = d.length; e < k; e++) {
                f = this.tiles.getMap(d[e].row, d[e].col, h.name, h.realLevel);
                if (f.img === null || !f) {
                    continue
                }
                this.remove(f.img);
                this.tiles.remove(f)
            }
        }
    };
    this._draw = function(c, n, h, k, e) {
        var m = c.mapConfig;
        var f;
        b = 0;
        a = (e - h + 1) * (k - n + 1);
        this.bounds = new Rectangle(h, n, e, k);
        this.cleanUp(this.bounds, m);
        for (var l = h; l <= e; l++) {
            for (var g = n; g <= k; g++) {
                var d = m.getBoundCol(l);
                f = this.tiles.getMap(g, l, m.name, m.realLevel);
                if (!f) {
                    f = this.tiles.addNode(g, l, m.name, m.realLevel)
                }
                if (m.isInRect(g, d)) {
                    this.appendImage(f, g, d, m)
                } else {
                    a--
                }
                if (!f.img || f.img == null) {
                    continue
                }
                SD.drawing.setTilePosition(c, this.r, f, l, g, h, n)
            }
        }
    };
    this.reOrderRowCol = function(t, q, r, o) {
        var k = [];
        var l = (o - q + 1) * (r - t + 1);
        var c = Math.floor((o - q - 1) / 2);
        var s = Math.floor((r - t) / 2);
        var v = t + s;
        var f = q + c;
        var d = 1;
        var e = true;
        k[0] = {
            row: v,
            col: f
        };
        var m = 1;
        while (m <= l) {
            var g = d % 2 == 0 ? -1 : 1;
            for (var h = 0; h < 2; h++) {
                for (j = 0; j < d; j++) {
                    if (e) {
                        f += g
                    } else {
                        v += g
                    }
                    var n = v <= r && v >= t;
                    var u = f <= o && f >= q;
                    if (u && n) {
                        k.push({
                            row: v,
                            col: f
                        })
                    }
                }
                e = !e
            }
            d++;
            m++
        }
        return k
    };
    this.setCC = function(d) {
        if (d == undefined || d == null || d == "") {
            return
        }
        var c = this.tiles.node;
        for (var e = 0; e < c.length; e++) {
            if (c[e].img != null) {
                c[e].img.className = d
            }
        }
        this.cssName = d
    }
};
SD.layer.ZoomObject = function() {
    SD.apply(this, new SD.layer.StdLayer("id_zoom_layer"));
    this.r = new Rectangle(0, 0, 0, 0);
    this.mapList = new MapRowCols();
    this.isRender = true;
    this.draw = function(a, k, d, f, c) {
        if (!this.enable) {
            return
        }
        var h = a.mapConfig;
        this.setDisplay(true);
        for (var g = d; g <= c; g++) {
            for (var e = k; e <= f; e++) {
                var b = this.mapList.getMap(e, g, h.name, h.realLevel);
                if (!b || b.img == null) {
                    continue
                }
                SD.drawing.setTilePosition(a, this.r, b, g, e, d, k);
                if (b.hasAppend == undefined) {
                    b.img.style.display = "";
                    this.div.appendChild(b.img);
                    b.hasAppend = true
                }
            }
        }
        this.isRender = false
    }
};
var StdDiv = SD.layer.StdDiv,
    StdLayer = SD.layer.StdLayer,
    SDLayer = SD.layer.SDLayer,
    DrawingLayer = SD.layer.DrawingLayer,
    MarkerStaticLayer = SD.layer.MarkerStaticLayer,
    MapObject = SD.layer.MapObject,
    ZoomObject = SD.layer.ZoomObject;

function LayerObject() {
    SD.apply(this, new StdLayer());
    this.r = new Rectangle(0, 0, 0, 0);
    this.projection = (new SD.projection.Server()).get("UTM WGS-1984 48N");
    this.getDataUrl = function(c, b, a, d) {
        return "http://sdlocal/api/index.php/layer/data/?s=" + a + "&r=" + c + "&c=" + b + "&l=" + d
    };
    this.getTileUrl = function(c, b, a, d) {
        return "http://sdlocal/api/index.php/layer/get/?s=" + a + "&r=" + c + "&c=" + b + "&l=" + d
    };
    this.parseData = function(b, d, a) {
        var f = [],
            h = {
                name: "",
                x: 0,
                y: 0,
                px: 0,
                py: 0
            };
        var e = b.getElementsByTagName("POI");
        if (e.length == 0) {
            return
        }
        for (i = 0; i < e.length; i++) {
            var c = e.item(i).attributes;
            h.name = c.getNamedItem("NAME").nodeValue;
            h.x = parseInt(c.getNamedItem("X").nodeValue);
            h.y = parseInt(c.getNamedItem("Y").nodeValue);
            if (h.x > 0 && h.y > 0) {
                var g = this.projection.metricToScreen(h.x, h.y, a.scale, a.topLeftScreen);
                h.px = g.x;
                h.py = g.y
            }
            f.push(h)
        }
        EventManager.add(d, "mouseover", function(l) {
            var k = SD.util.getCursorPos(l, this);
            SD.util.debug(k.x + " : " + k.y, true)
        })
    };
    this.draw = function(a, r, k, p, f) {
        if (!this.enable || this.projection.name != a.projection.name) {
            return
        }
        var l = this;
        var m = 0,
            e = 0,
            n, d;
        var s = a.mapTileSize;
        var q = a.mapConfig;
        n = s.x;
        d = s.y;
        this.clear();
        this.setDisplay(true);
        for (var o = k; o <= f; o++) {
            for (var g = r; g <= p; g++) {
                if (g < 1 || o < 1 || o > q.totalMapCol || g > q.totalMapRow) {
                    continue
                }
                this.r.left = ((o - k) * s.x) + a.offsetContainer.x;
                this.r.top = ((g - r) * s.y) + a.offsetContainer.y;
                this.r.setWidth(n);
                this.r.setHeight(d);
                var c = document.createElement("img");
                c.style.display = "none";
                c.src = this.getTileUrl(g, o, q.name, q.tileLevel);
                c.onload = function() {
                    this.style.display = ""
                };
                var b = this.getDataUrl(g, o, q.name, q.tileLevel);
                (new SD.util.Ajax(b, function(h) {
                    l.parseData(h, c, a)
                })).doGet();
                c.style.position = "absolute";
                c.style.width = this.r.width() + "px";
                c.style.height = this.r.height() + "px";
                c.style.top = this.r.top + "px";
                c.style.left = this.r.left + "px";
                this.div.appendChild(c)
            }
        }
    }
};
var Aes = {};
Aes.cipher = function(e, a) {
    var d = 4;
    var h = a.length / d - 1;
    var g = [
        [],
        [],
        [],
        []
    ];
    for (var f = 0; f < 4 * d; f++) {
        g[f % 4][Math.floor(f / 4)] = e[f]
    }
    g = Aes.addRoundKey(g, a, 0, d);
    for (var c = 1; c < h; c++) {
        g = Aes.subBytes(g, d);
        g = Aes.shiftRows(g, d);
        g = Aes.mixColumns(g, d);
        g = Aes.addRoundKey(g, a, c, d)
    }
    g = Aes.subBytes(g, d);
    g = Aes.shiftRows(g, d);
    g = Aes.addRoundKey(g, a, h, d);
    var b = new Array(4 * d);
    for (var f = 0; f < 4 * d; f++) {
        b[f] = g[f % 4][Math.floor(f / 4)]
    }
    return b
};
Aes.keyExpansion = function(f) {
    var d = 4;
    var b = f.length / 4;
    var g = b + 6;
    var e = new Array(d * (g + 1));
    var h = new Array(4);
    for (var c = 0; c < b; c++) {
        var a = [f[4 * c], f[4 * c + 1], f[4 * c + 2], f[4 * c + 3]];
        e[c] = a
    }
    for (var c = b; c < (d * (g + 1)); c++) {
        e[c] = new Array(4);
        for (var j = 0; j < 4; j++) {
            h[j] = e[c - 1][j]
        }
        if (c % b == 0) {
            h = Aes.subWord(Aes.rotWord(h));
            for (var j = 0; j < 4; j++) {
                h[j] ^= Aes.rCon[c / b][j]
            }
        } else {
            if (b > 6 && c % b == 4) {
                h = Aes.subWord(h)
            }
        }
        for (var j = 0; j < 4; j++) {
            e[c][j] = e[c - b][j] ^ h[j]
        }
    }
    return e
};
Aes.subBytes = function(b, a) {
    for (var d = 0; d < 4; d++) {
        for (var e = 0; e < a; e++) {
            b[d][e] = Aes.sBox[b[d][e]]
        }
    }
    return b
};
Aes.shiftRows = function(d, a) {
    var b = new Array(4);
    for (var e = 1; e < 4; e++) {
        for (var f = 0; f < 4; f++) {
            b[f] = d[e][(f + e) % a]
        }
        for (var f = 0; f < 4; f++) {
            d[e][f] = b[f]
        }
    }
    return d
};
Aes.mixColumns = function(h, f) {
    for (var j = 0; j < 4; j++) {
        var e = new Array(4);
        var d = new Array(4);
        for (var g = 0; g < 4; g++) {
            e[g] = h[g][j];
            d[g] = h[g][j] & 128 ? h[g][j] << 1 ^ 283 : h[g][j] << 1
        }
        h[0][j] = d[0] ^ e[1] ^ d[1] ^ e[2] ^ e[3];
        h[1][j] = e[0] ^ d[1] ^ e[2] ^ d[2] ^ e[3];
        h[2][j] = e[0] ^ e[1] ^ d[2] ^ e[3] ^ d[3];
        h[3][j] = e[0] ^ d[0] ^ e[1] ^ e[2] ^ d[3]
    }
    return h
};
Aes.addRoundKey = function(f, a, d, b) {
    for (var e = 0; e < 4; e++) {
        for (var g = 0; g < b; g++) {
            f[e][g] ^= a[d * 4 + g][e]
        }
    }
    return f
};
Aes.subWord = function(a) {
    for (var b = 0; b < 4; b++) {
        a[b] = Aes.sBox[a[b]]
    }
    return a
};
Aes.rotWord = function(a) {
    var c = a[0];
    for (var b = 0; b < 3; b++) {
        a[b] = a[b + 1]
    }
    a[3] = c;
    return a
};
Aes.sBox = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22];
Aes.rCon = [
    [0, 0, 0, 0],
    [1, 0, 0, 0],
    [2, 0, 0, 0],
    [4, 0, 0, 0],
    [8, 0, 0, 0],
    [16, 0, 0, 0],
    [32, 0, 0, 0],
    [64, 0, 0, 0],
    [128, 0, 0, 0],
    [27, 0, 0, 0],
    [54, 0, 0, 0]
];
Aes.Ctr = {};
Aes.Ctr.encrypt = function(j, a, u) {
    var k = 16;
    if (!(u == 128 || u == 192 || u == 256)) {
        return ""
    }
    j = Utf8.encode(j);
    a = Utf8.encode(a);
    var l = u / 8;
    var f = new Array(l);
    for (var s = 0; s < l; s++) {
        f[s] = isNaN(a.charCodeAt(s)) ? 0 : a.charCodeAt(s)
    }
    var z = Aes.cipher(f, Aes.keyExpansion(f));
    z = z.concat(z.slice(0, l - 16));
    var e = new Array(k);
    var t = (new Date()).getTime();
    var g = t % 1000;
    var d = Math.floor(t / 1000);
    var p = Math.floor(Math.random() * 65535);
    for (var s = 0; s < 2; s++) {
        e[s] = (g >>> s * 8) & 255
    }
    for (var s = 0; s < 2; s++) {
        e[s + 2] = (p >>> s * 8) & 255
    }
    for (var s = 0; s < 4; s++) {
        e[s + 4] = (d >>> s * 8) & 255
    }
    var n = "";
    for (var s = 0; s < 8; s++) {
        n += String.fromCharCode(e[s])
    }
    var w = Aes.keyExpansion(z);
    var r = Math.ceil(j.length / k);
    var m = new Array(r);
    for (var x = 0; x < r; x++) {
        for (var v = 0; v < 4; v++) {
            e[15 - v] = (x >>> v * 8) & 255
        }
        for (var v = 0; v < 4; v++) {
            e[15 - v - 4] = (x / 4294967296 >>> v * 8)
        }
        var h = Aes.cipher(e, w);
        var q = x < r - 1 ? k : (j.length - 1) % k + 1;
        var o = new Array(q);
        for (var s = 0; s < q; s++) {
            o[s] = h[s] ^ j.charCodeAt(x * k + s);
            o[s] = String.fromCharCode(o[s])
        }
        m[x] = o.join("")
    }
    var y = n + m.join("");
    y = base64_encode(y);
    return y
};
Aes.Ctr.decrypt = function(t, e, p) {
    var m = 16;
    if (!(p == 128 || p == 192 || p == 256)) {
        return ""
    }
    t = base64_decode(t);
    e = Utf8.encode(e);
    var n = p / 8;
    var j = new Array(n);
    for (var o = 0; o < n; o++) {
        j[o] = isNaN(e.charCodeAt(o)) ? 0 : e.charCodeAt(o)
    }
    var u = Aes.cipher(j, Aes.keyExpansion(j));
    u = u.concat(u.slice(0, n - 16));
    var f = new Array(8);
    ctrTxt = t.slice(0, 8);
    for (var o = 0; o < 8; o++) {
        f[o] = ctrTxt.charCodeAt(o)
    }
    var r = Aes.keyExpansion(u);
    var g = Math.ceil((t.length - 8) / m);
    var h = new Array(g);
    for (var s = 0; s < g; s++) {
        h[s] = t.slice(8 + s * m, 8 + s * m + m)
    }
    t = h;
    var a = new Array(t.length);
    for (var s = 0; s < g; s++) {
        for (var q = 0; q < 4; q++) {
            f[15 - q] = ((s) >>> q * 8) & 255
        }
        for (var q = 0; q < 4; q++) {
            f[15 - q - 4] = (((s + 1) / 4294967296 - 1) >>> q * 8) & 255
        }
        var l = Aes.cipher(f, r);
        var d = new Array(t[s].length);
        for (var o = 0; o < t[s].length; o++) {
            d[o] = l[o] ^ t[s].charCodeAt(o);
            d[o] = String.fromCharCode(d[o])
        }
        a[s] = d.join("")
    }
    var k = a.join("");
    console.log(k);
    k = Utf8.decode(k);
    return k
};
var Utf8 = {};
Utf8.encode = function(a) {
    var b = a.replace(/[\u0080-\u07ff]/g, function(e) {
        var d = e.charCodeAt(0);
        return String.fromCharCode(192 | d >> 6, 128 | d & 63)
    });
    b = b.replace(/[\u0800-\uffff]/g, function(e) {
        var d = e.charCodeAt(0);
        return String.fromCharCode(224 | d >> 12, 128 | d >> 6 & 63, 128 | d & 63)
    });
    return b
};
Utf8.decode = function(b) {
    var a = b.replace(/[\u00e0-\u00ef][\u0080-\u00bf][\u0080-\u00bf]/g, function(e) {
        var d = ((e.charCodeAt(0) & 15) << 12) | ((e.charCodeAt(1) & 63) << 6) | (e.charCodeAt(2) & 63);
        return String.fromCharCode(d)
    });
    a = a.replace(/[\u00c0-\u00df][\u0080-\u00bf]/g, function(e) {
        var d = (e.charCodeAt(0) & 31) << 6 | e.charCodeAt(1) & 63;
        return String.fromCharCode(d)
    });
    return a
};
Utf8.decode2 = function(a) {
    return decodeURIComponent(escape(a))
};
Utf8.gdecode = function(c, e, m) {
    var p = function(b) {
        b = b.replace(/\\'/g, "'");
        b = b.replace(/\\"/g, '"');
        b = b.replace(/\\0/g, "\0");
        b = b.replace(/\\\\/g, "\\");
        return b
    };
    c = p(c);
    var g = c.length;
    var f = 0;
    var i = [];
    var l = 0;
    var o = 0;
    var d = (e != undefined) ? e : true;
    var q = (m != undefined) ? m : "lonlat";
    try {
        while (f < g) {
            var n;
            var a = 0;
            var r = 0;
            do {
                n = c.charCodeAt(f++) - 63;
                r |= (n & 31) << a;
                a += 5
            } while (n >= 32);
            var k = ((r & 1) ? ~(r >> 1) : (r >> 1));
            o += k;
            a = 0;
            r = 0;
            do {
                n = c.charCodeAt(f++) - 63;
                r |= (n & 31) << a;
                a += 5
            } while (n >= 32);
            var h = ((r & 1) ? ~(r >> 1) : (r >> 1));
            l += h;
            if (q == "lonlat") {
                i.push({
                    lon: (o * (d ? 0.00001 : 0.1)),
                    lat: (l * (d ? 0.00001 : 0.1))
                })
            } else {
                if (q == "xy") {
                    i.push({
                        x: (o * (d ? 0.00001 : 0.1)),
                        y: (l * (d ? 0.00001 : 0.1))
                    })
                }
            }
        }
    } catch (j) {}
    return i
};
Base64 = {
    keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    encode: function(c) {
        c = escape(c);
        var a = "";
        var k, h, f = "";
        var j, g, e, d = "";
        var b = 0;
        do {
            k = c.charCodeAt(b++);
            h = c.charCodeAt(b++);
            f = c.charCodeAt(b++);
            j = k >> 2;
            g = ((k & 3) << 4) | (h >> 4);
            e = ((h & 15) << 2) | (f >> 6);
            d = f & 63;
            if (isNaN(h)) {
                e = d = 64
            } else {
                if (isNaN(f)) {
                    d = 64
                }
            }
            a = a + this.keyStr.charAt(j) + this.keyStr.charAt(g) + this.keyStr.charAt(e) + this.keyStr.charAt(d);
            k = h = f = "";
            j = g = e = d = ""
        } while (b < c.length);
        return a
    },
    decode: function(d) {
        var b = "";
        var l, j, g = "";
        var k, h, f, e = "";
        var c = 0;
        var a = /[^A-Za-z0-9\+\/\=]/g;
        if (a.exec(d)) {
            alert("There were invalid base64 characters in the input text.\nValid base64 characters are A-Z, a-z, 0-9, '+', '/',and '='\nExpect errors in decoding.")
        }
        d = d.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        do {
            k = this.keyStr.indexOf(d.charAt(c++));
            h = this.keyStr.indexOf(d.charAt(c++));
            f = this.keyStr.indexOf(d.charAt(c++));
            e = this.keyStr.indexOf(d.charAt(c++));
            l = (k << 2) | (h >> 4);
            j = ((h & 15) << 4) | (f >> 2);
            g = ((f & 3) << 6) | e;
            b = b + String.fromCharCode(l);
            if (f != 64) {
                b = b + String.fromCharCode(j)
            }
            if (e != 64) {
                b = b + String.fromCharCode(g)
            }
            l = j = g = "";
            k = h = f = e = ""
        } while (c < d.length);
        return unescape(b)
    }
};

function base64_decode(h) {
    var d = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var c, b, a, m, l, k, j, n, g = 0,
        o = 0,
        e = "",
        f = [];
    if (!h) {
        return h
    }
    h += "";
    do {
        m = d.indexOf(h.charAt(g++));
        l = d.indexOf(h.charAt(g++));
        k = d.indexOf(h.charAt(g++));
        j = d.indexOf(h.charAt(g++));
        n = m << 18 | l << 12 | k << 6 | j;
        c = n >> 16 & 255;
        b = n >> 8 & 255;
        a = n & 255;
        if (k == 64) {
            f[o++] = String.fromCharCode(c)
        } else {
            if (j == 64) {
                f[o++] = String.fromCharCode(c, b)
            } else {
                f[o++] = String.fromCharCode(c, b, a)
            }
        }
    } while (g < h.length);
    e = f.join("");
    return e
}

function base64_encode(j) {
    var e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var d, c, b, n, m, l, k, o, h = 0,
        p = 0,
        g = "",
        f = [];
    if (!j) {
        return j
    }
    do {
        d = j.charCodeAt(h++);
        c = j.charCodeAt(h++);
        b = j.charCodeAt(h++);
        o = d << 16 | c << 8 | b;
        n = o >> 18 & 63;
        m = o >> 12 & 63;
        l = o >> 6 & 63;
        k = o & 63;
        f[p++] = e.charAt(n) + e.charAt(m) + e.charAt(l) + e.charAt(k)
    } while (h < j.length);
    g = f.join("");
    var a = j.length % 3;
    return (a ? g.slice(0, a - 3) : g) + "===".slice(a || 3)
};
SD.projection.Default = function() {};
SD.projection.Default.prototype = {
    geoToMetric: function(b, a) {
        return {
            x: 0,
            y: 0
        }
    },
    metricToGeo: function(a, b) {
        return {
            x: 0,
            y: 0
        }
    },
    geoToScreen: function(e, c, d, a) {
        var b = this.geoToPixel(e, c, d);
        b.x -= a.x;
        b.y -= a.y;
        return b
    },
    screenToGeo: function(a, e, d, c) {
        var b = this.pixelToGeo(a + c.x, e + c.y, d);
        return b
    },
    metricToScreen: function(a, e, d, b) {
        var c = this.metricToPixel(a, e, d);
        c.x -= b.x;
        c.y -= b.y;
        return c
    },
    screenToMetric: function(a, e, d, c) {
        var b = this.pixelToMetric(a + c.x, e + c.y, d);
        return b
    },
    geoToPixel: function(d, b, c) {
        var a = this.geoToMetric(d, b);
        return this.metricToPixel(a.x, a.y, c)
    },
    pixelToGeo: function(b, d, c) {
        var a = this.pixelToMetric(b, d, c);
        return this.metricToGeo(a.x, a.y)
    },
    inflateGeo: function(c, a, e, d) {
        var b = this.geoToPixel(c.lon, c.lat, d);
        b = SD.util.offsetPoint(b, a, e);
        return this.pixelToGeo(b.x, b.y, d)
    },
    inflateVert: function(b, a, e, d) {
        var c = this.metricToPixel(b.x, b.y, d);
        c = SD.util.offsetPoint(c, a, e);
        return this.pixelToMetric(c.x, c.y, d)
    },
    metricToPixel: function(a, d, c) {
        var b = new Point();
        b.x = a / c;
        b.y = (d / c) * -1;
        return b
    },
    pixelToMetric: function(b, d, c) {
        var a = new Point();
        a.x = b * c;
        a.y = d * c * -1;
        return a
    }
};
SD.projection.BaseUTM = function() {
    this.a = 6378137;
    this.b = 6356752.3142;
    this.k0 = 0.9996;
    this.tZone = -1;
    this.tIsSouth = false
};
SD.projection.BaseUTM.prototype = {
    geoToMetric: function(o, r, d) {
        var u = (this.a - this.b) / (this.a + this.b);
        var v = Math.PI / (180 * 60 * 60);
        var z = Math.sqrt(1 - Math.pow(this.b / this.a, 2));
        var c = Math.pow(z, 2) / (1 - Math.pow(z, 2));
        r = r * Math.PI / 180;
        var C = this.a / Math.sqrt(1 - Math.pow(z * Math.sin(r), 2));
        if (!d) {
            d = 31 + parseInt((Math.floor(o / 6)));
            this.tZone = d
        }
        var a = parseInt((6 * d) - 183);
        var b = (o - a);
        var t = b * 3600 / 10000;
        var q = this.a * (1 - u + (5 / 4) * Math.pow(u, 2) * (1 - u) + (81 / 64) * Math.pow(u, 4) * (1 - u));
        var A = (3 * this.a * u / 2) * (1 - u - (7 / 8) * Math.pow(u, 2) * (1 - u) + (55 / 64) * Math.pow(u, 4));
        var f = (15 * this.a * Math.pow(u, 2) / 16) * (1 - u + (3 / 4) * Math.pow(u, 2) * (1 - u));
        var s = (35 * this.a * Math.pow(u, 3) / 48) * (1 - u + (11 / 16) * Math.pow(u, 2));
        var B = (315 * this.a * Math.pow(u, 4) / 51) * (1 - u);
        var w = (q * r) - (A * Math.sin(2 * r)) + (f * Math.sin(4 * r)) - (s * Math.sin(6 * r)) + (B * Math.sin(8 * r));
        var m = w * this.k0;
        var l = this.k0 * (100000000) * Math.pow(v, 2) * C * Math.sin(r) * Math.cos(r) / 2;
        var k = (this.k0 * (10000000000000000) * Math.pow(v, 4) * C * Math.sin(r) * Math.pow(Math.sin(r), 3) / 24) * ((5 - Math.pow(Math.tan(r), 2) + 9 * c * Math.pow(Math.cos(r), 2) + 4 * Math.pow(c, 2) * Math.pow(Math.cos(r), 4)));
        var i = this.k0 * 10000 * v * C * Math.cos(r);
        var g = (this.k0 * (1000000000000) * Math.pow(v, 3) * C * Math.pow(Math.cos(r), 3) / 6) * (1 - Math.pow(Math.tan(r), 2) + c * Math.pow(Math.cos(r), 2));
        var D = (Math.pow(t * v, 6) * C * Math.sin(r) * Math.pow(Math.cos(r), 5) / 720) * (61 - 58 * Math.pow(Math.tan(r), 2) + Math.pow(Math.tan(r), 4) + 270 * c * Math.pow(Math.cos(r), 2) - 330 * c * Math.pow(Math.sin(r), 2)) * this.k0 * Math.pow(10, 24);
        var h = m + (l * Math.pow(t, 2)) + (k * Math.pow(t, 4)) + (D * Math.pow(t, 6));
        if (h < 0) {
            h = h + 10000000;
            this.tIsSouth = true
        }
        var j = (i * t) + (g * Math.pow(t, 3)) + 500000;
        return new Vertex(j, h)
    },
    metricToGeo: function(o, l, f, A) {
        var E = Math.sqrt(1 - Math.pow(this.b / this.a, 2));
        var d = Math.pow(E, 2) / (1 - Math.pow(E, 2));
        o = 500000 - o;
        var z = l;
        if (A) {
            l = 10000000 - l
        }
        var B = 6 * f - 183;
        var i = l / this.k0;
        var w = i / (this.a * (1 - Math.pow(E, 2) / 4 - 3 * Math.pow(E, 4) / 64 - 5 * Math.pow(E, 6) / 256));
        var n = (1 - Math.sqrt((1 - Math.pow(E, 2)))) / (1 + Math.sqrt((1 - Math.pow(E, 2))));
        var g = (3 * n / 2 - 27 * Math.pow(n, 3) / 32);
        var c = (21 * Math.pow(n, 2) / 16 - 55 * Math.pow(n, 4) / 32);
        var b = (151 * Math.pow(n, 3) / 96);
        var a = (1097 * Math.pow(n, 4) / 512);
        var h = w + g * Math.sin(2 * w) + c * Math.sin(4 * w) + b * Math.sin(6 * w) + a * Math.sin(8 * w);
        var C = d * Math.pow(Math.cos(h), 2);
        var v = Math.pow(Math.tan(h), 2);
        var F = this.a * (1 - Math.pow(E, 2)) / Math.pow((1 - Math.pow(E, 2) * Math.pow(Math.sin(h), 2)), (3 / 2));
        var s = this.a / Math.sqrt((1 - Math.pow(E * Math.sin(h), 2)));
        var u = o / (s * this.k0);
        var t = s * Math.tan(h) / F;
        var r = (Math.pow(u, 2) / 2);
        var q = (5 + 3 * v + 10 * C - 4 * Math.pow(C, 2) - 9 * d) * Math.pow(u, 4) / 24;
        var p = (61 + 90 * v + 298 * C + 45 * Math.pow(v, 2) - 3 * Math.pow(C, 2) - 252 * d) * Math.pow(u, 6) / 720;
        var m = u;
        var k = (1 + 2 * v + C) * Math.pow(u, 3) / 6;
        var j = (5 - 2 * C + 28 * v - 3 * Math.pow(C, 2) + 8 * d + 24 * Math.pow(v, 2)) * Math.pow(u, 5) / 120;
        latitude = 180 * (h - t * (r - q + p)) / Math.PI;
        if (A) {
            latitude = latitude * -1
        }
        longitude = B - ((m - k + j) / Math.cos(h)) * 180 / Math.PI;
        return new GeoPoint(longitude, latitude)
    }
};
SD.projection.UTM = function(a, b) {
    this.zone = a;
    this.isSouth = b;
    this.obj = new SD.projection.BaseUTM();
    this.name = "UTM WGS-1984 " + this.zone + (this.isSouth ? "S" : "N");
    this.geoToMetric = function(d, c) {
        return this.obj.geoToMetric(d, c, this.zone)
    };
    this.metricToGeo = function(c, d) {
        return this.obj.metricToGeo(c, d, this.zone, this.isSouth)
    }
};
SD.extend(SD.projection.UTM, SD.projection.Default);
SD.projection.Mercator = function() {
    this.rMajor = 6378137;
    this.rMinor = 6356752.3142;
    this.temp = this.rMinor / this.rMajor;
    this.M_PI_2 = Math.PI / 2;
    this.eccent = Math.sqrt(1 - (this.temp * this.temp));
    this.eccnth = 0.5 * this.eccent;
    this.name = "Mercator WGS-1984";
    this.radToDeg = function(a) {
        return a * (180 / Math.PI)
    };
    this.degToRad = function(a) {
        return a * (Math.PI / 180)
    };
    this.mercX = function(a) {
        return this.rMajor * this.degToRad(a)
    };
    this.unMercX = function(a) {
        return this.radToDeg(a) / this.rMajor
    };
    this.geoToMetric = function(a, b) {
        return new Vertex(this.mercX(a), this.mercY(b))
    };
    this.metricToGeo = function(a, b) {
        return new GeoPoint(this.unMercX(a), this.unMercY(b))
    };
    this.unMercY = function(f) {
        var e = Math.exp(-f / this.rMajor);
        var d = Math.PI / 2 - 2 * Math.atan(e);
        var c = 0;
        var b = 1;
        while (Math.abs(b) > 1e-9 && c < 15) {
            var a = this.eccent * Math.sin(d);
            b = this.M_PI_2 - 2 * Math.atan(e * Math.pow((1 - a) / (1 + a), this.eccnth)) - d;
            d += b;
            c++
        }
        return this.radToDeg(d)
    };
    this.mercY = function(f) {
        if (f > 89.5) {
            f = 89.5
        }
        if (f < -89.5) {
            f = -89.5
        }
        var e = this.degToRad(f);
        var d = Math.sin(e);
        var a = this.eccent * d;
        var b = 0.5 * this.eccent;
        a = Math.pow(((1 - a) / (1 + a)), b);
        var c = Math.tan(0.5 * ((Math.PI * 0.5) - e)) / a;
        var g = 0 - this.rMajor * Math.log(c);
        return g
    }
};
SD.extend(SD.projection.Mercator, SD.projection.Default);
SD.projection.Server = function() {
    this.list = [{
        xname: "UTM WGS-1984 48N",
        obj: new SD.projection.UTM(48, false)
    }, {
        xname: "UTM WGS-1984 47N",
        obj: new SD.projection.UTM(47, false)
    }, {
        xname: "UTM WGS-1984 48S",
        obj: new SD.projection.UTM(48, true)
    }, {
        xname: "Mercator WGS-1984",
        obj: new SD.projection.Mercator()
    }, {
        xname: "UTM WGS-1984 49S",
        obj: new SD.projection.UTM(49, true)
    }];
    this.get = function(b) {
        if (this.list.length == 0) {
            return false
        }
        for (var a = 0; a < this.list.length; a++) {
            if (escape(this.list[a].xname) == escape(b)) {
                return this.list[a].obj
            }
        }
        return false
    };
    this.defaultProjection = function() {
        return this.list[0].obj
    }
};
SD.ns("SD.preset");
SD.preset.MapRasterLayer = function(a, m, k, e, l, b, i, j, d, g, c, f) {
    this.realLevel = 0;
    this.minLongitude = 0;
    this.minLatitude = 0;
    this.maxLongitude = 0;
    this.maxLatitude = 0;
    this.mapTileWidth = 0;
    this.mapTileHeight = 0;
    this.totalMapRow = 0;
    this.totalMapCol = 0;
    this.ratio = 1;
    this.cache = null;
    this.zoomTiles = null;
    this.managerInterval = null;
    this.totalTileLoaded = 0;
    this.gridSystem = false;
    this.projection = f;
    this.drawExpand = c;
    this.bounds = null;
    this.boundsPolyline = [];
    this.initialize(a, m, k, e, b, l, i, j, d, g)
};
SD.preset.MapRasterLayer.prototype.initialize = function(a, k, i, d, b, j, f, g, c, e) {
    this.name = a;
    this.path = k;
    this.mapTileWidth = i;
    this.mapTileHeight = d;
    this.totalMapCol = b;
    this.totalMapRow = j;
    this.minVertexLongitude = f;
    this.maxVertexLongitude = g;
    this.maxVertexLatitude = c;
    this.tileLevel = e;
    this.scale = this.scaleValue();
    this.minVertexLatitude = this.maxVertexLatitude - (this.totalMapRow * this.mapTileHeight) * this.scale;
    this.boundsMetric = new Rectangle(this.minVertexLongitude, this.maxVertexLatitude, this.maxVertexLongitude, this.minVertexLatitude);
    this.setToGeo();
    this.setToPixel()
};
SD.preset.MapRasterLayer.prototype.isInBounds0 = function(b) {
    var a = Intersection.RectangleRectangle(this.bounds, b);
    if (a.hit > 0) {
        return true
    }
    return false
};
SD.preset.MapRasterLayer.prototype.isInBounds1 = function(f, e) {
    var g = this.boundsPolyline.length;
    if (g > 0) {
        for (var d = 0; d < g; d++) {
            if (this.boundsPolyline[d] instanceof MapArea) {
                var a = this.boundsPolyline[d].isIn(f, e);
                if (a) {
                    return true
                }
            }
        }
        return false
    }
    if (this.bounds.top >= e && this.bounds.bottom <= e && this.bounds.left <= f && this.bounds.right >= f) {
        return true
    }
    return false
};
SD.preset.MapRasterLayer.prototype.isInRect = function(b, a) {
    return !(b < 1 || a < 1 || a > this.totalMapCol || b > this.totalMapRow)
};
SD.preset.MapRasterLayer.prototype.loadFromXml = function(a) {
    this.mapTileWidth = parseInt(a.getNamedItem("WIDTH").nodeValue);
    this.mapTileHeight = parseInt(a.getNamedItem("HEIGHT").nodeValue);
    this.totalMapCol = parseInt(a.getNamedItem("MAXCOL").nodeValue);
    this.totalMapRow = parseInt(a.getNamedItem("MAXROW").nodeValue);
    this.minVertexLongitude = parseFloat(a.getNamedItem("MINLONG").nodeValue);
    this.maxVertexLongitude = parseFloat(a.getNamedItem("MAXLONG").nodeValue);
    this.maxVertexLatitude = parseFloat(a.getNamedItem("MAXLAT").nodeValue);
    this.tileLevel = parseInt(a.getNamedItem("LEVELCODE").nodeValue);
    this.scale = this.scaleValue();
    this.minVertexLatitude = this.maxVertexLatitude - (this.totalMapRow * this.mapTileHeight) * this.scale
};
SD.preset.MapRasterLayer.prototype.scaleValue = function() {
    return ((this.maxVertexLongitude - this.minVertexLongitude) / (this.totalMapCol * this.mapTileWidth))
};
SD.preset.MapRasterLayer.prototype.setToGeo = function() {
    if (this.projection != null) {
        var b = this.projection.metricToGeo(this.maxVertexLongitude, this.minVertexLatitude);
        var a = this.projection.metricToGeo(this.minVertexLongitude, this.maxVertexLatitude);
        this.maxLongitude = b.lon;
        this.maxLatitude = a.lat;
        this.minLongitude = a.lon;
        this.minLatitude = b.lat;
        this.bounds = new Rectangle(this.minLongitude, this.maxLatitude, this.maxLongitude, this.minLatitude)
    }
};
SD.preset.MapRasterLayer.prototype.setToPixel = function() {
    if (this.projection != null) {
        var b = this.projection.metricToPixel(this.maxVertexLongitude, this.minVertexLatitude, this.scale);
        var a = this.projection.metricToPixel(this.minVertexLongitude, this.maxVertexLatitude, this.scale);
        this.maxPixelLongitude = b.x;
        this.maxPixelLatitude = a.y;
        this.minPixelLongitude = a.x;
        this.minPixelLatitude = b.y;
        this.boundsPixel = new Rectangle(this.minPixelLongitude, this.maxPixelLatitude, this.maxPixelLongitude, this.minPixelLatitude)
    }
};
SD.preset.MapRasterLayer.prototype.getRowCol = function(a, b) {
    return {
        col: Math.ceil((a - this.minPixelLongitude) / this.mapTileWidth),
        row: Math.ceil((b - this.maxPixelLatitude) / this.mapTileHeight)
    }
};
SD.preset.MapRasterLayer.prototype.createList = function(g, d, b, f) {
    var e = new SD.preset.MapRowCols();
    for (var c = g; c <= b; c++) {
        for (var a = d; a <= f; a++) {
            if (!this.drawExpand && !this.isInRect(a, c)) {
                continue
            }
            e.add({
                row: a,
                col: c,
                img: null,
                code: this.name,
                level: this.realLevel,
                div: null,
                top: 0,
                left: 0
            })
        }
    }
    return e
};
SD.preset.MapRasterLayer.prototype.getTileUrl = function(j, f) {
    var h = "http://";
    if (SD.MAP_PRE != null) {
        h += SD.MAP_PRE + (1 + (j + f) % 4) + "."
    }
    h += SD.MAP_URL;
    h = h + this.path + ("/");
    h = h + this.tileLevel;
    if (this.gridSystem) {
        var a = {
            row: 0,
            col: 0
        };
        var k = (this.totalMapRow / this.gridSystem.row);
        var e = (this.totalMapCol / this.gridSystem.col);
        for (var b = this.gridSystem.row; b >= 1; b--) {
            if ((b * k) >= j) {
                a.row = b
            }
        }
        for (var i = this.gridSystem.col; i >= 1; i--) {
            if ((i * e) >= f) {
                a.col = i
            }
        }
        var g = this.name == "ph" ? "" : this.name + "_";
        h += ("/" + a.row + "_" + a.col + "/" + g + this.tileLevel + "_" + a.row + "_" + a.col + "_" + j + "_" + f + ".gif?v=" + SD.MAP_VERSION)
    } else {
        if (this.name == "asia") {
            h = h + "/sg"
        } else {
            if (this.name == "minimap") {
                h = h + "/wrd"
            } else {
                if (this.name == "bali") {
                    h = h + "/bl"
                } else {
                    h = h + ("/" + escape(this.name))
                }
            }
        }
        h = h + j + "_" + f + "_" + this.tileLevel + ".gif?v=" + SD.MAP_VERSION
    }
    return h
};
SD.preset.MapRasterLayer.prototype.getTileId = function(b, a) {
    return this.name + "_" + b + "_" + a + "_" + this.tileLevel
};
SD.preset.MapRasterLayer.prototype.setTile = function(a, d, b) {
    var c = this.getTileUrl(d, b);
    a.style.display = "none";
    a.src = c;
    a.onload = function() {
        this.style.display = ""
    }
};
SD.preset.MapRasterLayer.prototype.createTile = function(d, b) {
    var c = this.getTileUrl(d, b);
    var a = document.createElement("img");
    a.style.display = "none";
    a.src = c;
    a.onload = function() {
        this.style.display = ""
    };
    return a
};
SD.preset.MapRasterLayer.prototype.getBoundRow = function(a) {
    if (this.ratio == 1 && this.drawExpand && (a < 1 || a > this.totalMapRow)) {
        a = 1
    }
    return a
};
SD.preset.MapRasterLayer.prototype.getBoundCol = function(a) {
    if (this.totalMapCol == 1) {
        return 1
    }
    if (this.ratio == 1 && this.drawExpand) {
        if (a <= -(this.totalMapCol) || a > (this.totalMapCol * 2)) {
            a = a % this.totalMapCol
        }
        a = a < 0 ? this.totalMapCol + a : (a > this.totalMapCol ? a - this.totalMapCol : (a == 0 || this.totalMapCol == 1 ? this.totalMapCol : a))
    }
    return a
};
SD.preset.MapRasterLayerRatio = function(b, a) {
    SD.apply(this, b);
    this.mapTileWidth *= a;
    this.mapTileHeight *= a;
    this.initialize(this.name, this.path, this.mapTileWidth, this.mapTileHeight, this.totalMapCol, this.totalMapRow, this.minVertexLongitude, this.maxVertexLongitude, this.maxVertexLatitude, this.tileLevel, this.realLevel)
};

function MapRasterMini(c, b, a) {
    SD.apply(this, c);
    this.min = b;
    this.max = a
}
SD.preset.MapRowCols = function() {
    this.node = [];
    this.max = 50
};
SD.preset.MapRowCols.prototype.add = function(a) {
    this.node.push(a)
};
SD.preset.MapRowCols.prototype.addNode = function(e, c, b, d) {
    var a = {
        row: e,
        col: c,
        img: null,
        code: b,
        level: d,
        top: 0,
        left: 0
    };
    this.node.push(a);
    return a
};
SD.preset.MapRowCols.prototype.getNodeByLevel = function(f) {
    var b = [],
        a = 0;
    for (var d = 0, e = this.node.length; d < e; d++) {
        if (this.node[d].level == f) {
            b[a] = this.node[d];
            a++
        }
    }
    return b
};
SD.preset.MapRowCols.prototype.getNodes = function(e, g) {
    var b = [],
        a = 0;
    for (var d = 0, f = this.node.length; d < f; d++) {
        if (this.node[d].level == g && this.node[d].code == e) {
            b[a] = this.node[d];
            a++
        }
    }
    return b
};
SD.preset.MapRowCols.prototype.getSumLoadedNodes = function(a) {
    var d = 0;
    for (var b = 0, e = a.length; b < e; b++) {
        if (a[b].img != undefined && (!a[b].img.complete || (typeof a[b].img.naturalWidth != "undefined" && a[b].img.naturalWidth == 0))) {
            continue
        }
        d++
    }
    return d
};
SD.preset.MapRowCols.prototype.clear = function() {
    for (var a = 0, b = this.node.length; a < b; a++) {
        if (this.node[a].img) {
            SD.util.purge(this.node[a].img);
            this.node[a].img = undefined
        }
        this.node[a] = undefined
    }
    this.node = []
};
SD.preset.MapRowCols.prototype.remove = function(b) {
    var a = -1;
    for (var d = 0, e = this.node.length; d < e; d++) {
        if (this.node[d] == b) {
            a = d;
            break
        }
    }
    if (a != -1) {
        this.node.splice(a, 1)
    }
};
SD.preset.MapRowCols.prototype.getMap = function(b, f, e, d) {
    for (var a = 0, g = this.node.length; a < g; a++) {
        if (this.node[a].row == b && this.node[a].col == f && this.node[a].level == d && this.node[a].code == e) {
            return this.node[a]
        }
    }
    return false
};
SD.preset.MapRowCols.prototype.unReloadImg = function() {
    for (var b = 0; b < this.node.length; b++) {
        var a = this.node[b];
        if (a.img != null) {
            a.img.removeAttribute("src")
        }
    }
};
SD.preset.MapRowCols.prototype.getBounds = function(a) {
    var d = new Rectangle(0, 0, 0, 0);
    if (a == undefined) {
        a = this.node
    }
    for (var b = 0, e = a.length; b < e; b++) {
        if (b == 0) {
            d.left = a[b].col;
            d.right = a[b].col;
            d.top = a[b].row;
            d.bottom = a[b].row
        }
        if (a[b].col > d.right) {
            d.right = a[b].col
        }
        if (a[b].col < d.left) {
            d.left = a[b].col
        }
        if (a[b].row < d.top) {
            d.top = a[b].row
        }
        if (a[b].row > d.bottom) {
            d.bottom = a[b].row
        }
    }
    return d
};
SD.preset.MapRowCols.prototype.getIntersectionRect = function(a, c) {
    var d = [];
    for (var b = c.left; b <= c.right; b++) {
        for (var e = c.top; e <= c.bottom; e++) {
            if (a.right < b || a.left > b || a.top > e || a.bottom < e) {
                d.push({
                    row: e,
                    col: b
                })
            }
        }
    }
    return d
};
SD.preset.MapRowCols.prototype.removeFromLayer = function(b) {
    for (var a = 0, d = this.removed.length; a < d; a++) {
        b.removeChild(this.removed[a]);
        this.removed[a] = null
    }
    this.removed = []
};
SD.mgr.Preset = function() {
    this.layers = [];
    this.initConfigDefault();
    this.filterLayers();
    this.initAreaDefault()
};
SD.mgr.Preset.prototype.getLength = function() {
    return this.layers.length
};
SD.mgr.Preset.prototype.filterLayers = function() {
    var d;
    for (var b = 0, e = this.layers.length; b < e; b++) {
        d = this.layers[b];
        if (d.length != undefined) {
            for (var a = 0; a < d.length; a++) {
                if (!(d[a].boundsPolyline instanceof Array)) {
                    d[a].boundsPolyline = new Array()
                }
            }
        } else {
            if (typeof d == "object") {
                if (!(d.boundsPolyline instanceof Array)) {
                    d.boundsPolyline = []
                }
            }
        }
    }
};
SD.mgr.Preset.prototype.addArea = function(d, e, b) {
    var a = function(k, l) {
        var h;
        for (var g = 0; g < k.length; g++) {
            h = k[g];
            if (h.length != undefined) {
                for (var f = 0; f < h.length; f++) {
                    if (l != undefined && l != h[f].realLevel) {
                        continue
                    }
                    if (h[f].name == e) {
                        h[f].boundsPolyline.push(d)
                    }
                }
            } else {
                if (typeof h == "object") {
                    if (l != undefined && l != h.realLevel) {
                        continue
                    }
                    if (h.name == e) {
                        h.boundsPolyline.push(d)
                    }
                }
            }
        }
    };
    if (b != undefined && b.length) {
        for (var c = 0; c < b.length; c++) {
            a(this.layers, b[c])
        }
    } else {
        a(this.layers)
    }
};
SD.mgr.Preset.prototype.getMapLayerByNearest = function(e, b, c, m) {
    var o, d = 0,
        l = 1000000,
        h = false,
        a = 0,
        k = b != undefined && b > 0 ? b - 1 : false;
    for (var g = 0; g < this.layers.length; g++) {
        if (k && k != g) {
            continue
        }
        o = this.layers[g];
        if (o.length != undefined) {
            for (var f = 0; f < o.length; f++) {
                if (o[f].isInBounds1(c, m)) {
                    if (parseInt(o[f].scale) == parseInt(e)) {
                        return {
                            level: g + 1,
                            layer: o[f]
                        }
                    }
                    d = Math.abs(o[f].scale - e);
                    if (d < l) {
                        h = o[f];
                        a = g + 1
                    }
                    l = d
                }
            }
        } else {
            if (typeof o == "object" && o.isInBounds1(c, m)) {
                if (parseInt(o.scale) == parseInt(e)) {
                    return {
                        level: g + 1,
                        layer: o
                    }
                }
                d = Math.abs(o.scale - e);
                if (d < l) {
                    h = o;
                    a = g + 1
                }
                l = d
            }
        }
    }
    if (typeof o == "object" && o.length == 0) {
        return {
            level: a,
            layer: o
        }
    }
    return {
        level: a,
        layer: h
    }
};
SD.mgr.Preset.prototype.getMapLayerByLevel = function(e, d, c) {
    var b = this.layers[e - 1];
    if (b != undefined) {
        if (b.length != undefined) {
            for (var a = 0; a < b.length; a++) {
                if (b[a].isInBounds1(d, c)) {
                    return b[a]
                }
            }
        } else {
            if (typeof b == "object") {
                if (b.isInBounds1(d, c)) {
                    return b
                }
            }
        }
    }
    return false
};
SD.mgr.Preset.prototype.getMapLayerByAllLevel = function(g, f) {
    var h = this.layers.length;
    var a = false;
    var d = 0;
    var c = 1;
    var e = false;
    for (var b = h; b >= 0; b--) {
        a = this.getMapLayerByLevel(b, g, f);
        if (a && a.mapTileHeight > 345) {
            continue
        }
        if (a) {
            e = a;
            return a
        }
    }
    return e
};
SD.mgr.Preset.prototype.getMapLayerByName = function(b, d) {
    var c = this.layers[d - 1];
    if (c != undefined) {
        if (c.length != undefined) {
            for (var a = 0; a < c.length; a++) {
                if (c[a].name == b) {
                    return c[a]
                }
            }
        } else {
            if (typeof c == "object") {
                if (c.name == b) {
                    return c
                }
            }
        }
    }
    return false
};
SD.mgr.Preset.prototype.addLayer = function(d, c) {
    var a = this.layers.length;
    if (d.length != undefined) {
        for (var b = 0; b < d.length; b++) {
            d[b].realLevel = a + 1
        }
    } else {
        if (typeof d == "object") {
            d.realLevel = a + 1
        }
    }
    this.layers.push(d)
};
SD.preset.Area = function(b, a) {
    this.nodes = (typeof b == "string") ? Utf8.gdecode(b) : this.formatBounds(b)
};
SD.preset.Area.prototype.formatBounds = function(d) {
    var b = [];
    for (var c = 0; c < d.length - 1; c += 2) {
        b.push({
            lon: d[c],
            lat: d[c + 1]
        })
    }
    return b
};
SD.preset.Area.prototype.isIn = function(b, g) {
    var a = 1,
        f = this.nodes.length;
    var c = f - 1;
    for (var e = 0; e < f; e++) {
        if ((this.nodes[e].lat <= g && g < this.nodes[c].lat) || (this.nodes[c].lat <= g && g < this.nodes[e].lat)) {
            var d = (this.nodes[c].lon - this.nodes[e].lon) * (g - this.nodes[e].lat) / (this.nodes[c].lat - this.nodes[e].lat) + this.nodes[e].lon;
            if (b < d) {
                a = 1 - a
            }
        }
        c = e
    }
    return a != 1 ? true : false
};
var MapRasterLayer = SD.preset.MapRasterLayer,
    MapRasterLayerRatio = SD.preset.MapRasterLayerRatio,
    MapRowCols = SD.preset.MapRowCols,
    MapManager = SD.mgr.Preset,
    MapArea = SD.preset.Area;
MapManager.prototype.initAreaDefault = function() {
    this.addArea(new MapArea("mkrxR_u_HwfFfiAacEfqDomEfiAyrBu\\c`Enq@azEqFerHgpCemHjeEt}AxkKbkFjrJ|hj@`mTtii@|A~YasTulE}sKqmHmfNmjGalC{aFtaAecIo~D"), "sg", [11, 12, 13]);
    this.addArea(new MapArea("avqlRoceQDxbADvbAjbAElbAEjbAClbAEDvbAmbADDvbAjbACDvbADvbAjbAClbAEBvbADxbADvbAmbADkbABBxbADvbADvbABxbADvbAmbADDvbAkbADBvbADvbABxbADvbAkbABBxbAlbAEjbACEybACwbAEwbACybAjbACjbAElbACjbAEDvbAjbACDvbABxbADvbABvbAlbACBvbADxbAjbAEBxbADvbAjbAClbAEjbACCybAEwbAlbAEEwbACybAjbACCwbAjbAECwbAEybAlbACCybAjbACCybAjbAClbAEEwbAkbABmbADkbABEwbACybAjbACCybAjbACCybAEwbAlbAECwbAjbAECwbAjbAECwbAEybAlbACCybAEwbAlbAEEwbACybAjbAClbAElbAClbAEBxbAlbAElbACEybAlbACDvbAjbAClbACDvbAjbAClbAECwbAEybACybAlbAClbAClbAEjbAClbAEDxbAlbACjbAElbAClbACDxbABvbAlbACBxbABvbADxbABxbAlbAClbAEjbAClbAClbACBxbAlbAElbAClbACCybACybAmbADCybACybAmbABEybACwbAmbABCybACybAmbADEybAmbABCybAmbADmbABCybAmbADCybAEybACybAmbADCybAmbABmbADEybACwbAlbAElbACEybAmbABCwbACybAmbABmbADmbABobADmbABmbADkbABBxbABxbAkbABmbADEybAmbADmbABCybAmbADmbADEybACybAEwbAEybACwbAEybAmbADCybAEwbAlbAEEybACwbAEybAEybAmbADmbADmbADmbABmbADmbADmbADmbABDxbAmbADEybAmbADEybAmbADCwbAEybAmbADEwbAmbADmbABmbADmbADmbADmbADDvbADxbAmbADEybAEwbAmbADDvbAmbADmbADDxbADvbADvbAmbADmbADkbADDxbADvbABvbADxbAlbAEDvbADvbAmbADDxbAmbADDvbAmbADDvbAlbAEDxbAlbAEDvbAjbAEDxbAmbABkbADmbADDxbAlbAEBvbAkbADDvbAmbADDvbADxbAjbAEDvbADxbAmbABDxbADvbAmbADkbADBvbADvbA"), "kv", [11, 12, 13]);
    this.addArea(new MapArea("yachStk|c@zRd{@_BniG}_C~lEodBtfAm[bbApf@bqDnuBtmEc|BleArLngEkz@|cDgKzvD__AfeCku@hv@kwArDor@vrGopBbeC~~A||EvgCvA~nArcAmNxjM{rB|vBdOzmBukAhgLq|@tsAc}E``Ck`EaI}jAb_D|mE`aEsp@fi@awDfJcmAxaBgu@sHcb@{eAn`@aqCdgB{pCdFi[{~Esz@cwFvrC`lCpjCoMnrBcuB`i@sqH_@cH_{A~XuJfxCrMyfEi|DmqEduCgpB~@}m@o|@zfDw}BqgHclD}lA`b@}gAkg@gYvlApd@|k@wb@vtBfk@~nC`Tni@}d@lw@c~FpjBi[CmzAweCsZu{DqfHffEcbGcpA_vAkaAyzCrt@izAciDkmDiWzA_cCb{E}oEraHcwCqmG}vCcgFxcGivF{s@eoJhrAgsIluDkaD{oAm_E{eExn@glC|mDkoBtfAs~Ea~Bks@diAmkGugDu_FugC}AhwAsfGmbCwpBlR}iCfvA{SscBw_Dsd@}Jr[kqAr[ulAsf@cbBioDkyAynAiaAcw@iiBkEqsCl[_n@gqAcl@|eA_|@ikByA{ZuxAhYgdBh_AcfD_|@wp@cOqqAleGupF~nAtAtnCmE|mDqwCdtFopAp_FqmE~_BeyBnn@{aBkyA{zJ~dPkfDhhGntCpeBbaUjge@baAnpGqoLdgbAdiAz{BdeI"), "jkt", [11, 12, 13]);
    this.addArea(new MapArea("ctq{YbjlKbzBdteYqGhgFcXdsCZ~OxfCd_RdpCzfMziKzbQdRxvCutDlqMcpB~zKizEbrFc`C`wE_Zbm@uiDz~rGfaB~h~GpeppAwvZhfgVnx{Jtpcy@ed|Hjd~eAwfdRvwbo@mvf{@`lrAe}qMei_CwciCg~wZgkz@qjaAg`Nq`SjyGwpN_pB_eB}HggBngMq}Di}QeyB_ca@yhCwqEooB~@}mClzD_uCgaBadFdO_`FrqGwbClqPeo[fyH{n^tzJ}bO_wI{bOtiM_wIru_@erSufAidFlyD}xQaj@}_C|iM?tqOhMlmYrgEb_LrsJxqBhyD~qOqiMnwIieJl~TwrUcia@izWqmLihe@g{J}bOpiKiyD|uPgpKyqBydHhpIqrD{gFkdHm{ImaI{|CxxBkrD_j@gvE}tAyvGugEilHqsJwmGszBqv@yb@mx@ayC{tGmqA}mAroAw|CjD}_Ige@mp@}z@iwAwruCubkAqbeKn`|JmmyIsnr@aen]k}rZm|yOousO_c|k@cauw@gcyEpp{C_|fRr`fq@g~xCh|kWy`yDfkmUe}_KtaoMqjfKditFe{`WdgnGwbo_@tq}I"), "wrd", [5, 6, 7, 8, 9, 10, 11, 12, 13]);
    this.addArea(new MapArea("axplT{eaoC}kjS??vkxK|kjS??wkxK"), "wrd", [5, 6, 7, 8, 9, 10]);
    this.addArea(new MapArea("guvuTccciCmw|B??|p|Alw|B??}p|A"), "wrd", [11, 12, 13]);
    this.addArea(new MapArea("{np}Qx|`x@eno[}qmAsvrgA~~fQcbpaA{}zCgu`l@kjoC}t{r@}oqBypewAjiuoA|h~a@fjchCzkymEudg^|evxAo`j^dihTi_a}C"), "wrd", [5, 6]);
    this.addArea(new MapArea("hejeAow_kHai{j@prFs`yNtq{@meHaqx@ttsA}xsBefy@ybWiarCqeiAmffLgzbBkymDcqlDa`fDwqiDxzBo}ty@vq~i@mnEjdoI|slIdqtd@op@bu`AvywcAmrtD?"), "wrd", [5, 6, 7]);
    this.addArea(new MapArea("{~{rPq_g}BgqBbqte@_ppKnavDxdk@xvqh@fdqF?zv_oAm`uTvabAladChsR~cuAlxbKpwrEzxc{@~gEkeAs`izAgvoB_qqDcdBeuHw}L_yRqrQiuG{fhA|bCibCyy_Ac~nLc~_@xhbAyaaE`uC{gq@b~a@|iLfn]}iLr__@{h^rk{BkpkDjrBaugAyrkCgnyCwkv@or\\gmhC`is@emlD_fsAkwq@kpfBi|hE_teF_zlAmaf@}uYkvaAcm~Bk_aCzsBukuBueDuaKmjb@qt_@{azBqwq@bpaCeqn@zibCmvhC``p@qyaF_uAgaJgxb@iwu@ehIkqAc~zAcfQks|Gxq`@o`jKuilDeySnGsrHfmDcmYj`qCoh|@vwUaj}Afz_Aju~@~scAmxwAfpqC_|Q|}p@efAzis@h{Efc[ba]|r\\lzWzsDjwY_cNr{h@wnc@jjZlrEi|q@taaCuvQpzx@oxNjly@whzDx~aAsyoEpbcCg`r@p{q@k|d@yqiAmo^_cGc|qBb{ZstQ|`m@yc_AxaWin_CpjgAgc`AzgkAosbAesVmwa@vfFgpQxxLspL`ax@gqpAbnf@gk{AlaHseGbcHoghCxmaBcyu@ooE{mnA~|KyjVyeDsuaAz}_@cruEroGra[a`Cgq]meIgt{Awi^uoh@t~Ws_DdgXuuDrrMjfR|pkAelKtqJmjYjjFlbFiuNuxJ{cb@i_p@cis@kwRsuFt}CgeMadHc}Jy_g@kv[apd@qlEesL_aUosYe~BqpiArpMkaEprGtx@fgTgu{@qi@enn@bsI{kJzrL{}Rvl@a{Pe}OwfF_yDacPqmBao`AhbZe{AvdLsLtwR_faE}rZt`AslWg`C_yOw{tBga}Aak~@g`T}fzCmucB{ls@yeJuzjC|rPkteCufl@oh[jhF}_[v}XghZbsg@c}Sftx@qhcBxboAulf@|jSisRzy~@`vgBd`_Aom`ApehBn_b@eoDvorBedn@~jrCbjxAhgu@fkc@p`^|tIfqUcq@krC`xqB~|yAd`bF`ykBlfkEhaEdqB`~|@m|PdehA`po@boI~fuBnvc@d|_DldUxq`@jvN`qQzsQdiFbtk@imLxqKtkFis@`i_BqmJ~he@fvMpvI|m_@cjXfzAacBfcKi~NtbG|nGtrQdfUqi_@lzwB"), "wrd", [5, 6, 7, 8, 9, 10])
};
MapManager.prototype.initConfigDefault = function() {
    var i = new SD.projection.Server();
    var b = new SD.projection.Mercator();
    var a = new SD.projection.UTM(48, false);
    var t = new SD.projection.UTM(47, false);
    var A = new SD.projection.UTM(48, true);
    var y = new MapRasterLayer("wrd", "wrd", 240, 345, 2, 3, -20031716.74, 20046263.33, 18980182.4, 1, true, b);
    this.addLayer(y);
    var x = new MapRasterLayer("wrd", "wrd", 256, 256, 7, 7, -20037445.90591325, 20037507.06038871, 20145713.852879956, 2, true, b);
    this.addLayer(x);
    var v = new MapRasterLayer("wrd", "wrd", 256, 256, 14, 14, -20037445.90591325, 20037507.06038871, 20145713.852879956, 3, true, b);
    this.addLayer(v);
    var u = new MapRasterLayer("wrd", "wrd", 256, 256, 21, 21, -20037445.90591325, 20037507.06038871, 20145713.852879956, 4, true, b);
    this.addLayer(u);
    var s = new MapRasterLayer("wrd", "wrd", 256, 256, 216, 216, -20235643.082, 20401182.518, 19547260.685, 5, true, b);
    s.gridSystem = {
        row: 1,
        col: 1
    };
    this.addLayer(s);
    var r = new MapRasterLayer("wrd", "wrd", 256, 256, 916, 916, -20235643.082, 20401182.518, 19547260.685, 6, true, b);
    r.gridSystem = {
        row: 2,
        col: 2
    };
    this.addLayer(r);
    var q = new MapRasterLayer("wrd", "wrd", 256, 256, 2200, 2200, -20235643.082, 20401182.518, 19547260.685, 7, false, b);
    q.gridSystem = {
        row: 4,
        col: 4
    };
    this.addLayer(q);
    var p = new MapRasterLayer("wrd", "wrd", 256, 256, 4800, 5400, -20225000, 24045668.4691916, 19510000, 8, false, b);
    p.gridSystem = {
        row: 8,
        col: 9
    };
    this.addLayer(p);
    var o = new MapRasterLayer("wrd", "wrd", 256, 256, 10500, 11200, -20225000, 20528561.4921523, 19061500, 9, false, b);
    o.gridSystem = {
        row: 15,
        col: 16
    };
    this.addLayer(o);
    var l = new MapRasterLayer("wrd", "wrd", 256, 256, 23800, 25200, -20225000, 20442459.8902404, 19061500, 10, false, b);
    l.gridSystem = {
        row: 34,
        col: 36
    };
    this.addLayer(l);
    var n = new MapRasterLayer("sg", "sg", 256, 256, 32, 56, 345342.104029, 398542.106215, 162993.174954, 8, false, a);
    var e = new MapRasterLayer("kv", "my/kv", 250, 250, 104, 106, 752180.49, 815780.49, 362251.98, 8, false, t);
    var g = new MapRasterLayer("jkt", "id/jkt", 256, 256, 155, 165, 640000, 758272, 9351104, 8, false, A);
    var k = new MapRasterLayer("wrd", "wrd", 256, 256, 53200, 56700, -20215700, 20426860, 18010900, 11, false, b);
    k.gridSystem = {
        row: 152,
        col: 162
    };
    this.addLayer([n, e, g, k]);
    var m = new MapRasterLayer("sg", "sg", 256, 256, 64, 112, 345342.104029, 398542.106215, 162993.174954, 9, false, a);
    var c = new MapRasterLayer("kv", "my/kv", 250, 250, 208, 212, 752180.49, 815780.49, 362251.98, 9, false, t);
    var f = new MapRasterLayer("jkt", "id/jkt", 256, 256, 310, 330, 640000, 758272, 9351104, 9, false, A);
    var j = new MapRasterLayer("wrd", "wrd", 256, 256, 106400, 113400, -20215700, 20426860, 18010900, 12, false, b);
    j.gridSystem = {
        row: 304,
        col: 324
    };
    this.addLayer([m, c, f, j]);
    var w = new MapRasterLayer("sg", "sg", 256, 256, 128, 224, 345342.104029, 398542.106215, 162993.174954, 10, false, a);
    var z = new MapRasterLayer("kv", "my/kv", 250, 250, 416, 424, 752180.49, 815780.49, 362251.98, 10, false, t);
    var d = new MapRasterLayer("jkt", "id/jkt", 256, 256, 620, 660, 640000, 758272, 9351104, 10, false, A);
    var h = new MapRasterLayer("wrd", "wrd", 256, 256, 212800, 226800, -20215700, 20426860, 18010900, 13, false, b);
    h.gridSystem = {
        row: 608,
        col: 648
    };
    this.addLayer([w, z, d, h])
};

function DrawingModelCollection() {
    this.node = [];
    this.add = function(a) {
        this.node.push(a)
    };
    this.remove = function(b) {
        var a = -1;
        for (var c = 0; c < this.node.length; c++) {
            if (this.node[c] == b) {
                a = c;
                break
            }
        }
        if (a != -1) {
            this.node.splice(a, 1)
        }
    };
    this.refresh = function(b) {
        for (var a = 0; a < this.node.length; a++) {
            this.node[a].init(b, a);
            this.node[a].hit(b)
        }
    };
    this.setDisplay = function(a) {
        for (var b = 0; b < this.node.length; b++) {
            this.node[b].setDisplay(a)
        }
    };
    this.panCenter = function(c, d, b) {
        for (var a = 0; a < this.node.length; a++) {
            this.node[a].init(c, a);
            this.node[a].panCenter(c, d, b)
        }
    }
}
SD.ns("SD.pantool");
SD.pantool.Drawing = function() {
    this._callback = [];
    this.Callback = function(d, c, a) {
        for (var b = 0; b < this._callback.length; b++) {
            if (this._callback[b][d]) {
                this._callback[b][d](c, a)
            }
        }
    };
    this.getDistance = function(e, c) {
        var f = e.x - c.x;
        var d = e.y - c.y;
        return Math.sqrt(f * f + d * d)
    };
    this.SetCallback = function(a) {
        this._callback.push(a)
    };
    this.getPos = function(b, a) {
        return SD.util.getCursorPos(b, a.viewportInfo.div)
    };
    this.getOffset = function(b, a) {
        var c = this.getPos(b, a);
        return new Point(-(c.x - a.viewportInfo.canvasSize.width / 2), -(c.y - a.viewportInfo.canvasSize.height / 2))
    };
    this.getOffsetPt = function(d, a, b, c) {
        if (b) {
            c.temp.tmpPos.x = d.x;
            c.temp.tmpPos.y = d.y
        }
        c.temp.pos.x = d.x;
        c.temp.pos.y = d.y;
        return new Point(-(d.x - a.viewportInfo.canvasSize.width / 2), -(d.y - a.viewportInfo.canvasSize.height / 2))
    };
    this.isNeedReload = function(d, b, c) {
        var a = Math.abs(b.x - d.x);
        var g = Math.abs(b.y - d.y);
        var f = c.width - c.width / 4;
        var e = c.height - c.height / 4;
        if (a >= f || g >= e) {
            return true
        }
        return false
    };
    this.fixE = function(a) {
        return SD.fixE(a)
    }
};
SD.pantool.Drawing.prototype = {
    MouseUp: function(b, a) {},
    MouseDown: function(b, a) {},
    MouseMove: function(b, a) {},
    MouseWheel: function(b, a) {},
    MouseDblClick: function(b, a) {}
};
SD.pantool.Draggable = function() {
    var d = null;
    var b = false;
    var a = null;
    var c = null;
    var e = {};
    this.name = "drag tool";
    SD.apply(this, new SD.pantool.Drawing());
    this.init = function(i, g, f) {
        d = i;
        e = f;
        c = g.ActiveTool();
        var h = this;
        EventManager.add(d, "mousedown", function(j) {
            g.ActiveTool(h)
        });
        EventManager.add(d, "dblclick", function(j) {
            g.ActiveTool(c)
        })
    };
    this.MouseDown = function(g, f) {
        if (SD.util.getMouseButton(g) == "LEFT") {
            b = true
        }
        return false
    };
    this.MouseMove = function(g, f) {
        if (SD.util.getMouseButton(g) == "LEFT" && b) {
            d.setOffset(f.viewportInfo.lastCursorPosOffset, f.viewportInfo.scale);
            if (e != null && e.MouseMove != undefined) {
                e.MouseMove(g, f)
            }
            clearInterval(a);
            var h = SD.util.isNearBoundary(d.getPtPosition(), f.viewportInfo.canvasSize, f.canvasInfo.topLeftContainer);
            if (h) {
                a = setInterval(function() {
                    d.setOffset({
                        x: -h.x,
                        y: -h.y
                    }, f.viewportInfo.scale);
                    f.moveByOffset({
                        x: h.x,
                        y: h.y
                    }, true);
                    f.update()
                }, 10)
            }
        }
        g.returnValue = false
    };
    this.MouseUp = function(i, f) {
        var h = f.viewportInfo.lastCursorPosDown;
        var g = f.viewportInfo.lastCursorPosUp;
        var j = g.x == h.x && g.y == h.y ? true : false;
        if (b && !j) {
            d.updatePosition(f.canvasInfo);
            if (e != null && e.MouseUp != undefined) {
                e.MouseUp(i, f)
            }
            f.ActiveTool(f.defaultTool)
        }
        clearInterval(a);
        a = null;
        b = false;
        return false
    }
};
SD.pantool.Viewport = function() {
    this.limitedPanning = true;
    var d = false;
    var i = false;
    var j;
    var f = new Timer();
    var a = false;
    var b = false;
    var h = null;
    var e = {
        x: null,
        y: null
    };
    var g = {
        x: null,
        y: null
    };
    this.animateZoom = new SD.pantool.SimpleAnimateZoom();
    SD.apply(this, new SD.pantool.Drawing());
    setInterval(function() {
        c()
    }, 150);
    var c = function() {
        if (a) {
            a = false;
            if (h != null) {
                h.update();
                if (h.getCompletedPercentage() == 100) {
                    h.zoomLayer.clear()
                }
            }
        }
    };
    this.setPreventPanning = function(k) {
        i = k
    };
    this.getPreventPanning = function() {
        return i
    };
    this.MouseClick = function(l, k) {
        var m = "url('" + SD.BASE_URL + "img/openhand.cur'), default";
        k.fakeDiv.style.cursor = m
    };
    this.MouseDown = function(l, k) {
        if (SD.util.getMouseButton(l) == "LEFT") {
            d = true;
            var m = "url('" + SD.BASE_URL + "img/closedhand.cur'), default";
            k.fakeDiv.style.cursor = m
        }
        h = k;
        this.Callback("MouseDown", l, k);
        return false
    };
    this.MouseMove = function(l, k) {
        this.Callback("MouseMove", l, k);
        if (!d || i) {
            return
        }
        if (SD.util.getMouseButton(l) == "LEFT" && d) {
            k.moveViewport();
            a = true;
            b = true
        } else {
            var m = "url('" + SD.BASE_URL + "img/openhand.cur'), default";
            k.fakeDiv.style.cursor = m
        }
        l.returnValue = false
    };
    this.MouseUp = function(k, n) {
        var o = SD.util.getMouseButton(k);
        var m = n.viewportInfo.lastCursorPosDown;
        var q = n.viewportInfo.lastCursorPosUp;
        var r = q.x == m.x && q.y == m.y ? true : false;
        var t = "url('" + SD.BASE_URL + "img/openhand.cur'), default";
        n.fakeDiv.style.cursor = t;
        this.Callback("MouseUp", k, n);
        if (d && !r) {
            n.OnEndDrag.triggered(n.canvasInfo)
        }
        if (r) {
            var l = new Date().getTime();
            var p = j || l + 1;
            var s = l - p;
            if (s < 500 && s > 1 && q.x == this._lastCursorPosUp.x && q.y == this._lastCursorPosUp.y && m.x == this._lastCursorPosDown.x && m.y == this._lastCursorPosDown.y) {
                n.viewportInfo.lastCursorWheel = n.viewportInfo.lastCursorLatLon;
                n.viewportInfo.lastCursorDelta = o == "LEFT" ? 1 : -1;
                if (k.type.match(/mouseup/gi)) {
                    this.animateZoom.go({
                        viewport: n,
                        step: 2
                    });
                    n.OnDoubleClick.triggered(n.viewportInfo)
                }
            }
            j = l
        }
        this._lastCursorPosDown = m;
        this._lastCursorPosUp = q;
        d = false;
        return false
    };
    this.MouseWheel = function(l, k) {
        SD.util.cancelEvent(l, false);
        var m = 0,
            n = k.viewportInfo.lastCursorDelta;
        if (n) {
            if (n > 0) {
                m = k.getNextLevel(true);
                k.wheelCenter(m);
                k.zoomIn()
            } else {
                m = k.getNextLevel(false);
                k.wheelCenter(m);
                k.zoomOut()
            }
        }
        f.moreInterval = false;
        f.useTimeout = true;
        f.setTInterval(350);
        f.start({
            callback: function() {
                k.OnEndWheel.triggered(k.viewportInfo)
            }
        })
    };
    this.AnimatedMouseWheel = function(m, k) {
        var l = 3;
        this.animateZoom.go({
            viewport: k,
            step: l,
            event: m
        });
        f.moreInterval = false;
        f.useTimeout = true;
        f.setTInterval(350);
        f.start({
            callback: function() {
                k.OnEndWheel.triggered(k.viewportInfo)
            }
        })
    }
};
SD.pantool.Iphone = function() {
    var d = false;
    var f = new AnimateZoom();
    var a = false;
    var b = false;
    var h = null;
    var j = 0;
    var i = {
        x: -100,
        y: -100
    };
    var e;
    var g;
    SD.apply(this, new SD.pantool.Drawing());
    setInterval(function() {
        c()
    }, 150);
    var c = function() {
        if (a) {
            if (b) {
                b = false;
                return
            }
            a = false;
            if (h != null) {
                h.update()
            }
        }
    };
    this.MouseClick = function(l, k) {
        if (l.preventDefault) {
            l.preventDefault()
        }
        this.Callback("MouseClick", l, k);
        l.returnValue = false
    };
    this.IsAndroidGesture = function(k) {
        return SD.isAndroid && k.touches.length == 2 ? true : false
    };
    this.MouseDown = function(l, k) {
        if (l.preventDefault) {
            l.preventDefault()
        }
        var o = k.viewportInfo.lastCursorPosDown;
        k.viewportInfo.lastCursorPosMove = o;
        h = k;
        if (k.viewportInfo.lastCursorLatLon.lon == 0) {
            var n = k.viewportInfo.viewportScreenToGeo(o.x, o.y);
            k.viewportInfo.lastCursorLatLon = k.getCenterOnWorldBound(n)
        }
        var m = k.viewportInfo;
        e = l.touches.length;
        var p = m.lastCursorPosOffset.x == i.x && m.lastCursorPosOffset.y == i.y ? true : false;
        if (e == 1) {
            d = true
        }
        i = m.lastCursorPosOffset;
        this.Callback("MouseDown", l, k);
        if (this.IsAndroidGesture(l)) {
            this.GestureStart(l, k)
        }
    };
    this.MouseMove = function(l, k) {
        if (l.preventDefault) {
            l.preventDefault()
        }
        if (d) {
            k.moveViewport();
            a = true;
            b = true
        }
        this.Callback("MouseMove", l, k);
        if (this.IsAndroidGesture(l)) {
            this.GestureChange(l, k)
        }
        l.returnValue = false
    };
    this.MouseUp = function(n, l) {
        if (n.preventDefault) {
            n.preventDefault()
        }
        if (d) {
            l.update()
        }
        var k = new Date().getTime();
        var m = g || k + 1;
        var q = k - m;
        var p = l.viewportInfo;
        var o = false;
        if (p.lastCursorPosUp != undefined) {
            o = p.lastCursorPosUp.x == p.lastCursorPosDown.x && p.lastCursorPosUp.y == p.lastCursorPosDown.y
        }
        if (!o && d) {
            l.OnEndDrag.triggered(l.canvasInfo)
        }
        if (q < 500 && q > 0 && o) {
            l.viewportInfo.lastCursorDelta = e == 1 ? 1 : -1;
            l.OnDoubleClick.triggered(l.viewportInfo);
            f.viewport = l;
            f.displayCross = false;
            f.panCenter = false;
            f.scroll = 1;
            f.callback()
        }
        g = k;
        d = false;
        this.Callback("MouseUp", n, l);
        if (SD.isAndroid) {
            this.GestureEnd(n, l)
        }
        return false
    };
    this.GestureStart = function(l, k) {
        SD.util.cancelEvent(l);
        if (l.preventDefault) {
            l.preventDefault()
        }
        if (this.IsAndroidGesture(l)) {
            var o = {
                x: l.touches[0].pageX,
                y: l.touches[0].pageY
            };
            var n = {
                x: l.touches[1].pageX,
                y: l.touches[1].pageY
            };
            j = this.getDistance(o, n)
        }
        var m = this.getPos(l, k);
        if (isNaN(m.x)) {
            m = {
                x: k.viewportInfo.canvasSize.width / 2,
                y: k.viewportInfo.canvasSize.height / 2
            }
        }
        k.viewportInfo.lastCursorPosDown = m;
        k.viewportLayer.setTopLeft({
            x: 0,
            y: 0
        });
        k.clearMap();
        k.animateMap();
        d = false
    };
    this.GestureEnd = function(l, k) {
        SD.util.cancelEvent(l);
        SD.util.debug(k.viewportInfo.scale);
        if (k.updateMapLayerByNearest(k.viewportInfo.scale, false) != false) {
            k.draw()
        }
        k.viewportInfo.lastCursorDelta = l.scale < 1 ? -1 : 1;
        k.OnEndWheel.triggered(k.viewportInfo)
    };
    this.GestureChange = function(n, l) {
        SD.util.cancelEvent(n);
        if (n.preventDefault) {
            n.preventDefault()
        }
        if (this.IsAndroidGesture(n)) {
            var q = {
                x: n.touches[0].pageX,
                y: n.touches[0].pageY
            };
            var p = {
                x: n.touches[1].pageX,
                y: n.touches[1].pageY
            };
            var m = this.getDistance(q, p);
            n.scale = m / j
        }
        var o = l.viewportInfo.levelIndex <= 5 && n.scale < 1 ? 4 : 1;
        var k = l.viewportInfo.mapConfig.scale * (1 / n.scale) * o;
        l.wheelCenter(k, l.getCursorDistanceFromCenter(), l.viewportInfo.lastCursorLatLon);
        l.viewportInfo.mapConfig.ratio = n.scale;
        l.setScale(k);
        l.animateMap()
    }
};
SD.pantool.SimpleAnimateZoom = function() {
    this.aScale = {
        first: 0,
        latest: 0,
        inValid: function() {
            return this.latest == -1 || this.first == this.latest
        },
        reset: function() {
            this.first = 0;
            this.latest = 0
        }
    };
    var a = null;
    this.count = 0;
    this.reset = function() {
        if (a) {
            clearInterval(a);
            a = null
        }
    };
    this.temp = {
        offsetCenter: null,
        scaleFirst: null,
        scaleLatest: null,
        scaleInit: null,
        ratio: null,
        level: null,
        canvasSize: {
            width: null,
            height: null
        },
        offsetMap: {
            x: null,
            y: null
        },
        pos: {
            x: null,
            y: null
        },
        tmpPos: {
            x: null,
            y: null,
            level: null
        },
        initPos: {
            x: null,
            y: null
        },
        differentPoint: false,
        deltaPos: {
            dx: 0,
            dy: 0,
            rat: 0
        },
        prevTime: 0
    };
    this.point = {
        old: {
            pointGeo: null,
            topLeftGeo: null,
            centerGeo: null,
            topLeftScreen: null,
            scale: null,
            geoView: null
        },
        nw: {
            pointGeo: null,
            topLeftGeo: null,
            centerGeo: null,
            topLeftScreen: null,
            scale: null
        }
    };
    this.animate = function(i, c, g, j, b, p, e) {
        e.activeTool.setPreventPanning(true);
        var h = SD.util.easeInOut(i.aScale, c, g);
        var m = b.mapConfig.scale / h;
        if (j) {
            i.temp.ratio = m
        } else {
            m *= i.temp.ratio
        }
        var n = b.projection.geoToPixel(i.point.old.topLeftGeo.lon, i.point.old.topLeftGeo.lat, h);
        var l = b.projection.inflateGeo(i.point.nw.pointGeo, p.offsetCenter.x, p.offsetCenter.y, h);
        var k = b.projection.geoToMetric(l.lon, l.lat);
        var d = b.projection.metricToPixel(k.x, k.y, h);
        var o = {
            x: d.x - (b.canvasSize.width / 2),
            y: d.y - (b.canvasSize.height / 2)
        };
        var f = {
            x: (n.x - o.x),
            y: (n.y - o.y)
        };
        e.zoomLayer.setTransform(m, f);
        return m
    };
    this.go = function(c) {
        if (a) {
            return
        }
        this.count++;
        var n = c.viewport;
        var r = n.viewportInfo;
        var e = false;
        var k = {
            lon: r.lastCursorLatLon.lon,
            lat: r.lastCursorLatLon.lat
        };
        var q = n.getCursorDistanceFromCenter();
        var p = false;
        var o = {
            dx: 0,
            dy: 0
        };
        var g = {
            x: 0,
            y: 0
        };
        this.point.nw.topLeftGeo = r.topLeftGeo;
        this.point.nw.topLeftScreen = SD.util.clone(r.topLeftScreen);
        this.point.nw.pointGeo = r.lastCursorLatLon;
        this.point.nw.scale = r.scale;
        this.point.nw.centerGeo = r.centerGeo;
        var b = new Date().getTime();
        var f = b - this.temp.prevTime;
        var j = false;
        if (this.temp.prevTime == 0) {
            j = true
        }
        this.temp.prevTime = b;
        var d = true;
        if (this.point.old.geoView) {
            d = r.isInViewport(this.point.old.geoView)
        }
        var l = n.getCompletedPercentage();
        if (this.temp.level == r.levelIndex || !d || (f > 300 && l > 70) || j) {
            p = true;
            this.temp.level = r.levelIndex;
            e = false;
            this.temp.differentPoint = false;
            this.point.old.topLeftGeo = r.topLeftGeo;
            this.point.old.topLeftScreen = SD.util.clone(r.topLeftScreen);
            this.point.old.pointGeo = r.lastCursorLatLon;
            this.point.old.centerGeo = r.centerGeo;
            this.point.old.scale = r.scale;
            this.point.old.geoView = r.geoView
        }
        if (!c.offsetCenter) {
            var m = new DrawingTool();
            c.offsetCenter = m.getOffsetPt(r.lastCursorPosMove, n, p, this)
        }
        if (this.temp.tmpPos.level != r.levelIndex && this.temp.tmpPos.x != null && this.temp.tmpPos.y != null && r.lastCursorPosMove.x != this.temp.tmpPos.x && r.lastCursorPosMove.y != this.temp.tmpPos.y) {
            e = true
        }
        var h = c.step || 6;
        var s = r.lastCursorDelta;
        this.aScale.first = r.scale;
        this.aScale.latest = n.getNextLevel(s > 0 ? true : false);
        if (c.scaleIncrement) {
            var i = r.scale * c.scaleIncrement;
            this.aScale.latest = s > 0 ? r.scale - i : r.scale + i
        }
        if (p) {
            this.temp.scaleFirst = this.aScale.latest;
            this.temp.scaleInit = this.aScale.first;
            this.temp.tmpPos.level = r.levelIndex;
            this.temp.initPos = r.projection.geoToPixel(r.lastCursorLatLon.lon, r.lastCursorLatLon.lat, this.temp.scaleInit)
        } else {
            this.aScale.first = this.temp.scaleFirst
        }
        if (this.aScale.inValid()) {
            return
        }
        n.clearMap(p);
        n.mapLayer.tiles.unReloadImg();
        n.animateMap();
        if (SD.isIE) {
            n.zoomLayer.setWidth(r.canvasSize)
        }
        var t = 0,
            u = this;
        if (this.point.old.topLeftGeo == null) {
            this.point.old.topLeftGeo = SD.util.clone(r.lastCursorLatLon)
        }
        this.animate(u, h, t, p, r, c, n);
        a = setInterval(function() {
            var v = u.animate(u, h, t, p, r, c, n);
            t++;
            if (t > h) {
                clearInterval(a);
                a = null;
                n.wheelCenter(u.aScale.latest, q, k);
                n.activeTool.setPreventPanning(false);
                if (c.scaleIncrement) {
                    if (c.callback) {
                        c.callback(n.viewportInfo)
                    }
                    return
                }
                n.setLevel(s > 0 ? r.levelIndex + 1 : r.levelIndex - 1);
                n.updateMapLayerByNearest(u.aScale.latest, true);
                if (u.temp.level == r.levelIndex) {
                    n.zoomLayer.setUnTransform()
                }
                n.draw();
                u.temp.offsetCenter = c.offsetCenter;
                u.temp.scaleFirst = u.aScale.latest;
                u.temp.ratio = v;
                if (e) {
                    u.temp.tmpPos.x = r.lastCursorPosMove.x;
                    u.temp.tmpPos.y = r.lastCursorPosMove.y;
                    u.temp.differentPoint = true
                }
            }
        }, 100)
    }
};

function AnimateZoom() {
    this.viewport = null;
    this.scroll = 0;
    this.aScale = {
        first: 0,
        latest: 0
    };
    this.panCenter = false;
    this.displayCross = true;
    var c = null;
    var a = null;
    var b = {
        offset: null,
        cursor: null,
        geo: null
    };
    this.init = function() {
        if (c == null) {
            var d = this.viewport.viewportInfo.canvasSize;
            c = {};
            c.h = document.createElement("div");
            c.v = document.createElement("div");
            c.h.style.cssText = "border-style: solid none none none; border-color:rgb(5, 137, 79); width: " + d.width + "px; border-width:1px; height: 1px; position: absolute; left: 0px; top: 0p; display:none";
            c.v.style.cssText = "border-style: none solid none none; border-color:rgb(5, 137, 79); width: 1px; height: " + d.height + "px; border-width:1px; position: absolute; left: 0px; top: 0p; display:none";
            this.viewport.viewportInfo.div.appendChild(c.h);
            this.viewport.viewportInfo.div.appendChild(c.v)
        }
    };
    this.setCrossDisplay = function(e) {
        var d = "";
        if (!e) {
            d = "none"
        } else {
            c.h.style.width = this.viewport.viewportInfo.canvasSize.width + "px";
            c.v.style.height = this.viewport.viewportInfo.canvasSize.height + "px"
        }
        c.h.style.display = d;
        c.v.style.display = d
    };
    this.setCrossCursor = function(d) {
        if (!this.displayCross || d == null) {
            return
        }
        this.setCrossDisplay(true);
        c.h.style.top = d.y + "px";
        c.v.style.left = d.x + "px"
    };
    this.animate = function(e, d) {
        if (a) {
            clearInterval(a)
        }
        var f = 0,
            g = this;
        a = setInterval(function() {
            g.setCrossCursor(b.cursor);
            if (f == 0) {
                g.viewport.viewportLayer.setTopLeft({
                    x: 0,
                    y: 0
                });
                g.viewport.clearMap()
            }
            var j = SD.util.easeInOut(g.aScale, e, f);
            var i = g.viewport.viewportInfo.mapConfig.scale / j;
            i = f == 0 && i == 1 ? 0.99 : i;
            var h = i >= 0.1 && g.aScale.latest != 0;
            if (h) {
                if (!g.panCenter) {
                    g.viewport.wheelCenter(j, b.offset, b.geo)
                }
                g.viewport.viewportInfo.mapConfig.ratio = i;
                g.viewport.setScale(j);
                g.viewport.animateMap()
            }
            f++;
            if (f > e || i < 0.09) {
                g.zoomViewport(d);
                window.clearInterval(a);
                a = null
            }
        }, 20)
    };
    this.zoomViewport = function(d) {
        this.setCrossDisplay(false);
        this.viewport.setLevel(d ? this.viewport.viewportInfo.levelIndex + 1 : this.viewport.viewportInfo.levelIndex - 1);
        if (!this.panCenter) {
            this.viewport.wheelCenter(this.aScale.latest, b.offset, b.geo)
        }
        if (this.aScale.latest == 0) {
            return
        }
        this.viewport.updateMapLayerByNearest(this.aScale.latest, true);
        this.viewport.draw();
        this.scroll = 0;
        this.aScale = {
            first: 0,
            latest: 0
        };
        b = {
            offset: null,
            cursor: null,
            geo: null
        }
    };
    this.preInit = function() {
        if (this.scroll == 1) {
            b.offset = this.viewport.getCursorDistanceFromCenter();
            b.geo = this.viewport.viewportInfo.lastCursorLatLon;
            b.cursor = this.viewport.viewportInfo.lastCursorPosMove
        }
    };
    this.callback = function() {
        this.init();
        var g = this.viewport.viewportInfo.lastCursorDelta;
        var e = this.viewport.viewportInfo.levelIndex;
        if (this.scroll > 5) {
            if (g > 0) {
                this.viewport.setLevel(e + 1)
            } else {
                this.viewport.setLevel(e - 1)
            }
        }
        this.aScale.first = this.viewport.viewportInfo.scale;
        this.aScale.latest = this.viewport.getNextLevel(g > 0 ? true : false);
        if (this.aScale.latest == -1) {
            if (this.scroll > 5) {
                this.viewport.setLevel(g > 0 ? e - 1 : e + 1)
            }
            this.scroll = 0;
            b = {
                offset: null,
                cursor: null,
                geo: null
            }
        } else {
            if (this.aScale.first != this.aScale.latest) {
                var f = Math.abs(this.aScale.first - this.aScale.latest);
                this.animate(f < 4 ? 2 : 3, g > 0)
            } else {
                this.scroll = 0;
                b = {
                    offset: null,
                    cursor: null,
                    geo: null
                }
            }
        }
    }
}
SD.pantool.Timer = function() {
    this.moreInterval = true;
    this.useTimeout = false;
    var c = {
        interval: 25,
        time: null,
        deviation: 0
    };
    var b = null,
        a = 0;
    this.setTInterval = function(d) {
        c.interval = d
    };
    this.isRender = function() {
        if (c.time != null) {
            var d = new Date();
            c.deviation = d.getTime() - c.time.getTime();
            if (!this.useTimeout) {
                c.time = d
            }
            if (c.deviation == 0) {
                return false
            }
            if ((this.moreInterval && c.deviation < c.interval) || (!this.moreInterval && c.deviation >= c.interval)) {
                return true
            }
        }
        return false
    };
    this.reset = function() {
        c.deviation = 0;
        a = 0;
        if (b && this.useTimeout) {
            window.clearTimeout(b)
        }
        b = null
    };
    this.hit = function(d) {
        var e = this;
        if (b && this.useTimeout) {
            window.clearTimeout(b)
        }
        if (this.isRender()) {
            if (d != undefined && d.callback) {
                d.callback();
                this.reset()
            }
        } else {
            if ((this.moreInterval && c.deviation > c.interval) || (!this.moreInterval && c.deviation > 1000)) {
                this.reset()
            } else {
                if (this.useTimeout) {
                    a++;
                    b = window.setTimeout(function() {
                        e.hit(d)
                    }, 50)
                }
            }
        }
    };
    this.start = function(d) {
        if (c.time == null || this.useTimeout) {
            c.time = new Date()
        }
        this.hit(d)
    }
};
var DrawingTool = SD.pantool.Drawing,
    DraggableTool = SD.pantool.Draggable,
    ViewportPanTool = SD.pantool.Viewport,
    IphonePanTool = SD.pantool.Iphone,
    SimpleAnimateZoom = SD.pantool.SimpleAnimateZoom,
    Timer = SD.pantool.Timer;
SD.vector = {
    XMLNS_SVG: "http://www.w3.org/2000/svg"
};
SD.vector.SVG = function(d, c, a) {
    this.div = d;
    if (!c) {
        c = d.clientWidth
    }
    if (!a) {
        a = d.clientHeight
    }
    this._currentShape = null;
    this.width = c;
    this.height = a;
    this._stack = [];
    this._stackSize = 0;
    var b = document.createElementNS(SD.vector.XMLNS_SVG, "svg");
    b.setAttribute("width", c);
    b.setAttribute("height", a);
    b.setAttribute("overflow", "visible");
    this.div.appendChild(b);
    this._root = b;
    this.setPosition = function(f, e) {
        this._root.style.position = "absolute";
        this._root.style.zIndex = 0;
        if (!isNaN(e)) {
            this._root.style.left = e + "px"
        }
        if (!isNaN(f)) {
            this._root.style.top = f + "px"
        }
    };
    this.setViewBox = function(f, e) {
        if (!e) {
            e = 2
        }
        var g = f.left + " " + f.top + " " + f.width() + " " + f.height();
        this._root.setAttribute("viewBox", g);
        this._root.setAttribute("preserveAspectRatio", "none");
        this._root.setAttribute("xmlns", "http://www.w3.org/2000/svg")
    };
    this.setSize = function(e) {
        this._root.setAttribute("width", e.width);
        this._root.setAttribute("height", e.height);
        this.width = e.width;
        this.height = e.height
    };
    this.setAttribute = function(g, e) {
        for (var f in e) {
            g.setAttributeNS(null, f, e[f])
        }
    };
    this.createCircle = function(h, f) {
        var e = document.createElementNS(SD.vector.XMLNS_SVG, "ellipse");
        e.setAttribute("cx", h.x);
        e.setAttribute("cy", h.y);
        e.setAttribute("stroke-linecap", "round");
        e.setAttribute("stroke-linejoin", "round");
        var g = f.size ? f.size : 0;
        e.setAttribute("rx", (f.diameter || f.diameterHorizontal) - g);
        e.setAttribute("ry", (f.diameter || f.diameterVertical) - g);
        if (f.bgColor) {
            e.setAttribute("fill", f.bgColor)
        }
        if (f.lineColor || f.color) {
            e.setAttribute("stroke", f.lineColor || f.color)
        }
        if (f.lineWidth || f.size) {
            e.setAttribute("stroke-width", f.lineWidth || f.size)
        }
        if (f.opacity >= 0) {
            e.setAttribute("opacity", f.opacity)
        }
        if (f.fillOpacity >= 0) {
            e.setAttribute("fill-opacity", f.fillOpacity)
        }
        if (f.dash > 0) {
            e.setAttribute("stroke-dasharray", f.dash)
        }
        this._root.appendChild(e);
        this._pushStack(e)
    };
    this.createArrow = function(j, f) {
        var e = document.createElementNS(SD.vector.XMLNS_SVG, "polyline");
        var i = f.diameter;
        var g = f.size ? f.size : 0;
        i -= g;
        var h = (j.x + i - 5) + "," + (j.y - 5) + " " + (j.x + i) + "," + j.y + " " + j.x + "," + j.y + " " + (j.x + i) + "," + j.y + " " + (j.x + i - 5) + "," + (j.y + 5);
        e.setAttribute("fill", "none");
        e.setAttribute("stroke-linecap", "round");
        e.setAttribute("stroke-linejoin", "round");
        e.setAttribute("points", h);
        e.setAttribute("stroke", f.color || f.lineColor);
        e.setAttribute("stroke-width", f.size || f.lineWidth);
        this._root.appendChild(e);
        this._pushStack(e)
    };
    this.createText = function(g, f) {
        var e = document.createElementNS(SD.vector.XMLNS_SVG, "text");
        e.setAttribute("x", g.x + f.fromCenter);
        e.setAttribute("y", g.y - 5);
        e.setAttribute("fill", "red");
        e.setAttribute("stroke-linejoin", "bevel");
        e.setAttribute("font-size", 12);
        e.appendChild(document.createTextNode(f.text));
        this._root.appendChild(e);
        this._pushStack(e)
    };
    this._pushStack = function(e) {
        if (this._stackSize + 1 < this._stack.length) {
            this._stack.length = this._stackSize + 1
        }
        this._stack[this._stackSize++] = e
    };
    this.clear = function() {
        for (var e = this._stackSize; e--;) {
            if (this._stack[e] != undefined) {
                this._root.removeChild(this._stack[e])
            }
        }
        this._stack.length = 0;
        this._stackSize = 0
    }
};
SD.vector.Canvas = function(c, b, a) {
    this.div = c;
    if (!b) {
        b = c.clientWidth
    }
    if (!a) {
        a = c.clientHeight
    }
    this._currentShape = null;
    this.width = b;
    this.rect = {};
    this.height = a;
    this._stack = [];
    this._stackSize = 0;
    var d = document.createElement("canvas");
    d.setAttribute("id", "canvas_trans");
    d.setAttribute("width", b);
    d.setAttribute("height", a);
    d.setAttribute("overflow", "visible");
    this.div.appendChild(d);
    this._root = d;
    this.setPosition = function(f, e) {
        this._root.style.position = "absolute";
        this._root.style.zIndex = 0;
        if (!isNaN(e)) {
            this._root.style.left = e + "px"
        }
        if (!isNaN(f)) {
            this._root.style.top = f + "px"
        }
    };
    this.setViewBox = function(f, e) {
        this.rect = f
    };
    this.setSize = function(e) {
        this._root.setAttribute("width", e.width);
        this._root.setAttribute("height", e.height);
        this.width = e.width;
        this.height = e.height
    };
    this.setAttribute = function(g, e) {
        for (var f in e) {
            g.setAttribute(null, f, e[f])
        }
    };
    this.createCircle = function(g, f) {
        var e = this._root.getContext("2d");
        e.beginPath();
        e.arc(g.x, g.y, (f.diameter || f.diameterHorizontal) - size, 0, Math.PI * 2, true);
        if (f.bgColor) {
            e.fillStyle = f.bgColor
        }
        if (f.lineColor || f.color) {
            e.strokeStyle = f.lineColor || f.color
        }
        if (f.lineWidth || f.size) {
            e.lineWidth = f.lineWidth || f.size
        }
        e.closePath()
    };
    this.createArrow = function(j, g) {
        var f = this._root.getContext("2d");
        f.beginPath();
        var e = document.createElementNS(SD.vector.XMLNS_SVG, "polyline");
        var i = g.diameter;
        var h = g.size ? g.size : 0;
        i -= h;
        f.lineWidth = g.size || g.lineWidth;
        f.lineJoin = "mitter";
        f.moveTo((j.x + i - 5), (j.y - 5));
        f.lineTo((j.x + i), j.y);
        f.lineTo(j.x, j.y);
        f.lineTo((j.x + i), j.y);
        f.lineTo((j.x + i - 5), (j.y + 5));
        f.stoke();
        f.closePath()
    };
    this.createText = function(g, f) {
        var e = this._root.getContext("2d");
        e.beginPath();
        e.fillStyle = "red";
        e.font = "12pt verdana";
        e.fillText(f.text, g.x, g.y - 5);
        e.closePath()
    };
    this._pushStack = function(e) {};
    this.clear = function() {
        var e = this._root.getContext("2d");
        e.clearRect(0, 0, b, a)
    }
};
SD.vector.VML = function(d, c, a) {
    SD.util.initVML();
    if (!c) {
        c = d.clientWidth
    }
    if (!a) {
        a = d.innerHeight || d.clientHeight
    }
    var b = document.createElement("v:group");
    b.style.cssText = "width:" + c + "px; height:" + a + "px; position: absolute; ";
    d.appendChild(b);
    this._root = b;
    this.width = c;
    this.height = a;
    this._currentShape = null;
    this._stack = [];
    this._stackSize = 0;
    this.setPosition = function(f, e) {
        if (!isNaN(e)) {
            this._root.style.left = e + "px"
        }
        if (!isNaN(f)) {
            this._root.style.top = f + "px"
        }
    };
    this.setViewBox = function(f, e) {
        if (!e) {
            e = 2
        }
        this._root.coordorigin = f.left + " " + f.top;
        this._root.coordsize = parseFloat(f.width()) + "," + parseFloat(f.height())
    };
    this.setSize = function(f, e) {
        this._root.style.width = f.width + "px";
        this._root.style.height = f.height + "px";
        if (!e) {
            this._root.coordorigin = "0 0";
            this._root.coordsize = f.width + "," + f.height
        }
        this.width = f.width;
        this.height = f.height
    };
    this.setAttribute = function(g, e) {
        for (var f in e) {
            g.i = e[f]
        }
    };
    this.createCircle = function(l, g) {
        var f = document.createElement("v:oval");
        f.strokeweight = 2;
        if (g.diameter) {
            var e = g.diameter * 2;
            f.style.cssText = "width: " + e + "px;height: " + e + "px; left: " + (l.x - g.diameter) + "px; top: " + (l.y - g.diameter) + "px; "
        }
        if (g.diameterHorizontal && g.diameterVertical) {
            var e = g.diameterHorizontal * 2;
            var i = g.diameterVertical * 2;
            f.style.cssText = "width: " + e + "px;height: " + i + "px; left: " + (l.x - g.diameterHorizontal) + "px; top: " + (l.y - g.diameterVertical) + "px; "
        }
        f.filled = g.bgColor == "none" ? false : true;
        if (g.lineColor || g.size) {
            f.strokecolor = g.lineColor || g.size
        }
        if (g.lineWidth || g.size) {
            f.strokeweight = (g.lineWidth || g.size) + "px"
        }
        var k = document.createElement("v:stroke");
        k.endcap = "round";
        if (g.opacity >= 0) {
            k.opacity = g.opacity
        }
        if (g.dash) {
            k.dashstyle = "dash"
        }
        f.appendChild(k);
        if (g.fillOpacity >= 0) {
            var j = document.createElement("v:fill");
            j.unselectable = "on";
            if (g.bgColor) {
                j.color = g.bgColor
            }
            if (g.fillOpacity >= 0) {
                j.opacity = g.fillOpacity
            }
            f.appendChild(j)
        }
        this._root.appendChild(f);
        this._pushStack(f)
    };
    this.createArrow = function(g, f) {
        var e = document.createElement("v:polyline");
        e.filled = false;
        if (f.lineColor) {
            e.strokecolor = f.lineColor
        }
        if (f.lineWidth) {
            e.strokeweight = f.lineWidth + "px"
        }
        e.points = (g.x + f.diameter - 5) + "," + (g.y - 5) + " " + (g.x + f.diameter) + "," + g.y + " " + g.x + "," + g.y + " " + (g.x + f.diameter) + "," + g.y + " " + (g.x + f.diameter - 5) + "," + (g.y + 5);
        this._root.appendChild(e);
        this._pushStack(e)
    };
    this.createText = function(g, e) {
        var f = document.createElement("v:line");
        f.from = g.x + " " + (g.y - 10);
        f.to = (g.x + e.fromCenter + e.text.length * 10) + " " + (g.y);
        f.innerHTML = "<v:fill on='True' color='red'/><v:path textpathok='True'/><v:textpath on='True' string='" + e.text + "' style='font-family:Arial;font-size:8pt;'/>";
        this._root.appendChild(f);
        this._pushStack(f)
    };
    this._pushStack = function(e) {
        if (this._stackSize + 1 < this._stack.length) {
            this._stack.length = this._stackSize + 1
        }
        this._stack[this._stackSize++] = e
    };
    this.clear = function() {
        for (var e = this._stack.length; e--;) {
            if (this._stack[e] != undefined) {
                this._root.removeChild(this._stack[e])
            }
        }
        this._stack.length = 0;
        this._stackSize = 0
    }
};

function PolylineHandle(a) {
    this.canvas = a._root;
    this.object = null;
    if (SD.isSvg) {
        this.initSVG()
    } else {
        if (SD.isCanvas) {} else {
            this.initVML()
        }
    }
}
PolylineHandle.prototype.initSVG = function() {
    if (this.object == null) {
        this.object = document.createElementNS(SD.vector.XMLNS_SVG, "rect");
        this.object.setAttribute("width", 10);
        this.object.setAttribute("height", 10);
        this.object.setAttribute("stroke", "black");
        this.object.setAttribute("fill", "white");
        this.object.setAttribute("display", "none");
        if (this.canvas != null) {
            this.canvas.appendChild(this.object)
        }
    }
};
PolylineHandle.prototype.setPosition = function(a) {
    if (SD.isSvg) {
        this.object.setAttribute("x", a.x);
        this.object.setAttribute("y", a.y);
        this.object.setAttribute("display", "inline")
    } else {
        this.object.style.left = a.x + "px";
        this.object.style.top = a.y + "px";
        this.object.style.display = "inline"
    }
};
PolylineHandle.prototype.initVML = function() {
    if (this.object == null) {
        this.object = document.createElement("v:rect");
        this.object.style.cssText = "width:10px;height:10px;position:absolute;display:none";
        this.object.filled = true;
        this.object.strokecolor = "black";
        this.object.strokeweight = "1px";
        if (this.canvas != null) {
            this.canvas.appendChild(this.object)
        }
    }
};
SD.vector.PathSVG = function(a) {
    var b = document.createElementNS(SD.vector.XMLNS_SVG, "path");
    a.appendChild(b);
    return {
        setPoints: function(d) {
            if (d.length > 0) {
                var e = "M" + parseFloat(d[0].x) + " " + parseFloat(d[0].y) + " L";
                for (var c = 1; c < d.length; c++) {
                    e += parseFloat(d[c].x) + " " + parseFloat(d[c].y) + " "
                }
                b.style.display = "";
                b.setAttribute("d", e)
            }
        },
        clear: function() {
            b.style.display = "none"
        },
        arrow: function(h, f, e, c) {
            var g = document.createElementNS(SD.vector.XMLNS_SVG, "path");
            if (c.color) {
                g.setAttribute("fill", c.color);
                g.setAttribute("stroke", c.color)
            }
            if (c.size) {
                g.setAttribute("stroke-width", c.size)
            }
            g.setAttribute("stroke-linecap", "round");
            g.setAttribute("stroke-linejoin", "round");
            var d = "M " + h.x + " " + h.y + " L " + f.x + " " + f.y + " " + e.x + " " + e.y;
            g.setAttribute("d", d);
            return g
        },
        setOptions: function(c) {
            if (!c.bgColor) {
                c.bgColor = "none"
            }
            if (c.bgColor) {
                b.setAttribute("fill", c.bgColor)
            }
            if (c.color) {
                b.setAttribute("stroke", c.color)
            }
            if (c.size) {
                b.setAttribute("stroke-width", c.size)
            }
            if (c.opacity >= 0) {
                b.setAttribute("opacity", c.opacity)
            }
            if (c.fillOpacity >= 0) {
                b.setAttribute("fill-opacity", c.fillOpacity)
            }
            if (c.dash > 0) {
                b.setAttribute("stroke-dasharray", c.dash)
            }
            b.setAttribute("stroke-linecap", "round");
            b.setAttribute("stroke-linejoin", "round")
        }
    }
};
SD.vector.PathVML = function(c, b) {
    var e = document.createElement("v:polyline");
    var d = document.createElement("v:stroke");
    e.appendChild(d);
    var a = document.createElement("v:skew");
    a.on = "false";
    e.appendChild(a);
    c.appendChild(e);
    return {
        setPoints: function(g) {
            var h = "";
            for (var f = 0; f < g.length; f++) {
                h += (f > 0 ? "," : "") + parseInt(g[f].x) + "," + parseInt(g[f].y)
            }
            if (e.points) {
                e.points.value = h
            } else {
                e.points = h
            }
        },
        clear: function() {
            if (e.points) {
                e.points.value = ""
            } else {
                e.points = ""
            }
        },
        arrow: function(k, i, h, f) {
            var j = document.createElement("v:polyline");
            j.filled = true;
            if (f.color) {
                j.fillcolor = f.color;
                j.strokecolor = f.color
            }
            if (f.size) {
                j.strokeweight = f.size + "px"
            }
            var g = i.x + "," + i.y + " " + k.x + "," + k.y + " " + h.x + "," + h.y;
            if (j.points) {
                j.points.value = g
            } else {
                j.points = g
            }
            var l = document.createElement("v:stroke");
            l.endcap = "round";
            if (f.opacity >= 0) {
                l.opacity = f.opacity
            }
            j.appendChild(l);
            return j
        },
        setOptions: function(g) {
            e.filled = !g.bgColor ? false : true;
            if (g.color) {
                e.strokecolor = g.color
            }
            if (g.size) {
                e.strokeweight = g.size + "px"
            }
            var j = e.children,
                k = false;
            for (var h = 0; h < j.length; h++) {
                var n = j[h];
                if (n.nodeName == "stroke") {
                    var m = n;
                    m.endcap = "round";
                    if (g.opacity >= 0) {
                        m.opacity = g.opacity
                    }
                    if (g.dash) {
                        m.dashstyle = g.dash + " 1"
                    }
                } else {
                    if (n.nodeName == "fill" && g.fillOpacity >= 0) {
                        var l = n;
                        k = true;
                        l.unselectable = "on";
                        if (g.bgColor) {
                            l.color = g.bgColor
                        }
                        if (g.fillOpacity >= 0) {
                            l.opacity = g.fillOpacity
                        }
                    } else {
                        if (n.nodeName == "skew" && g.transform) {
                            var f = n;
                            f.on = "true";
                            if (g.transform.scale) {
                                f.matrix = g.transform.scale + ",0,0," + g.transform.scale + ",0,0"
                            }
                            if (g.transform.offset) {
                                f.offset = g.transform.offset.x + "px," + g.transform.offset.y + "px"
                            }
                        }
                    }
                }
            }
            if (!k && g.fillOpacity) {
                var l = document.createElement("v:fill");
                l.unselectable = "on";
                if (g.bgColor) {
                    l.color = g.bgColor
                }
                if (g.fillOpacity >= 0) {
                    l.opacity = g.fillOpacity
                }
                e.appendChild(l)
            }
        }
    }
};
SD.vector.PathCanvas = function(a) {
    var c = a.getContext("2d"),
        b = function(r, p, s, q) {
            var o = [10, 4];
            var g = function(v, u) {
                return v <= u
            };
            var e = function(v, u) {
                return v >= u
            };
            var d = function(v, u) {
                return Math.min(v, u)
            };
            var m = function(v, u) {
                return Math.max(v, u)
            };
            var l = {
                thereYet: e,
                cap: d
            };
            var i = {
                thereYet: e,
                cap: d
            };
            if (p - q > 0) {
                i.thereYet = g;
                i.cap = m
            }
            if (r - s > 0) {
                l.thereYet = g;
                l.cap = m
            }
            c.moveTo(r, p);
            var k = r;
            var h = p;
            var t = 0,
                j = true;
            while (!(l.thereYet(k, s) && i.thereYet(h, q))) {
                var f = Math.atan2(q - p, s - r);
                var n = o[t];
                k = l.cap(s, k + (Math.cos(f) * n));
                h = i.cap(q, h + (Math.sin(f) * n));
                if (j) {
                    c.lineTo(k, h)
                } else {
                    c.moveTo(k, h)
                }
                t = (t + 1) % o.length;
                j = !j
            }
        };
    return {
        setPoints: function(f, e) {
            c = a.getContext("2d");
            c.beginPath();
            if (f.length > 0) {
                c.moveTo(parseFloat(f[0].x), parseFloat(f[0].y));
                for (var d = 1; d < f.length; d++) {
                    if (e.dash) {
                        if (f[d] != undefined) {
                            b(f[d - 1].x, f[d - 1].y, f[d].x, f[d].y)
                        }
                    } else {
                        c.lineTo(parseFloat(f[d].x), parseFloat(f[d].y))
                    }
                }
            }
        },
        clear: function() {
            c.clearRect(0, 0, a.getAttribute("width"), a.getAttribute("height"))
        },
        arrow: function(h, g, f, e) {
            var d = a.getContext("2d");
            d.beginPath();
            if (e.color) {
                d.fillStyle = e.color;
                d.strokeStyle = e.color
            }
            if (e.size) {
                d.lineWidth = e.size
            }
            d.moveTo(h.x, h.y);
            d.lineTo(g.x, g.y);
            d.lineTo(f.x, f.y);
            d.lineJoin = "miter";
            d.closePath();
            d.fill();
            d.stroke();
            return false
        },
        setOptions: function(d) {
            c.clearRect(0, 0, a.getAttribute("width"), a.getAttribute("height"));
            if (d.size) {
                c.lineWidth = d.size
            }
            if (d.color) {
                c.strokeStyle = d.color
            }
            if (d.opacity >= 0) {
                c.globalAlpha = d.opacity
            }
            c.stroke();
            if (d.fillOpacity >= 0) {
                c.globalAlpha = d.fillOpacity;
                c.fillStyle = d.bgColor;
                c.fill()
            }
        }
    }
};
SD.vector.Polyline = function(a) {
    this.canvas = a._root;
    this.points = null;
    this.options = {};
    this.arrow = [];
    if (SD.isSvg) {
        this.object = new SD.vector.PathSVG(this.canvas)
    } else {
        if (SD.isCanvas) {
            this.object = new SD.vector.PathCanvas(this.canvas)
        } else {
            this.object = new SD.vector.PathVML(this.canvas)
        }
    }
};
SD.vector.Polyline.prototype.init = function(b, a) {
    this.points = b;
    this.options = a;
    this.object.setPoints(b, a);
    this.setOptions(a)
};
SD.vector.Polyline.prototype.addArrow = function(i, f, n) {
    var c = 12;
    var l = new Point(f.x - i.x, f.y - i.y);
    var m = Math.sqrt(Math.pow(l.x, 2) + Math.pow(l.y, 2));
    var o = new Point(l.x / m, l.y / m);
    var b = new Point(f.x - (c * o.x), f.y - (c * o.y));
    var k = new Point(l.y, -l.x);
    var a = Math.sqrt(Math.pow(k.x, 2) + Math.pow(k.y, 2));
    var d = new Point(k.x / a, k.y / a);
    var h = f;
    var j = new Point(b.x + (c * d.x / 2), b.y + (c * d.y / 2));
    var e = new Point(b.x - (c * d.x / 2), b.y - (c * d.y / 2));
    var g = this.object.arrow(j, h, e, n);
    if (g) {
        this.canvas.appendChild(g);
        this.arrow.push(g)
    }
};
SD.vector.Polyline.prototype.clearArrow = function() {
    for (var a = 0, b = this.arrow.length; a < b; a++) {
        this.canvas.removeChild(this.arrow[a])
    }
    this.arrow = []
};
SD.vector.Polyline.prototype.setDisplayArrow = function(a) {
    for (var b = 0, d = this.arrow.length; b < d; b++) {
        this.arrow[b].style.display = (a) ? "" : "none"
    }
};
SD.vector.Polyline.prototype.clear = function() {
    this.object.clear()
};
SD.vector.Polyline.prototype.setOptions = function(a) {
    this.options = a;
    this.object.setOptions(a)
};
if (SD.isSvg) {
    SD.vector.Drawing = SD.vector.SVG
} else {
    if (SD.isCanvas) {
        SD.vector.Drawing = SD.vector.Canvas
    } else {
        SD.vector.Drawing = SD.vector.VML
    }
}
SD.vector.Drawing.prototype.constructor = SD.vector.Drawing;
var VectorSVG = SD.vector.SVG,
    VectorCanvas = SD.vector.Canvas,
    VectorVML = SD.vector.VML,
    PolylineVector = SD.vector.Polyline,
    DrawingVector = SD.vector.Drawing;

function MapSlider(a) {
    this.minValue = 0;
    this.maxValue = 100;
    this.width = 0;
    this.height = 0;
    this.position = {
        top: 0,
        left: 0
    };
    this.value = 50;
    this.increment = 1;
    this.renderTo = null;
    this.button = null;
    this.obj = null;
    this.dragging = false;
    this.vertical = false;
    this.drag = {
        start: 0,
        end: 0
    };
    SD.apply(this, a)
}
MapSlider.prototype = {
    init: function() {
        this.obj = document.createElement("div");
        this.obj.style.cssText = "position:absolute;top:" + this.position.top + "px;left:" + this.position.left + "px;width:" + parseInt(this.renderTo.style.width) + "px; height:" + this.height + "px; cursor:pointer;";
        this.button.size = {
            width: parseInt(this.button.style.width),
            height: parseInt(this.button.style.height)
        };
        this.renderTo.appendChild(this.obj);
        this.obj.appendChild(this.button);
        this.obj.attribute = this;
        this.button.attribute = this;
        EventManager.add(this.obj, "click", function(b) {
            var c = SD.util.getCursorPos(b, this.attribute.obj);
            this.attribute.button.style.top = c.y + "px";
            this.attribute.onDragEnd(b)
        });
        EventManager.add(this.button, "mousedown", this.mouseDown);
        if (this.events) {
            if (this.events.length != undefined) {
                for (var a = 0; a < this.events.length; a++) {
                    EventManager.add(this.events[a].obj, this.events[a].type, this.events[a].callback)
                }
            } else {
                if (typeof this.events == "object") {
                    EventManager.add(this.events.obj, this.events.type, this.events.callback)
                }
            }
        }
    },
    mouseDown: function(a) {
        if (a.preventDefault) {
            a.preventDefault()
        }
        if (SD.util.getMouseButton(a) == "LEFT") {
            this.attribute.dragging = true;
            this.attribute.drag.start = SD.util.getCursorPos(a, this.attribute.obj);
            document.attribute = this.attribute;
            EventManager.add(document, "mousemove", this.attribute.mouseMove);
            EventManager.add(document, "mouseup", function(b) {
                this.attribute.dragging = false;
                this.attribute.onDragEnd(b);
                this.attribute.drag.start = {
                    start: 0,
                    end: 0
                }
            })
        }
        return true
    },
    mouseMove: function(a) {
        if (a.preventDefault) {
            a.preventDefault()
        }
        if (SD.util.getMouseButton(a) == "LEFT" && this.attribute.dragging == true) {
            if (this.attribute.vertical) {
                var c = SD.util.getCursorPos(a, this.attribute.obj);
                var b = this.attribute.obj.offsetHeight - this.attribute.button.offsetHeight;
                if (c.y < b && c.y > 0) {
                    this.attribute.button.style.top = c.y + "px"
                }
                if (c.y > this.attribute.height && c.y < 0) {
                    this.attribute.dragging = false
                }
            }
        }
        a.returnValue = false;
        return true
    },
    onDragEnd: function(f) {
        var b = this;
        var a = b.maxValue - b.minValue;
        var c;
        if (!b.vertical) {
            c = b.obj.offsetWidth - b.button.offsetWidth
        } else {
            c = b.obj.offsetHeight - b.button.offsetHeight
        }
        var d = ((parseInt(b.button.style.top) + b.button.offsetHeight) / c) * a;
        this.setValue(d)
    },
    setFromWheel: function(a) {
        this.setValue(a * this.increment, true)
    },
    setValue: function(c, f) {
        if (c < this.minValue) {
            c = this.minValue
        }
        if (c > this.maxValue) {
            c = this.maxValue
        }
        var e = c % this.increment,
            b = c;
        if (e > 0) {
            if (e > (this.increment / 2)) {
                b = c + (this.increment - e)
            } else {
                b = c - e
            }
        }
        this.value = b;
        var h = this.maxValue - this.minValue;
        var g, d, i = this.button.size;
        if (this.vertical) {
            d = (this.width - i.width) / 2 + "px";
            g = (this.height - i.height) * (this.value - this.minValue) / h + "px"
        } else {
            d = (this.width - i.width) * (this.value - this.minValue) / h + "px";
            g = (this.height - i.width) / 2 + "px"
        }
        this.button.style.top = g;
        this.button.style.left = d;
        if (this.callback && !f) {
            var a = this.callback(this.value / this.increment);
            if (!a) {}
        }
    }
};

function MapControl(a) {
    this.map = a;
    this.slider = null;
    this.createContainer = function(e, g, d, f, c, b) {
        return SD.util.createDiv("", e, g, d, f, "absolute", c, b)
    };
    this.createControl = function(c, e, d) {
        var b = SD.util.createImg("", c, e + "px", d + "px", "", "", "absolute");
        b.style.cursor = "pointer";
        b.map = this.map;
        b.control = this;
        return b
    };
    this.getSpriteButton = function(b, h, g, d, f) {
        var c = document.createElement("div");
        if (SD.isIE && !SD.isIE7 && !SD.isIE8) {
            c.style.cssText = "position:" + b + "; left:" + h.x + "px;top:" + h.y + "px;width:" + d.w + "px; height:" + d.h + "px; overflow:hidden;";
            var e = document.createElement("div");
            e.style.cssText = "FILTER:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + SD.IMG_URL + "map13.png'); position: absolute; top: " + g.y + "px;left: " + g.x + "px; height: 314px; width:325px;";
            c.appendChild(e);
            c.setBackgroundPosition = function(i) {
                e.style.top = i.y + "px";
                e.style.left = i.x + "px"
            }
        } else {
            c.style.cssText = "position:" + b + ";left:" + h.x + "px;top:" + h.y + "px;background-position:" + g.x + "px " + g.y + "px;background-image:url(" + SD.IMG_URL + "map13.png);width:" + d.w + "px; height:" + d.h + "px;" + (f != undefined ? "cursor:pointer;" : "");
            c.setBackgroundPosition = function(i) {
                this.style.backgroundPosition = i.x + "px " + i.y + "px"
            }
        }
        return c
    };
    this.setOpacity = function(c, b) {
        c.style.opacity = b / 10;
        c.style.filter = "alpha(opacity = " + (b * 10) + ")"
    };
    this.getDirection = function() {
        var e = this.map.size.width / 3;
        var f = {
            x: -185,
            y: -48
        };
        var d = {
            x: -185,
            y: -5
        };
        var c = this.getSpriteButton("relative", {
            x: 7,
            y: 0
        }, f, {
            w: 44,
            h: 44
        });
        var i = document.createElement("div");
        i.style.cssText = "position: absolute;left:15px;top:0px;width:15px;height:18px;cursor:pointer;";
        var g = document.createElement("div");
        g.style.cssText = "position: absolute;left:15px;top:25px;width:15px;height:18px;cursor:pointer;";
        var j = document.createElement("div");
        j.style.cssText = "position: absolute;left:0px;top:14px;width:18px;height:15px;cursor:pointer;";
        var h = document.createElement("div");
        h.style.cssText = "position: absolute;left:25px;top:14px;width:18px;height:15px;cursor:pointer;";
        EventManager.add(c, "mouseover", function() {
            c.setBackgroundPosition(d)
        });
        EventManager.add(c, "mouseout", function() {
            c.setBackgroundPosition(f)
        });
        var b = this.map;
        EventManager.add(i, "click", function() {
            b.panBy(0, -(b.size.height / 3))
        });
        EventManager.add(j, "click", function() {
            b.panBy(-e, 0)
        });
        EventManager.add(h, "click", function() {
            b.panBy(e, 0)
        });
        EventManager.add(g, "click", function() {
            b.panBy(0, (b.size.height / 3))
        });
        c.appendChild(i);
        c.appendChild(g);
        c.appendChild(j);
        c.appendChild(h);
        return c
    };
    this.getZoomControl = function() {
        var b = new SD.util.createDiv("", "20px", "10px", "20px", "40px", "relative");
        var c = this.getSpriteButton("absolute", {
            x: 2,
            y: 18
        }, {
            x: -56,
            y: -164
        }, {
            w: 14,
            h: 13
        }, true);
        var e = this.getSpriteButton("absolute", {
            x: 2,
            y: 0
        }, {
            x: -39,
            y: -164
        }, {
            w: 14,
            h: 13
        }, true);
        this.setOpacity(c, 4);
        this.setOpacity(e, 4);
        var d = this;
        EventManager.add(c, "mouseover", function() {
            d.setOpacity(c, 10)
        });
        EventManager.add(c, "mouseout", function() {
            d.setOpacity(c, 4)
        });
        EventManager.add(e, "mouseover", function() {
            d.setOpacity(e, 10)
        });
        EventManager.add(e, "mouseout", function() {
            d.setOpacity(e, 4)
        });
        EventManager.add(c, "click", function() {
            d.map.viewport.zoomOut()
        });
        EventManager.add(e, "click", function() {
            d.map.viewport.zoomIn()
        });
        b.appendChild(c);
        b.appendChild(e);
        return b
    };
    this.getLevelControl = function() {
        var b = this;
        var j = new SD.util.createDiv("", "2px", "10px", "30px", "120px", "relative", 11);
        var l = {
            x: -249,
            y: 0
        };
        var d = {
            x: -287,
            y: 0
        };
        var f = this.getSpriteButton("absolute", {
            x: 9,
            y: 0
        }, d, {
            w: 38,
            h: 308
        }, true);
        var c = this.getSpriteButton("absolute", {
            x: 11,
            y: 35
        }, {
            x: -56,
            y: -164
        }, {
            w: 14,
            h: 13
        }, true);
        var e = this.getSpriteButton("absolute", {
            x: 11,
            y: 288
        }, {
            x: -39,
            y: -164
        }, {
            w: 14,
            h: 13
        }, true);
        EventManager.add(c, "click", function() {
            b.map.zoomOut()
        });
        EventManager.add(e, "click", function() {
            b.map.zoomIn()
        });
        this.setOpacity(c, 4);
        this.setOpacity(e, 4);
        f.appendChild(c);
        f.appendChild(e);
        var i = {
            x: -73,
            y: -164
        };
        var k = {
            x: -91,
            y: -164
        };
        var h = this.getSpriteButton("absolute", {
            x: 10,
            y: 0
        }, k, {
            w: 18,
            h: 13
        });
        this.slider = new MapSlider({
            renderTo: f,
            button: h,
            events: [{
                obj: f,
                type: "mouseover",
                callback: function() {
                    b.setOpacity(c, 10);
                    b.setOpacity(e, 10);
                    h.setBackgroundPosition(i);
                    f.setBackgroundPosition(l)
                }
            }, {
                obj: f,
                type: "mouseout",
                callback: function() {
                    b.setOpacity(c, 4);
                    b.setOpacity(e, 4);
                    h.setBackgroundPosition(k);
                    f.setBackgroundPosition(d)
                }
            }],
            width: 38,
            height: 230,
            position: {
                top: 53,
                left: 0
            },
            vertical: true,
            increment: 18,
            minValue: 17,
            maxValue: 230,
            map: this.map,
            viewport: this.map.viewport,
            callback: function(m) {
                if (m != this.map.zoom) {
                    this.map.setZoom(m, true)
                }
            }
        });
        this.slider.init();
        this.slider.setFromWheel(this.map.zoom);
        var g = this.slider;
        this.map.viewport.OnLevelChanged.register(function(m) {
            g.setFromWheel(m.levelIndex, true)
        }, this.slider);
        j.appendChild(f);
        return j
    };
    this.getOverviewControl = function(b) {
        var c = new ViewportControlMini(this.map.viewport, b);
        c.draw();
        return c.getPanel()
    };
    this.getSelectedController = function(c, b) {
        if (c == undefined) {
            return false
        }
        for (var d = 0; d < c.length; d++) {
            if (d == b) {
                c[d].style.border = "1px solid #000"
            } else {
                c[d].style.border = ""
            }
        }
    };
    this.getDrawControl = function() {
        var b = document.createElement("div");
        b.style.cssText = "position:absolute; left:0px; bottom:0px; width:90px; height:25px; border:1px solid brown;";
        var e = [];
        e[0] = this.createControl("http://x1.sdimgs.com/img/draw-text.png", 5, 5);
        e[1] = this.createControl("http://x1.sdimgs.com/img/draw-circles.png", 25, 5);
        e[2] = this.createControl("http://x1.sdimgs.com/img/draw-poly.png", 45, 5);
        e[3] = this.createControl("http://x1.sdimgs.com/img/draw-polyline.png", 65, 5);
        var c = new DrawingManager({
            map: this.map
        });
        for (var d = 0; d < e.length; d++) {
            b.appendChild(e[d]);
            e[d].index = d;
            EventManager.add(e[d], "click", function() {
                this.control.getSelectedController(e, this.index);
                c.setActive(this.index)
            })
        }
        return b
    };
    this.getTransparentControl = function() {
        var b = this;
        var e = "40px";
        if (this.map.navigation.length > 0) {
            if (this.map.navigation[0].constructor.name == "MediumMapControl") {
                e = "130px"
            } else {
                if (this.map.navigation[0].constructor.name == "CompleteMapControl") {
                    e = "410px"
                }
            }
        }
        var d = new SD.util.createDiv("", "17px", e, "24px", "24px", "relative");
        var c = document.createElement("div");
        c.style.cssText = "background-image:url(" + SD.IMG_URL + "transparent_button.gif); position:absolute; left:0px; top:0px; width:24px; height:24px; overflow:hidden; cursor:pointer;";
        c.onclick = function() {
            b.showTransparentLayer(this, 1)
        };
        d.appendChild(c);
        return d
    };
    this.showTransparentLayer = function(d, b) {
        var c = this;
        if (b == 1) {
            this.map.viewport.mapControl.style.backgroundColor = "#000000";
            this.map.viewport.mapContainer.div.style.opacity = 0.4;
            if (d) {
                d.style.backgroundPosition = "-24px 0px";
                d.onclick = function() {
                    c.showTransparentLayer(this, 0)
                }
            }
        } else {
            this.map.viewport.mapControl.style.backgroundColor = "#CCFFCC";
            this.map.viewport.mapContainer.div.style.opacity = 1;
            if (d) {
                d.style.backgroundPosition = "0px 0px";
                d.onclick = function() {
                    c.showTransparentLayer(this, 1)
                }
            }
        }
    }
}
MapControl.instance = [];
MapControl.getInstance = function(b, c) {
    var a = (c.div ? c.div.id : "") || c.id || Math.round(Math.random() * 100);
    if (MapControl.instance[a] == null || !(MapControl.instance[a] instanceof MapControl)) {
        MapControl.instance[a] = new MapControl(b)
    }
    return MapControl.instance[a]
};

function MediumMapControl(a) {
    this.control = null;
    this.controls = [];
    this.getNavigation = function() {
        var b = new SD.util.createDiv("", "0px", "40px", "50px", "100px", "absolute", 101);
        this.controls.push(this.control.getDirection());
        this.controls.push(this.control.getZoomControl());
        b.appendChild(this.controls[0]);
        b.appendChild(this.controls[1]);
        return b
    };
    this.setDisplay = function(c, b) {
        if (this.controls[c] != null) {
            this.controls[c].style.display = b ? "" : "none"
        }
    }
}

function CompleteMapControl(a) {
    this.control = null;
    this.controls = [];
    this.getNavigation = function() {
        var b = new SD.util.createDiv("", "0px", "40px", "50px", "321px", "absolute", 11);
        this.controls.push(this.control.getDirection());
        this.controls.push(this.control.getLevelControl());
        b.appendChild(this.controls[0]);
        b.appendChild(this.controls[1]);
        return b
    };
    this.setDisplay = function(c, b) {
        if (this.controls[c] != null) {
            this.controls[c].style.display = b ? "" : "none"
        }
    }
}

function TransparentMapControl() {
    this.control = null;
    this.getNavigation = function() {
        return this.control.getTransparentControl()
    }
}

function OverviewMapControl(a) {
    this.control = null;
    this.size = a;
    this.getNavigation = function() {
        return this.control.getOverviewControl(this.size)
    }
}

function DrawingMapControl() {
    this.control = null;
    this.getNavigation = function() {
        return this.control.getDrawControl()
    }
};
SD.drawing.util = {
    LineSegment: function(d, c) {
        this.p0 = d;
        this.p1 = c;
        this.distance = function(a) {
            return this.distancePointLine(a, this.p0, this.p1)
        };
        this.distancePtoP = function(g, e) {
            var h = g.x - e.x;
            var f = g.y - e.y;
            return Math.sqrt(h * h + f * f)
        };
        this.distancePointLine = function(f, a, g) {
            if (a.x == g.x && a.y == g.y) {
                return this.distancePtoP(f, a)
            }
            var e = ((f.x - a.x) * (g.x - a.x) + (f.y - a.y) * (g.y - a.y)) / ((g.x - a.x) * (g.x - a.x) + (g.y - a.y) * (g.y - a.y));
            if (e <= 0) {
                return this.distancePtoP(f, a)
            }
            if (e >= 1) {
                return this.distancePtoP(f, g)
            }
            var b = ((a.y - f.y) * (g.x - a.x) - (a.x - f.x) * (g.y - a.y)) / ((g.x - a.x) * (g.x - a.x) + (g.y - a.y) * (g.y - a.y));
            return Math.abs(b) * Math.sqrt(((g.x - a.x) * (g.x - a.x) + (g.y - a.y) * (g.y - a.y)))
        };
        this.distanceToPolyline = function(e, b) {
            if (e.length < 2) {
                if (e.length == 1) {
                    return this.distancePtoP(b, e[0])
                }
                return false
            }
            var a = 1000;
            var g = 0;
            for (var f = 0; f < e.length - 1; f++) {
                g = this.distancePointLine(b, e[f], e[f + 1]);
                if (g < a) {
                    a = g
                }
            }
            return a
        }
    },
    DPSimplifier: function(b, a) {
        this.pts = b;
        this.usePt = [];
        this.seg = new SD.drawing.util.LineSegment();
        this.distanceTolerance = a;
        this.simplify = function() {
            for (var d = 0; d < this.pts.length; d++) {
                this.usePt[d] = true
            }
            this.simplifySection(0, this.pts.length - 1);
            var c = new Array();
            for (var d = 0; d < this.pts.length; d++) {
                if (this.usePt[d]) {
                    c.push(this.pts[d])
                }
            }
            return c
        };
        this.simplifySection = function(f, d) {
            if ((f + 1) == d) {
                return
            }
            this.seg.p0 = this.pts[f];
            this.seg.p1 = this.pts[d];
            var g = -1,
                e = f;
            for (var c = f + 1; c < d; c++) {
                var h = this.seg.distance(this.pts[c]);
                if (h > g) {
                    g = h;
                    e = c
                }
            }
            if (g <= this.distanceTolerance) {
                for (var c = f + 1; c < d; c++) {
                    this.usePt[c] = false
                }
            } else {
                this.simplifySection(f, e);
                this.simplifySection(e, d)
            }
        }
    },
    IntersectionRectangleRectangle: function(j, a) {
        var i = new Point(j.left, j.top);
        var g = new Point(j.right, j.bottom);
        var b = new Point(j.right, j.top);
        var h = new Point(j.left, j.bottom);
        var f = SD.drawing.util.IntersectionLineRectangle(i, b, a);
        var e = SD.drawing.util.IntersectionLineRectangle(b, g, a);
        var d = SD.drawing.util.IntersectionLineRectangle(h, g, a);
        var c = SD.drawing.util.IntersectionLineRectangle(g, i, a);
        var k = {
            status: "No Intersection",
            hit: 0
        };
        k.hit += f.hit;
        k.hit += e.hit;
        k.hit += d.hit;
        k.hit += c.hit;
        if (k.hit > 0) {
            k.status = "Intersection"
        }
        return k
    },
    IntersectionLineRectangle: function(b, a, k) {
        var j = new Point(k.left, k.top);
        var h = new Point(k.right, k.bottom);
        var c = new Point(k.right, k.top);
        var i = new Point(k.left, k.bottom);
        var g = SD.drawing.util.IntersectionLineLine(j, c, b, a);
        var f = SD.drawing.util.IntersectionLineLine(c, h, b, a);
        var e = SD.drawing.util.IntersectionLineLine(j, i, b, a);
        var d = SD.drawing.util.IntersectionLineLine(i, h, b, a);
        var l = {
            status: "No Intersection",
            hit: 0
        };
        l.hit += g.hit;
        l.hit += f.hit;
        l.hit += e.hit;
        l.hit += d.hit;
        if (l.hit > 0) {
            l.status = "Intersection"
        }
        return l
    },
    IntersectionLineLine: function(e, c, i, h) {
        var j = {
            status: "",
            hit: 0
        };
        var f = (h.x - i.x) * (e.y - i.y) - (h.y - i.y) * (e.x - i.x);
        var g = (c.x - e.x) * (e.y - i.y) - (c.y - e.y) * (e.x - i.x);
        var d = (h.y - i.y) * (c.x - e.x) - (h.x - i.x) * (c.y - e.y);
        if (d != 0) {
            var b = f / d;
            var a = g / d;
            if (0 <= b && b <= 1 && 0 <= a && a <= 1) {
                j.status = "Intersection";
                j.hit++
            } else {
                j.status = "No Intersection"
            }
        } else {
            if (f == 0 || g == 0) {
                j.status = "Coincident"
            } else {
                j.status = "Parallel"
            }
        }
        return j
    }
};
SD.shape.Polyline = function(a, b) {
    this.name = "";
    this.map = null;
    this.projection = null;
    this.centerGeo = new GeoPoint();
    this.centerMetric = new Vertex();
    this.boundScreen = false;
    this.boundMetric = new Rectangle();
    this.boundGeo = new Rectangle();
    this.bounds = new Rectangle();
    this.wbound = new Rectangle();
    this.points = a;
    this.useMapProjection = false;
    this.useGeo = false;
    this._simplifier = new SD.drawing.util.DPSimplifier();
    this._canvas = null;
    this._polyline = null;
    this.hideOnLevel = [];
    SD.apply(this, b);
    SD.apply(this, new StdLayer());
    if (this.projection == null) {
        this.useMapProjection = true;
        this.useGeo = true
    }
    if (this.map != null) {
        this._canvas = new DrawingVector(this.div, this.map.size.width, this.map.size.height);
        this._polyline = new PolylineVector(this._canvas);
        this.map.viewport.vectorLayer.addNode(this);
        this.map.pushElement(this);
        if (this.points != null && this.points.length != undefined) {
            this.getBounds(this.map.canvasInfo);
            this.draw(this.map.canvasInfo)
        }
    }
};
SD.shape.Polyline.prototype = {
    convertPoints: function(c, a) {
        var d = [];
        for (var b = 0; b < this.points.length; b++) {
            d.push(a ? new c(this.points[b].y, this.points[b].x) : new c(this.points[b].x, this.points[b].y))
        }
        return d
    },
    setPoints: function(a) {
        this.points = a;
        this.resetBounds();
        this.getBounds(null)
    },
    draw: function(b) {
        if (b == null) {
            b = this.map.canvasInfo
        } else {
            this.map.canvasInfo = b
        }
        if (b.projection == undefined) {
            return
        }
        if (this.hideOnLevel) {
            for (var a = 0, e = this.hideOnLevel.length; a < e; a++) {
                if (b.levelIndex == this.hideOnLevel[a]) {
                    this.setDisplay(false);
                    return
                }
            }
        }
        this.projection = this.useMapProjection ? b.projection : this.projection;
        var c = (!this.useMapProjection && this.projection.name == b.projection.name) || this.useMapProjection;
        if (c && (this.points != null && this.points.length != undefined)) {
            this.updateView(b);
            this.generateVector(b);
            this.setDisplay(true)
        } else {
            this.setDisplay(false)
        }
    },
    update: function(a) {},
    updateView: function(d) {
        if (this._polyline) {
            this._polyline.clear()
        }
        var g = this.getMetricBounds(d);
        var a, e, h = 10,
            c = this.projection.metricToScreen;
        if (this.useGeo) {
            c = this.projection.geoToScreen
        }
        a = c.call(this.projection, g.left, g.top, d.scale, d.topLeftOverlay);
        e = c.call(this.projection, g.right, g.bottom, d.scale, d.topLeftOverlay);
        var f = new Rectangle(a.x - h, a.y - h, e.x + h, e.y + h);
        var b = new Size(f.width(), parseInt(f.height()));
        if (b.width > 0 && b.height > 0) {
            this._canvas.setSize(b)
        }
        if (f.left != 0 || f.top != 0) {
            this._canvas.setPosition(f.top, f.left)
        }
        this.boundScreen = f
    },
    generateVector: function(b) {
        this._canvas.clear();
        this._polyline.clearArrow();
        var n, h = new Vertex(0, 0),
            a = new Point();
        var m = [];
        if (this.points != null && this.points != undefined) {
            this._simplifier.pts = this.points;
            this._simplifier.distanceTolerance = this.useGeo ? (b.scale / 30000) : b.scale / 2;
            m = this._simplifier.simplify()
        }
        var g = 55,
            j = [];
        var c = this.projection.metricToScreen;
        if (this.useGeo) {
            c = this.projection.geoToScreen
        }
        var l = {
            x: b.topLeftOverlay.x + this.boundScreen.left,
            y: b.topLeftOverlay.y + this.boundScreen.top
        };
        for (var d = 0, f = m.length; d < f; d++) {
            if (m[d].x == undefined || m[d].y == undefined || (h.x == m[d].x && h.y == m[d].y)) {
                continue
            }
            n = c.call(this.projection, m[d].x, m[d].y, b.scale, l);
            if (!isNaN(n.x) && !isNaN(n.y)) {
                j.push(n);
                if (this.arrowOption != undefined && this.arrowOption && d > 0) {
                    var k = new Point(n.x - a.x, n.y - a.y);
                    var e = Math.sqrt(Math.pow(k.x, 2) + Math.pow(k.y, 2));
                    if (e >= g) {
                        this._polyline.addArrow(a, n, this.arrowOption)
                    }
                }
            }
            h = m[d];
            a = n
        }
        this._polyline.init(j, this)
    },
    isInBoundary: function(b) {
        if (isNaN(this.boundGeo.left)) {
            return true
        }
        var a = SD.drawing.util.IntersectionRectangleRectangle(this.boundGeo, b.geoView);
        if (a.hit > 0 || (this.isInBounds(this.centerGeo, b.geoView) || this.isInBounds(b.centerGeo, this.boundGeo))) {
            this.setDisplay(true);
            return true
        }
        this.setDisplay(false);
        return false
    },
    isInBounds: function(a, b) {
        if (b.top >= a.lat && b.bottom <= a.lat && b.left <= a.lon && b.right >= a.lon) {
            return true
        }
        return false
    },
    resetBounds: function() {
        this.boundMetric.right = 0;
        this.scale = -1
    },
    getMetricBounds: function(a) {
        this.bounds = this.boundMetric;
        return this.boundMetric
    },
    getBounds: function(c) {
        if ((this.boundMetric.right == 0 || this.boundMetric.right == undefined) && this.points != null) {
            for (var b = 0, d = this.points.length; b < d; b++) {
                if (b == 0) {
                    this.boundMetric.left = parseFloat(this.points[b].x);
                    this.boundMetric.right = parseFloat(this.points[b].x);
                    this.boundMetric.top = parseFloat(this.points[b].y);
                    this.boundMetric.bottom = parseFloat(this.points[b].y)
                }
                if (parseFloat(this.points[b].x) > this.boundMetric.right) {
                    this.boundMetric.right = parseFloat(this.points[b].x)
                }
                if (parseFloat(this.points[b].x) < this.boundMetric.left) {
                    this.boundMetric.left = parseFloat(this.points[b].x)
                }
                if (parseFloat(this.points[b].y) > this.boundMetric.top) {
                    this.boundMetric.top = parseFloat(this.points[b].y)
                }
                if (parseFloat(this.points[b].y) < this.boundMetric.bottom) {
                    this.boundMetric.bottom = parseFloat(this.points[b].y)
                }
            }
            var a, e;
            if (this.useGeo) {
                a = {
                    lon: this.boundMetric.left,
                    lat: this.boundMetric.top
                };
                e = {
                    lon: this.boundMetric.right,
                    lat: this.boundMetric.bottom
                }
            } else {
                a = this.projection.metricToGeo(this.boundMetric.left, this.boundMetric.top);
                e = this.projection.metricToGeo(this.boundMetric.right, this.boundMetric.bottom)
            }
            this.centerGeo.lon = a.lon + ((e.lon - a.lon) / 2);
            this.centerGeo.lat = a.lat + ((e.lat - a.lat) / 2);
            this.centerMetric.x = this.boundMetric.left + ((this.boundMetric.right - this.boundMetric.left) / 2);
            this.centerMetric.y = this.boundMetric.top + ((this.boundMetric.bottom - this.boundMetric.top) / 2);
            this.boundGeo.left = a.lon;
            this.boundGeo.top = a.lat;
            this.boundGeo.right = e.lon;
            this.boundGeo.bottom = e.lat
        }
        return this.boundMetric
    },
    setOptions: function(a) {
        this._polyline.setOptions(a);
        if (!SD.isIE && a.transform) {
            if (a.transform.scale && a.transform.offset) {
                if (a.transform.scale == 1 && a.transform.offset.x == 0 && a.transform.offset == 0) {
                    this.setUnTransform(scale, offset)
                } else {
                    this.setTransform(a.transform.scale, a.transform.offset)
                }
            }
        }
    }
};
SD.shape.Geofence = function(a) {
    this.center = null;
    this.map = null;
    this.projection = null;
    this.text = a.radius + " m";
    this.centerMetric = new Vertex();
    this.boundGeo = new Rectangle();
    this.boundMetric = new Rectangle();
    this.scaleDiameter = 0;
    this.radius = a.radius;
    this.useMapProjection = false;
    SD.apply(this, a);
    SD.apply(this, new StdLayer());
    this.points = [new Vertex(this.center.lon, this.center.lat)];
    if (this.map != null) {
        this._canvas = new DrawingVector(this.div, this.map.size.width, this.map.size.height);
        this.map.viewport.vectorLayer.addNode(this);
        this.draw(this.map.canvasInfo)
    }
};
SD.extend(SD.shape.Geofence, SD.shape.Polyline);
SD.shape.Geofence.prototype.update = function() {};
SD.shape.Geofence.prototype.getMetricBounds = function(b) {
    this.scaleDiameter = Math.abs(this.radius / b.scale);
    if (this.boundGeo.left == 0 || this.boundGeo.left == undefined) {
        var c = this.projection.inflateGeo(this.boundGeo, -this.scaleDiameter, -this.scaleDiameter, b.scale);
        var a = this.projection.inflateGeo(this.boundGeo, this.scaleDiameter, this.scaleDiameter, b.scale);
        this.boundGeo = new Rectangle(c.lon, c.lat, a.lon, a.lat)
    }
    this.centerMetric = this.projection.geoToMetric(this.center.lon, this.center.lat);
    c = this.projection.inflateVert(this.centerMetric, -this.scaleDiameter, -this.scaleDiameter, b.scale);
    a = this.projection.inflateVert(this.centerMetric, this.scaleDiameter, this.scaleDiameter, b.scale);
    this.boundMetric = new Rectangle(c.x, c.y, a.x, a.y);
    return this.boundMetric
};
SD.shape.Geofence.prototype.generateVector = function(a) {
    this._canvas.clear();
    var b = this.projection.metricToScreen(this.centerMetric.x, this.centerMetric.y, a.scale, a.topLeftOverlay);
    this.diameter = this.scaleDiameter;
    this._canvas.createArrow(b, this);
    this._canvas.createCircle(b, this);
    this._canvas.createText(b, this)
};
SD.shape.Geofence.prototype.updateView = function(d) {
    if (this._polyline) {
        this._polyline.clear()
    }
    var g = this.getMetricBounds(d);
    var a, e, h = 0,
        c = this.projection.metricToScreen;
    if (this.useGeo) {
        c = this.projection.geoToScreen
    }
    a = c.call(this.projection, g.left, g.top, d.scale, d.topLeftOverlay);
    e = c.call(this.projection, g.right, g.bottom, d.scale, d.topLeftOverlay);
    var f = new Rectangle(a.x - h, a.y - h, e.x + h, e.y + h);
    var b = new Size(f.width(), f.height());
    this._canvas.setViewBox(f, this.size);
    if (b.width > 0 && b.height > 0) {
        this._canvas.setSize(b, true)
    }
    if (f.left != 0 || f.top != 0) {
        this._canvas.setPosition(f.top, f.left)
    }
    this.boundScreen = f
};
SD.mgr.__geofence = {
    i: 0,
    a: []
};
SD.mgr.Geofence = function(a) {
    this.map = null;
    this.projection = (new SD.projection.Server()).get("UTM WGS-1984 48N");
    SD.apply(this, new SD.genmap.OverlayManager());
    SD.apply(this, a);
    this.add = function(b) {
        b.map = this.map;
        b.projection = this.projection;
        b.useMapProjection = true;
        var c = new SD.shape.Geofence(b);
        this._add(c);
        return c
    };
    this.remove = function(b) {
        this._remove(b);
        this.map.viewport.vectorLayer.removeNode(b)
    }
};
SD.genmap.GeofenceManager = function(b) {
    var a = new SD.mgr.Geofence(b);
    SD.mgr.__geofence.i++;
    SD.mgr.__geofence.a.push(a);
    return a
};
SD.mgr.__polyline = {
    i: 0,
    a: []
};
SD.mgr.Polyline = function(a) {
    this.map = null;
    this.projection = (new SD.projection.Server()).get("UTM WGS-1984 48N");
    SD.apply(this, new SD.genmap.OverlayManager());
    SD.apply(this, a);
    this.add = function(b, c) {
        c.map = this.map;
        var d = new SD.shape.Polyline(b, c);
        this._add(d);
        return d
    };
    this.remove = function(b) {
        this._remove(b);
        this.map.viewport.vectorLayer.removeNode(b)
    }
};
SD.genmap.PolylineManager = function(b) {
    var a = new SD.mgr.Polyline(b);
    SD.mgr.__polyline.i++;
    SD.mgr.__polyline.a.push(a);
    return a
};
SD.shape.Ellipse = function(a, b) {
    this.position = a;
    this.map = null;
    this.projection = null;
    this._canvas = null;
    SD.apply(this, b);
    SD.apply(this, new StdLayer());
    if (this.map != null) {
        this._canvas = new DrawingVector(this.div, this.map.size.width, this.map.size.height);
        this.map.viewport.vectorLayer.addNode(this);
        this.draw(this.map.canvasInfo)
    }
};
SD.shape.Ellipse.prototype = {
    setPosition: function(a) {
        this.position = a
    },
    draw: function(a) {
        if (a == null) {
            a = this.map.canvasInfo
        } else {
            this.map.canvasInfo = a
        }
        if (this.projection.name == a.projection.name) {
            this.generateVector(a)
        } else {
            this.setDisplay(false)
        }
    },
    generateVector: function(a) {
        this._canvas.clear();
        var b = this.projection.metricToScreen(this.position.x, this.position.y, a.scale, a.topLeftOverlay);
        this._canvas.createCircle(b, this.options)
    }
};
SD.extend(SD.shape.Ellipse, SD.shape.Polyline);
SD.genmap.MarkerImage = function(a) {
    this.image = SD.BASE_URL + "icon.php";
    this.title = "";
    this.pt = new Point(0, 0);
    this.iconSize = new Size(19, 32);
    this.iconAnchor = new Point(9, 34);
    this.infoWindowAnchor = new Point(9, 35);
    SD.apply(this, a);
    this.object = "";
    this.getObject = function(b) {
        if (this.object == "") {
            this.object = document.createElement("img");
            this.object.style.width = this.iconSize.width + "px";
            this.object.style.height = this.iconSize.height + "px";
            this.object.style.position = "absolute";
            this.object.style.cursor = "pointer";
            this.object.src = this.image;
            if (this.title != "") {
                this.object.alt = this.title;
                this.object.title = this.title
            }
        }
        if (b > 0) {
            this.object.style.zIndex = b
        }
        return this.object
    }
};
SD.genmap.MarkerImage.prototype = {
    setIndex: function(a) {
        this.object.style.zIndex = a
    },
    setImage: function(a) {
        this.object.src = a
    },
    setPoint: function(a) {
        this.setPosition(a)
    },
    setOffset: function(b) {
        this.pt.x += b.x;
        this.pt.y += b.y;
        var a = this.getObject();
        a.style.left = this.pt.x + "px";
        a.style.top = this.pt.y + "px"
    },
    getPosition: function() {
        return {
            x: this.pt.x + this.iconAnchor.x,
            y: this.pt.y + this.iconAnchor.y
        }
    },
    setPosition: function(b) {
        var a = this.getObject();
        this.pt.x = (b.x - this.iconAnchor.x);
        this.pt.y = (b.y - this.iconAnchor.y);
        a.style.left = this.pt.x + "px";
        a.style.top = this.pt.y + "px"
    },
    setDisplay: function(b) {
        var c = this.getObject();
        var a = b == true ? "" : "none";
        c.style.display = a
    }
};
SD.genmap.MarkerSprite = function(a) {
    this.__sprite = true;
    SD.apply(this, new SD.genmap.MarkerImage(a));
    this.getObject = function(d) {
        if (this.object == "") {
            var c = (this.cursor == undefined) ? "pointer" : this.cursor;
            var b = (this.useFilter == undefined) ? false : this.useFilter;
            if (b) {
                this.object = SD.util.createImgSprite(this.css, this.iconSize.width, this.iconSize.height, this.bgPosLeft, this.bgPosTop, this.iconAnchor.x, this.iconAnchor.y, "cursor: " + c, "", "", true)
            } else {
                this.object = SD.util.createImgSprite(this.css, this.iconSize.width, this.iconSize.height, this.bgPosLeft, this.bgPosTop, this.iconAnchor.x, this.iconAnchor.y, "cursor: " + c)
            }
            if (this.title != "") {
                this.object.alt = this.title;
                this.object.title = this.title
            }
        }
        if (d > 0) {
            this.object.style.zIndex = d
        }
        return this.object
    }
};
SD.genmap.MarkerPhoto = function(a) {
    SD.apply(this, new SD.genmap.MarkerImage(a));
    this.getObject = function(e) {
        if (this.object == "") {
            var b = this.iconSize.width,
                d = this.iconSize.height;
            this.object = document.createElement("div");
            this.object.id = "bldg_img" + this.elm_id;
            var c = document.createElement("img");
            this.object.appendChild(c);
            c.style.width = b;
            c.style.height = d;
            c.title = this.alt;
            c.style.position = "absolute";
            c.src = this.image;
            this.object.style.width = b;
            this.object.style.height = d;
            this.object.style.padding = "2px";
            this.object.style.position = "absolute";
            this.object.style.cursor = "pointer";
            if (a.background != "empty" || a.background == "") {
                this.object.style.backgroundColor = "#ffffff";
                this.object.style.border = "1px #777777 solid"
            }
            if (this.title != "") {
                this.object.alt = this.title;
                this.object.title = this.title
            }
        }
        if (e > 0) {
            this.object.style.zIndex = e
        }
        return this.object
    }
};
SD.genmap.MarkerStatic = function(c) {
    if (c == null) {
        return
    }
    this.map = null;
    this.icon = new SD.genmap.MarkerImage();
    this.position = null;
    this.positionPt = null;
    this.projection = null;
    this.draggable = false;
    this.visible = true;
    this.hideOnLevel = [];
    this.zIndex = 1;
    this.div = null;
    this.b = false;
    this.useMapProjection = true;
    if (c.icon != undefined && typeof c.icon == "string") {
        var b = c.icon;
        c.icon = new SD.genmap.MarkerImage(c);
        c.icon.image = b
    } else {
        if (c.icon != undefined) {
            var d = SD.util.clone(c.icon);
            c.icon = d
        }
    }
    SD.apply(this, c);
    if (c.title) {
        this.icon.title = c.title
    }
    if (this.projection == null) {
        this.projection = this.map.viewportInfo.projection
    }
    if (this.div == null) {
        this.div = this.icon.getObject(this.zIndex);
        this.map.viewport.markerStaticLayer.addNode(this);
        this.draw(this.map.canvasInfo)
    }
    if (this.draggable) {
        var a = new DraggableTool();
        a.init(this, this.map.viewport, this.draggableMethod)
    }
};
SD.genmap.MarkerStatic.prototype = {
    replaceIcon: function(b) {
        var a = SD.util.clone(this);
        a.div = b.getObject(this.zIndex);
        this.map.viewport.markerStaticLayer.replaceNode(this, a);
        this.icon = b;
        this.div = a.div
    },
    getObject: function() {
        return this.icon.getObject()
    },
    getPtPosition: function() {
        return this.icon.getPosition()
    },
    getSize: function() {
        return this.icon.iconSize
    },
    updatePosition: function(b) {
        var c = this.getPtPosition();
        var a;
        if (this.position.lon || this.position.lat) {
            a = this.projection.screenToGeo(c.x, c.y, b.scale, b.topLeftOverlay);
            this.position = a
        } else {
            if (this.position.x || this.position.y) {
                a = this.projection.screenToMetric(c.x, c.y, b.scale, b.topLeftOverlay);
                this.position = a
            }
        }
    },
    setPosition: function(a) {
        if (a == null) {
            return
        }
        this.position = a;
        this.draw(this.map.canvasInfo)
    },
    setPositionByOffset: function(c) {
        if (c == null) {
            return
        }
        var a = this.map.viewport.projection.geoToScreen(this.position.lon, this.position.lat, this.map.viewportInfo.scale, this.map.viewportInfo.topLeftScreen);
        var b = this.map.viewport.projection.screenToGeo((a.x + c.x), (a.y + c.y), this.map.viewportInfo.scale, this.map.viewportInfo.topLeftScreen);
        this.setPosition(b)
    },
    setOffset: function(b, a) {
        this.icon.setOffset(b)
    },
    draw: function(b) {
        if (b != null && this.position != null) {
            if (b.projection == undefined) {
                return
            }
            for (var a = 0, e = this.hideOnLevel.length; a < e; a++) {
                if (b.levelIndex == this.hideOnLevel[a]) {
                    this.setDisplay(false);
                    return
                }
            }
            this.projection = this.useMapProjection ? b.projection : this.projection;
            var c = (!this.useMapProjection && this.projection.name == b.projection.name) || this.useMapProjection;
            if (c) {
                if (this.position.lon || this.position.lat) {
                    this.positionPt = this.projection.geoToScreen(this.position.lon, this.position.lat, b.scale, b.topLeftOverlay)
                } else {
                    if (this.position.x || this.position.y) {
                        this.positionPt = this.projection.metricToScreen(this.position.x, this.position.y, b.scale, b.topLeftOverlay)
                    }
                }
                if (this.positionPt != null && (this.positionPt.x || this.positionPt.y)) {
                    this.icon.setPosition(this.positionPt);
                    this.setDisplay(true);
                    return
                }
            }
        }
        this.setDisplay(false)
    },
    setEnable: function(a) {
        this.enable = a;
        if (this.div != null) {
            this.div.style.visibility = a ? "" : "hidden"
        }
        this.setDisplay(a)
    },
    setDisplay: function(a) {
        if (this.div != null) {
            this.visible = a;
            this.div.style.display = a ? "" : "none"
        }
    }
};
SD.mgr.Marker = function(a) {
    this.map = null;
    this.projection = (new SD.projection.Server()).get("Mercator WGS-1984");
    this.useMapProjection = true;
    SD.apply(this, new SD.genmap.OverlayManager());
    SD.apply(this, a);
    this.add = function(d) {
        SD.mgr.__marker.z++;
        d.map = this.map;
        d.projection = this.projection;
        d.useMapProjection = this.useMapProjection;
        d.guid = SD.mgr.__marker.z;
        var c = new SD.genmap.MarkerStatic(d);
        c.guid = SD.mgr.__marker.z;
        c.b = this.map.pushElement(c);
        this._add(c);
        return c
    };
    this.remove = function(c) {
        this._remove(c);
        this.map.removeElement(c);
        this.map.viewport.markerStaticLayer.removeNode(c)
    };
    this.clear = function() {
        this._clear()
    };
    this.setAutoAdjust = function(v) {
        var d = new Rectangle(0, 0, 0, 0);
        var t = new Rectangle(0, 0, 0, 0);
        var u, p, m = 0;
        if (v == undefined) {
            v = this.node[0].position.lon ? true : false
        }
        for (var l = 0, n = this.node.length; l < n; l++) {
            if (this.node[l].position == undefined) {
                continue
            }
            u = parseFloat(this.node[l].position.lon ? this.node[l].position.lon : this.node[l].position.x);
            p = parseFloat(this.node[l].position.lat ? this.node[l].position.lat : this.node[l].position.y);
            if (m == 0) {
                d.left = u;
                d.right = u;
                d.top = p;
                d.bottom = p
            }
            if (u > d.right) {
                d.right = u
            }
            if (u < d.left) {
                d.left = u
            }
            if (p < d.top) {
                d.top = p
            }
            if (p > d.bottom) {
                d.bottom = p
            }
            m++
        }
        var g = this.map.viewport.mapManager.layers,
            e, f = 1,
            s;
        var k = false;
        var o = {
            lon: (d.left + d.right) / 2,
            lat: (d.top + d.bottom) / 2
        };
        if (!v) {
            o = this.projection.metricToGeo(o.x, o.y)
        }
        var q = {
            width: this.map.viewportInfo.canvasSize.width / 2,
            height: this.map.viewportInfo.canvasSize.height / 2
        };
        for (l = g.length - 1; l >= 0; l--) {
            e = g[l];
            if (k) {
                break
            }
            if (e.length != undefined) {
                for (var h = 0; h < e.length; h++) {
                    if (!e[h].projection) {
                        continue
                    }
                    if (e[h].projection.name != this.projection.name) {
                        continue
                    }
                    s = b(q, o, e[h], d, t, v);
                    f = !s ? f : s;
                    k = s;
                    if (s) {
                        break
                    }
                }
            } else {
                if (typeof e == "object") {
                    if (!e.projection) {
                        continue
                    }
                    if (e.projection.name != this.projection.name) {
                        continue
                    }
                    s = b(q, o, e, d, t, v);
                    f = !s ? f : s;
                    k = s;
                    if (s) {
                        break
                    }
                }
            }
        }
        if (f > 0) {
            this.map.setCenter(o, f)
        }
    };
    var b = function(k, d, g, c, h, l) {
        var i = {
            x: k.width * g.scale,
            y: k.height * g.scale * -1
        };
        var f = g.projection.geoToMetric(d.lon, d.lat);
        h.left = f.x - i.x;
        h.right = f.x + i.x;
        h.top = f.y + i.y;
        h.bottom = f.y - i.y;
        if (l) {
            var j = g.projection.metricToGeo(h.left, h.top);
            var e = g.projection.metricToGeo(h.right, h.bottom);
            h.top = j.lat;
            h.left = j.lon;
            h.right = e.lon;
            h.bottom = e.lat
        }
        if (c.left > h.left && c.left < h.right && c.right > h.left && c.right < h.right && c.bottom < h.bottom && c.bottom > h.top && c.top < h.bottom && c.top > h.top) {
            return g.realLevel
        }
        return false
    }
};
SD.mgr.__marker = {
    i: 0,
    a: [],
    z: 0
};
SD.genmap.MarkerStaticManager = function(b) {
    var a = new SD.mgr.Marker(b);
    SD.mgr.__marker.a.push(a);
    SD.mgr.__marker.i++;
    return a
};
SD.util.createImgSprite = function(g, p, e, q, a, b, c, i, k, o, n) {
    n = (n == undefined) ? false : true;
    if (SD.isIE6 && !n) {
        var m = document.createElement("div");
        b = (b == undefined) ? "" : "left:" + b + "px;";
        c = (c == undefined) ? "" : "top:" + (c) + "px;";
        i = (i == undefined) ? "" : i;
        m.style.cssText = "position:absolute; " + b + c + i;
        var l = document.createElement("div");
        l.style.cssText = "width:" + p + "px; height:" + e + "px; position: relative; overflow:hidden;";
        var j = document.createElement("div");
        j.className = g;
        k = (k == undefined) ? 1000 : k;
        o = (o == undefined) ? 1000 : o;
        j.style.cssText = "width: " + k + "px; height: " + o + "px; position:absolute; left:" + (-q) + "px; top: " + (-a) + "px;";
        l.appendChild(j);
        m.appendChild(l);
        m.setClassName = function(d) {
            m.childNodes[0].childNodes[0].className = d
        };
        m.setBgPosition = function(f, d) {
            m.childNodes[0].childNodes[0].style.left = -f + "px";
            m.childNodes[0].childNodes[0].style.top = -d + "px"
        };
        m.setWidth = function(d) {
            m.childNodes[0].style.width = d + "px"
        };
        m.setHeight = function(d) {
            m.childNodes[0].style.height = d + "px"
        };
        m.setTopLeft = function(d, f) {
            m.style.top = f + "px";
            m.style.left = d + "px"
        };
        m.getTopLeft = function() {
            return m.style.left + " " + m.style.top
        };
        m.getBgPosition = function() {
            return m.childNodes[0].childNodes[0].style.left + " " + m.childNodes[0].childNodes[0].style.top
        };
        return m
    } else {
        var l = document.createElement("div");
        b = (b == undefined) ? "" : "left:" + b + "px;";
        c = (c == undefined) ? "" : "top:" + c + "px;";
        l.className = g;
        l.style.cssText = "background-position: " + (-q) + "px " + (-a) + "px;width:" + p + "px; height:" + e + "px; position:absolute;" + b + "" + c + i;
        l.setClassName = function(d) {
            l.className = d
        };
        l.setBgPosition = function(f, d) {
            l.style.backgroundPosition = (-f) + "px " + (-d) + "px"
        };
        l.setWidth = function(d) {
            l.style.width = d + "px"
        };
        l.setHeight = function(d) {
            l.style.height = d + "px"
        };
        l.setTopLeft = function(d, f) {
            l.style.top = f + "px";
            l.style.left = d + "px"
        };
        l.getBgPosition = function() {
            return l.style.backgroundPosition
        };
        l.getTopLeft = function() {
            return l.style.left + " " + l.style.top
        };
        return l
    }
};
SD.genmap.GInfoWindow = function(a) {
    this.marker = null;
    this.content = "";
    this.visible = true;
    this.size = new Size(200, 100);
    this.minSize = new Size(175, 80);
    SD.apply(this, new StdLayer("id_ginfowindow"));
    SD.apply(this, a);
    this.init();
    this.open = function(b, c) {
        this.visible = true;
        this.marker = b;
        this.content = c;
        this.divContent.innerHTML = c;
        this.draw(true)
    };
    this.close = function() {
        this.visible = false;
        this.setDisplay(false)
    };
    this.draw = function(b) {
        var f = this.marker instanceof SD.genmap.MarkerStatic;
        if (this.marker == null || (f && (!this.marker.visible || !this.visible))) {
            this.setDisplay(false);
            return
        }
        var c = this.getCorner();
        var g = {
            x: 0,
            y: 0
        };
        if (f) {
            g.x = this.marker.positionPt.x - this.marker.icon.infoWindowAnchor.x - c.x;
            g.y = this.marker.positionPt.y - this.marker.icon.infoWindowAnchor.y - c.y
        } else {
            if (this.marker instanceof Point) {
                g.x = this.marker.x - c.x;
                g.y = this.marker.y - c.y;
                this.marker.topLeftContainer = {
                    x: 0,
                    y: 0
                }
            }
        }
        this.setTopLeft(g);
        this.setDisplay(true);
        var e = {
                x: 0,
                y: 0
            },
            d = f ? this.marker.map : (this.map != undefined ? this.map : this.marker);
        if (b != true) {
            return
        }
        g = SD.util.offsetPoint(g, d.canvasInfo.topLeftContainer.x, d.canvasInfo.topLeftContainer.y);
        if (g.x < 0) {
            e.x = g.x
        }
        if (g.x + this.size.width > d.size.width) {
            e.x = -(d.size.width - (g.x + this.size.width)) + 20
        }
        if (g.y < 0) {
            e.y = g.y - 20
        }
        if (g.y + this.size.height + 70 > d.size.height) {
            e.y = g.y + this.size.height - d.size.height / 2
        }
        if (e.x != 0 || e.y != 0) {
            d.panBy(e.x, e.y)
        }
    };
    this.getCorner = function() {
        return new Point(Math.abs(this.size.width / 3), this.size.height + 65)
    }
};
SD.genmap.GInfoWindow.prototype.setSize = function(a, b) {
    this.size.width = a;
    this.size.height = b;
    this.validating();
    this.reloadUI()
};
SD.genmap.GInfoWindow.prototype.validating = function() {
    if (this.size.width < this.minSize.width) {
        this.size.width = this.minSize.width
    }
    if (this.size.height < this.minSize.height) {
        this.size.height = this.minSize.height
    }
};
SD.genmap.GInfoWindow.prototype.reloadUI = function() {
    this.tr.style.left = (this.size.width - 25) + "px";
    this.bl.style.top = (this.size.height - 25) + "px";
    this.br.style.left = (this.size.width - 25) + "px";
    this.br.style.top = (this.size.height - 25) + "px";
    this.c0.style.left = Math.floor(this.size.width / 3) + "px";
    this.c0.style.top = (this.size.height - 27) + "px";
    this.exBtn.style.left = (this.size.width - 20) + "px";
    this.div.style.width = this.size.width + "px";
    this.div.style.height = this.size.height + "px";
    var b = 2;
    var a = 24;
    this.tb.style.width = (this.size.width - 50) + "px";
    this.tb.style.height = "25px";
    this.mb.style.width = (this.size.width - b) + "px";
    this.mb.style.height = (this.size.height - 50) + "px";
    this.bb.style.top = (this.size.height - 25) + "px";
    this.bb.style.width = (this.size.width - 50) + "px";
    this.bb.style.height = a + "px";
    this.divContent.style.width = (this.size.width - 35) + "px";
    this.divContent.style.height = (this.size.height - 30) + "px"
};
SD.genmap.GInfoWindow.prototype.init = function() {
    this.validating();
    this.tl = SD.util.createInfoFrame(25, 25, 0, 0, -128, 0, "layer.png");
    this.tl.children[0].width = 187;
    this.tl.children[0].height = 96;
    this.tr = SD.util.createInfoFrame(25, 25, 0, 0, -153, 0, "layer.png");
    this.tr.children[0].width = 187;
    this.tr.children[0].height = 96;
    this.bl = SD.util.createInfoFrame(25, 25, 0, 0, -128, -25, "layer.png");
    this.bl.children[0].width = 187;
    this.bl.children[0].height = 96;
    this.br = SD.util.createInfoFrame(25, 25, 0, 0, -153, -25, "layer.png");
    this.br.children[0].width = 187;
    this.br.children[0].height = 96;
    this.c0 = SD.util.createInfoFrame(97, 96, 0, 0, 1, -3, "layer.png");
    this.c0.children[0].width = 187;
    this.c0.children[0].height = 96;
    this.exBtn = SD.util.createInfoFrame(15, 15, 0, 20, -109, -13, "layer.png");
    this.exBtn.children[0].width = 187;
    this.exBtn.children[0].height = 96;
    this.exBtn.style.cursor = "pointer";
    this.exBtn.style.zIndex = 20;
    var a = this;
    if (SD.isIphone) {
        EventManager.add(this.exBtn, "touchstart", function() {
            a.close()
        })
    } else {
        EventManager.add(this.exBtn, "click", function() {
            a.close()
        })
    }
    this.tb = document.createElement("div");
    this.tb.style.cssText = "border-top: 1px solid rgb(171, 171, 171); position: absolute; left: 25px; top: 0px; height: 25px; background-color: white;";
    this.mb = document.createElement("div");
    this.mb.style.cssText = "border-left: 1px solid rgb(171, 171, 171); border-right: 1px solid rgb(171, 171, 171); position: absolute; left: 0px; top: 25px; background-color: white;";
    this.bb = document.createElement("div");
    this.bb.style.cssText = "border-bottom: 1px solid rgb(171, 171, 171); position: absolute; left: 25px; background-color: white;";
    this.divContent = document.createElement("div");
    this.divContent.style.cssText = "position: absolute; left: 16px; top: 16px; z-index: 10;";
    this.divContent.innerHTML = this.content;
    this.div.appendChild(this.tl);
    this.div.appendChild(this.tr);
    this.div.appendChild(this.bl);
    this.div.appendChild(this.br);
    this.div.appendChild(this.tb);
    this.div.appendChild(this.mb);
    this.div.appendChild(this.bb);
    this.div.appendChild(this.c0);
    this.div.appendChild(this.exBtn);
    this.div.appendChild(this.divContent);
    this.div.style.position = "absolute";
    this.div.style.cursor = "default";
    EventManager.add(this.div, "mousedown", function(b) {
        SD.util.cancelEvent(b, true, true)
    });
    EventManager.add(this.div, "DOMMouseScroll", function(b) {
        b.cancelBubble = true;
        b.cancel = true
    });
    EventManager.add(this.div, "mousewheel", function(b) {
        b.cancelBubble = true;
        b.cancel = true
    });
    this.reloadUI();
    this.setDisplay(false)
};
SD.genmap.SDInfoWindow = function(a) {
    this.marker = null;
    this.content = "";
    this.visible = true;
    this.size = new Size(200, 100);
    this.minSize = new Size(175, 80);
    SD.apply(this, new StdLayer());
    SD.apply(this, a);
    this.init();
    this.open = function(b, c) {
        this.visible = true;
        this.marker = b;
        this.content = c;
        this.divContent.innerHTML = c;
        this.draw(true)
    };
    this.close = function() {
        this.visible = false;
        this.setDisplay(false)
    };
    this.draw = function(b) {
        var f = this.marker instanceof SD.genmap.MarkerStatic;
        if (this.marker == null || (f && (!this.marker.visible || !this.visible))) {
            this.setDisplay(false);
            return
        }
        var c = this.getCorner();
        var g = {
            x: 0,
            y: 0
        };
        if (f) {
            g.x = this.marker.positionPt.x - this.marker.icon.infoWindowAnchor.x - c.x;
            g.y = this.marker.positionPt.y - this.marker.icon.infoWindowAnchor.y - c.y
        } else {
            if (this.marker instanceof Point) {
                g.x = this.marker.x - c.x;
                g.y = this.marker.y - c.y;
                this.marker.topLeftContainer = {
                    x: 0,
                    y: 0
                }
            }
        }
        this.setTopLeft(g);
        this.setDisplay(true);
        var e = {
                x: 0,
                y: 0
            },
            d = f ? this.marker.map : (this.map != undefined ? this.map : this.marker);
        if (b != true) {
            return
        }
        g = SD.util.offsetPoint(g, d.canvasInfo.topLeftContainer.x, d.canvasInfo.topLeftContainer.y);
        if (g.x < 0) {
            e.x = g.x
        }
        if (g.x + this.size.width > d.size.width) {
            e.x = -(d.size.width - (g.x + this.size.width)) + 20
        }
        if (g.y < 0) {
            e.y = g.y - 20
        }
        if (g.y + this.size.height > d.size.height) {
            e.y = g.y + this.size.height - d.size.height / 2
        }
        if (e.x != 0 || e.y != 0) {
            d.panBy(e.x, e.y)
        }
    };
    this.getCorner = function() {
        return new Point(Math.abs(this.size.width / 2) - 10, this.size.height)
    }
};
SD.genmap.SDInfoWindow.prototype.validating = function() {
    if (this.size.width < this.minSize.width) {
        this.size.width = this.minSize.width
    }
    if (this.size.height < this.minSize.height) {
        this.size.height = this.minSize.height
    }
};
SD.genmap.SDInfoWindow.prototype.reloadUI = function() {
    this.tr.style.left = (this.size.width - 8) + "px";
    this.bl.style.top = (this.size.height - 8) + "px";
    this.br.style.left = (this.size.width - 8) + "px";
    this.br.style.top = (this.size.height - 8) + "px";
    this.exBtn.style.left = this.size.width - 8 - 13 + "px";
    this.div.style.width = this.size.width + "px";
    this.div.style.height = this.size.height + "px";
    var c = !SD.isSvg ? 0 : 2;
    var a = !SD.isSvg ? 25 : 24;
    var b = !SD.isSvg ? 11 : 1;
    this.tb.style.width = (this.size.width - 16) + "px";
    this.mb.style.width = (this.size.width - c) + "px";
    this.mb.style.height = (this.size.height - 16) + "px";
    this.bb.style.top = (this.size.height - 8 - b) + "px";
    this.bb.style.width = (this.size.width - 16) + "px";
    this.divContent.style.width = (this.size.width - 24) + "px";
    this.divContent.style.height = (this.size.height - 24) + "px";
    this.divContent.innerHTML = this.content
};
SD.genmap.SDInfoWindow.prototype.setSize = function(a, b) {
    this.size.width = a;
    this.size.height = b;
    this.validating();
    this.reloadUI()
};
SD.genmap.SDInfoWindow.prototype.init = function() {
    this.validating();
    this.tl = SD.util.createInfoFrame(8, 8, 0, 0, 0, 0, "small_top_left.png");
    this.tr = SD.util.createInfoFrame(8, 8, this.size.width - 8, 0, 0, 0, "small_top_right.png");
    this.bl = SD.util.createInfoFrame(8, 8, 0, this.size.height - 8, 0, 0, "small_btm_left.png");
    this.br = SD.util.createInfoFrame(8, 8, this.size.width - 8, this.size.height - 8, 0, 0, "small_btm_right.png");
    this.exBtn = SD.util.createInfoFrame(14, 13, this.size.width - 8 - 13, 10, 0, 0, "cl_grey.png");
    this.exBtn.style.cursor = "pointer";
    this.exBtn.style.zIndex = 20;
    var a = this;
    if (SD.isIphone) {
        EventManager.add(this.exBtn, "touchstart", function() {
            a.close()
        })
    } else {
        EventManager.add(this.exBtn, "click", function() {
            a.close()
        })
    }
    this.tb = new SD.util.createDiv();
    this.tb.style.cssText = "border-top: 1px solid rgb(171, 171, 171); position: absolute; left: 8px; top: 0px; width: " + (this.size.width - 16) + "px;height: 8px; background-color: white;";
    this.mb = new SD.util.createDiv();
    this.mb.style.cssText = "border-left: 1px solid rgb(171, 171, 171); border-right: 1px solid rgb(171, 171, 171); position: absolute; left: 0px; top: 8px; width: " + (this.size.width) + "px;height: " + (this.size.height - 16) + "px; background-color: white;";
    this.bb = new SD.util.createDiv();
    this.bb.style.cssText = "border-bottom: 1px solid rgb(171, 171, 171); position: absolute; left: 8px; top: " + parseInt(this.size.height - 8) + "px;width: " + (this.size.width - 16) + "px; height: 8px; background-color: white;";
    this.divContent = new SD.util.createDiv();
    this.divContent.style.cssText = "position: absolute; left: 8px; top: 8px; width: " + (this.size.width - 24) + "px; height: " + (this.size.height - 24) + "px; z-index: 10;";
    this.div.appendChild(this.tl);
    this.div.appendChild(this.tr);
    this.div.appendChild(this.bl);
    this.div.appendChild(this.br);
    this.div.appendChild(this.tb);
    this.div.appendChild(this.mb);
    this.div.appendChild(this.bb);
    this.div.appendChild(this.exBtn);
    this.div.appendChild(this.divContent);
    this.div.style.cursor = "default";
    this.div.onmousedown = function(b) {
        SD.util.cancelEvent(b, true, true)
    };
    EventManager.add(this.div, "DOMMouseScroll", function(b) {
        b.cancelBubble = true;
        b.cancel = true
    });
    EventManager.add(this.div, "mousewheel", function(b) {
        b.cancelBubble = true;
        b.cancel = true
    });
    this.reloadUI();
    this.setDisplay(false)
};

function DrawingPanTool(c) {
    var b = c;
    var a = false;
    this.name = "drawing pan tool";
    this.MouseDblClick = function(e, d) {
        a = false;
        b.endDraw();
        d.ActiveTool(d.defaultTool);
        return false
    };
    this.MouseDown = function(e, d) {
        if (SD.util.getMouseButton(e) == "LEFT") {
            b.drawReal(d.viewportInfo.getMetricPosDown());
            a = true
        } else {
            a = false
        }
    };
    this.MouseMove = function(e, d) {
        if (SD.util.getMouseButton(e) == "LEFT" && a) {
            b.drawBuffer(d.viewportInfo.getMetricPosMove())
        }
    }
}
SD.extend(DrawingPanTool, DrawingTool);

function DrawingManager(a) {
    this.map = null;
    SD.apply(this, a);
    this.objects = [];
    this.activeIndex = 0;
    this.activeObject = null;
    this.panTool = new DrawingPanTool(this)
}
DrawingManager.MODE_POLYLINE_OPEN = 3;
DrawingManager.MODE_POLYLINE_CLOSE = 2;
DrawingManager.MODE_ELLIPSE = 1;
DrawingManager.MODE_DRAG = 0;
DrawingManager.prototype.setActive = function(a) {
    this.activeObject = Shape.getInstance(a, {
        map: this.map
    });
    if (a == DrawingManager.MODE_DRAG) {
        this.map.viewport.ActiveTool(this.map.viewport.defaultTool)
    } else {
        this.map.viewport.ActiveTool(this.panTool)
    }
};
DrawingManager.prototype.drawReal = function(a) {
    if (this.objects[this.activeIndex] == null || this.objects.length == 0) {
        this.objects[this.activeIndex] = this.activeObject.init(a)
    } else {
        this.activeObject.clearBuffer();
        this.activeObject.drawReal(this.objects[this.activeIndex], a)
    }
};
DrawingManager.prototype.endDraw = function() {
    this.activeObject.endDraw(this.objects[this.activeIndex]);
    this.activeIndex++
};
DrawingManager.prototype.drawBuffer = function(a) {
    this.activeObject.drawBuffer(a)
};

function Shape() {}
Shape.obj_po = null;
Shape.obj_pc = null;
Shape.obj_e = null;
Shape.getInstance = function(c, a) {
    var b = null;
    if (c == DrawingManager.MODE_POLYLINE_OPEN) {
        if (Shape.obj_po == null) {
            Shape.obj_po = new SD.drawing.OpenPolyline(a)
        }
        b = Shape.obj_po
    } else {
        if (c == DrawingManager.MODE_POLYLINE_CLOSE) {
            if (Shape.obj_pc == null) {
                Shape.obj_pc = new SD.drawing.ClosePolyline(a)
            }
            b = Shape.obj_pc
        } else {
            if (Shape.obj_e == null) {
                Shape.obj_e = new Ellipse()
            }
            b = Shape.obj_e
        }
    }
    return b
};
SD.drawing.OpenPolyline = function(a) {
    this.name = "SD.drawing.OpenPolyline";
    this.closeShape = false;
    this.positions = [];
    this.markers = [];
    SD.apply(this, a);
    this.buffer = new SD.shape.Polyline([], {
        map: this.map,
        projection: this.map.viewportInfo.projection,
        color: "red",
        size: 2,
        opacity: "0.9",
        dash: 7
    });
    this.buffer.name = "ObjectBUFFER"
};
SD.drawing.OpenPolyline.prototype.init = function(a) {
    this.positions.push(a);
    var b = new SD.shape.Polyline(this.positions, {
        map: this.map,
        projection: this.map.viewportInfo.projection,
        color: "blue",
        size: 5,
        opacity: "0.7"
    });
    b.name = "ObjectREAL";
    this._addMarker(b, a);
    return b
};
SD.drawing.OpenPolyline.prototype.drawBuffer = function(b) {
    var a = this.positions.length;
    if (a > 0) {
        var c = this.positions[a - 1];
        this._drawBuffer([c, b])
    }
};
SD.drawing.OpenPolyline.prototype._drawBuffer = function(a) {
    if (!a) {
        return
    }
    this._draw(this.buffer, a)
};
SD.drawing.OpenPolyline.prototype.clearBuffer = function() {
    this._drawBuffer([])
};
SD.drawing.OpenPolyline.prototype.drawReal = function(b, a) {
    this.positions.push(a);
    this._draw(b, this.positions);
    this._addMarker(b, a)
};
SD.drawing.OpenPolyline.prototype._draw = function(b, a) {
    if (!b) {
        return
    }
    b.setPoints(a);
    b.draw(null)
};
SD.drawing.OpenPolyline.prototype.endDraw = function(a) {
    a.nodes = this.markers;
    this.positions = [];
    this.markers = []
};
SD.drawing.OpenPolyline.prototype.getListMetric = function(d, a, b, g) {
    if (d.nodes && d.nodes[a]) {
        if (d.nodes.length > 0) {
            var f = [];
            for (var e = 0, h = d.points.length; e < h; e++) {
                if (g && (e == a - 1 || e == a + 1)) {
                    f.push(d.points[e])
                }
                if (e == a) {
                    f.push(b)
                } else {
                    if (!g) {
                        f.push(d.points[e])
                    }
                }
            }
            if (this.closeShape) {
                if (g && a == 0) {
                    f = [d.points[h - 2], b, d.points[1]]
                } else {
                    if (!g) {
                        f[h - 1] = f[0]
                    }
                }
            }
            return f
        }
    }
    return false
};
SD.drawing.OpenPolyline.prototype._addMarker = function(d, c) {
    var b = new SD.genmap.MarkerStatic({
        map: this.map,
        icon: new DrawingNode({
            opacity: 1
        }),
        projection: this.projection
    });
    b.index = this.markers.length;
    b.setPosition(c);
    var a = new DraggableTool();
    a.init(b, this.map.viewport, {
        _manager: this,
        MouseMove: function(h, f) {
            var g = f.viewportInfo.getMetricPosMove();
            this._manager._drawBuffer(this._manager.getListMetric(d, b.index, g, true))
        },
        MouseUp: function(g, f) {
            this._manager.clearBuffer();
            this._manager._draw(d, this._manager.getListMetric(d, b.index, b.position, false))
        }
    });
    this.markers.push(b)
};
SD.drawing.ClosePolyline = function(a) {
    SD.drawing.ClosePolyline.superclass.constructor.call(this, a);
    this.name = "SD.drawing.ClosePolyline";
    this.closeShape = true
};
SD.extend(SD.drawing.ClosePolyline, SD.drawing.OpenPolyline);
SD.drawing.ClosePolyline.prototype.endDraw = function(a) {
    this.positions.push(this.positions[0]);
    SD.drawing.ClosePolyline.superclass._draw.call(this, a, this.positions);
    SD.drawing.ClosePolyline.superclass.endDraw.call(this, a)
};
SD.drawing.Ellipse = function(a) {
    SD.drawing.Ellipse.superclass.constructor.call(this, a);
    this.name = "SD.drawing.Ellipse";
    this.buffer = new SD.shape.Ellipse([], {
        map: this.map,
        projection: this.map.viewportInfo.projection,
        color: "red",
        size: 2,
        opacity: "0.9",
        dash: 7
    });
    this.buffer.name = "ObjectBUFFER"
};
SD.drawing.Ellipse.prototype.init = function(a) {
    this.positions.push(a);
    var b = new SD.shape.Polyline(this.positions, {
        map: this.map,
        projection: this.map.viewportInfo.projection,
        color: "blue",
        size: 5,
        opacity: "0.7"
    });
    b.name = "ObjectREAL";
    this._addMarker(b, a);
    return b
};
SD.drawing.Ellipse.prototype.drawBuffer = function(b) {
    var a = this.positions.length;
    if (a > 0) {
        var c = this.positions[a - 1];
        this._drawBuffer([c, b])
    }
};
SD.drawing.Ellipse.prototype._drawBuffer = function(a) {
    if (!a) {
        return
    }
    this._draw(this.buffer, a)
};
SD.drawing.Ellipse.prototype.clearBuffer = function() {
    this._drawBuffer([])
};
SD.drawing.Ellipse.prototype.drawReal = function(b, a) {
    this.positions.push(a);
    this._draw(b, this.positions);
    this._addMarker(b, a)
};
SD.drawing.Ellipse.prototype._draw = function(b, a) {
    if (!b) {
        return
    }
    b.setPoints(a);
    b.draw(null)
};
SD.drawing.Ellipse.prototype.endDraw = function(a) {
    a.nodes = this.markers;
    this.positions = [];
    this.markers = []
};
SD.drawing.Ellipse.prototype.getListMetric = function(d, a, b, g) {
    if (d.nodes && d.nodes[a]) {
        if (d.nodes.length > 0) {
            var f = [];
            for (var e = 0, h = d.points.length; e < h; e++) {
                if (g && (e == a - 1 || e == a + 1)) {
                    f.push(d.points[e])
                }
                if (e == a) {
                    f.push(b)
                } else {
                    if (!g) {
                        f.push(d.points[e])
                    }
                }
            }
            if (this.closeShape) {
                if (g && a == 0) {
                    f = [d.points[h - 2], b, d.points[1]]
                } else {
                    if (!g) {
                        f[h - 1] = f[0]
                    }
                }
            }
            return f
        }
    }
    return false
};
SD.drawing.Ellipse.prototype._addMarker = function(d, c) {
    var b = new SD.genmap.MarkerStatic({
        map: this.map,
        icon: new DrawingNode({
            opacity: 1
        }),
        projection: this.projection
    });
    b.index = this.markers.length;
    b.setPosition(c);
    var a = new DraggableTool();
    a.init(b, this.map.viewport, {
        _manager: this,
        MouseMove: function(h, f) {
            var g = f.viewportInfo.getMetricPosMove();
            this._manager._drawBuffer(this._manager.getListMetric(d, b.index, g, true))
        },
        MouseUp: function(g, f) {
            this._manager.clearBuffer();
            this._manager._draw(d, this._manager.getListMetric(d, b.index, b.position, false))
        }
    });
    this.markers.push(b)
};

function DrawingNode(a) {
    this.pt = new Point(0, 0);
    this.iconSize = new Size(8, 8);
    this.iconAnchor = new Point(4, 4);
    this.infoWindowAnchor = new Point(5, 5);
    SD.apply(this, a);
    this.object = "";
    this.getObject = function(b) {
        if (this.object == "") {
            this.object = document.createElement("div");
            this.object.style.width = "8px";
            this.object.style.height = "8px";
            this.object.style.position = "absolute";
            this.object.style.cursor = "pointer";
            this.object.style.fontSize = "1%";
            this.object.style.border = "1px solid #cfcfcf";
            this.object.style.backgroundColor = "#ffffff";
            if (this.opacity > 0) {
                this.object.style.opacity = this.opacity;
                this.object.style.filter = "alpha(opacity=" + (this.opacity * 100) + ")"
            }
        }
        if (b > 0) {
            this.object.style.zIndex = b
        }
        return this.object
    }
}
SD.extend(DrawingNode, SD.genmap.MarkerImage);

function ViewportInfo() {
    this.div = null;
    this.scale = 66.66666940601503;
    this.levelIndex = 1;
    this.lastCursorLatLon = new GeoPoint(0, 0);
    this.lastCursorPosDown = new Point(0, 0);
    this.lastCursorPosUp = new Point(0, 0);
    this.lastCursorPosMove = new Point(0, 0);
    this.lastCursorPosOffset = new Point(0, 0);
    this.lastCursorDelta = 0;
    this.projection = new SD.projection.Mercator();
    this.canvasSize = new Size(0, 0);
    this.centerGeo = new GeoPoint(0, 0);
    this.centerMetric = new Vertex(0, 0);
    this.centerScreen = new Point(0, 0);
    this.topLeftGeo = new GeoPoint(0, 0);
    this.topLeftMetric = new Vertex(0, 0);
    this.topLeftScreen = new Point(0, 0);
    this.topLeftOverlay = new Point(0, 0);
    this.topLeftContainer = new Point(0, 0);
    this.screenView = new Rectangle(0, 0, 0, 0);
    this.metricView = new Rectangle(0, 0, 0, 0);
    this.geoView = new Rectangle(0, 0, 0, 0);
    this.mapConfig = null;
    this.init = function(a, c, b) {
        if (c != null) {
            this.projection = c
        }
        if (b) {
            this.centerGeo = this.projection.metricToGeo(this.centerMetric.x, this.centerMetric.y)
        } else {
            this.centerMetric = this.projection.geoToMetric(this.centerGeo.lon, this.centerGeo.lat)
        }
        this.centerScreen = this.projection.metricToPixel(this.centerMetric.x, this.centerMetric.y, this.scale);
        if (a != null) {
            this.canvasSize = a
        }
        this.topLeftScreen.x = this.centerScreen.x - (this.canvasSize.width / 2);
        this.topLeftScreen.y = this.centerScreen.y - (this.canvasSize.height / 2);
        this.recalculate()
    };
    this.recalculate = function() {
        this.topLeftMetric = this.projection.pixelToMetric(this.topLeftScreen.x, this.topLeftScreen.y, this.scale);
        this.topLeftGeo = this.projection.pixelToGeo(this.topLeftScreen.x, this.topLeftScreen.y, this.scale);
        this.screenView = new Rectangle(this.topLeftScreen.x, this.topLeftScreen.y, this.canvasSize.width, this.canvasSize.height);
        var a = this.projection.pixelToMetric(this.topLeftScreen.x + this.canvasSize.width, this.topLeftScreen.y + this.canvasSize.height, this.scale);
        this.metricView = new Rectangle(this.topLeftMetric.x, this.topLeftMetric.y, a.x, a.y);
        var b = this.projection.pixelToGeo(this.topLeftScreen.x + this.canvasSize.width, this.topLeftScreen.y + this.canvasSize.height, this.scale);
        this.geoView = new Rectangle(this.topLeftGeo.lon, this.topLeftGeo.lat, b.lon, b.lat)
    };
    this.getCanvasRect = function() {
        if (this.mapConfig == null) {
            return false
        }
        var b = this.projection.geoToPixel(this.mapConfig.minLongitude, this.mapConfig.maxLatitude, this.scale);
        var c = {
            x: this.topLeftScreen.x - b.x,
            y: this.topLeftScreen.y - b.y
        };
        var a = {
            x: c.x + this.canvasSize.width,
            y: c.y + this.canvasSize.height
        };
        return new Rectangle(c.x, c.y, a.x, a.y)
    };
    this.getCanvasSize = function() {
        if (this.mapConfig == null) {
            return false
        }
        var a = this.mapConfig.ratio == 0.99 ? 1 : this.mapConfig.ratio;
        return {
            x: this.mapConfig.mapTileWidth * a,
            y: this.mapConfig.mapTileHeight * a
        }
    };
    this.reInit = function() {
        this.init(this.canvasSize, this.projection)
    };
    this.getRowCol = function(a) {
        if (this.mapConfig == null) {
            return false
        }
        return this.mapConfig.getRowCol(a.x + this.topLeftScreen.x, a.y + this.topLeftScreen.y)
    };
    this.getCursorMoveRowCol = function() {
        return this.getRowCol(this.lastCursorPosMove)
    };
    this.viewportScreenToGeo = function(a, b) {
        return this.projection.screenToGeo(a, b, this.scale, this.topLeftScreen)
    };
    this.viewportGeoToScreen = function(a) {
        return this.projection.geoToScreen(a.lon, a.lat, this.scale, this.topLeftScreen)
    };
    this.viewportScreenToMetric = function(a, b) {
        return this.projection.screenToMetric(a, b, this.scale, this.topLeftScreen)
    };
    this.canvasGeoToScreen = function(a) {
        if (this.topLeftOverlay == undefined) {
            return false
        }
        return this.projection.geoToScreen(a.lon, a.lat, this.scale, this.topLeftOverlay)
    };
    this.setCenterFromViewportScreenPosition = function(a, b) {
        this.centerGeo = this.viewportScreenToGeo(a, b);
        this.reInit()
    };
    this.viewportScale = function(a) {
        if (a != undefined) {
            this.scale = a;
            this.reInit()
        } else {
            return this.scale
        }
    };
    this.setCenter = function(a, c) {
        var b = this.projection.inflateGeo(this.centerGeo, -a, -c, this.scale);
        if (b) {
            this.centerGeo = b;
            this.reInit()
        }
    };
    this.getMetricPosDown = function() {
        var a = this.lastCursorPosDown;
        return this.viewportScreenToMetric(a.x, a.y)
    };
    this.getMetricPosMove = function() {
        var a = this.lastCursorPosMove;
        return this.viewportScreenToMetric(a.x, a.y)
    };
    this.isInViewport = function(a) {
        if (this.pointInGeoView(a.left, a.top) || this.pointInGeoView(a.left, a.bottom) || this.pointInGeoView(a.right, a.top) || this.pointInGeoView(a.right, a.bottom) || this.pointInGeoView(this.geoView.left, this.geoView.top, a) || this.pointInGeoView(this.geoView.left, this.geoView.bottom, a) || this.pointInGeoView(this.geoView.right, this.geoView.top, a) || this.pointInGeoView(this.geoView.right, this.geoView.bottom, a)) {
            return true
        }
        return false
    };
    this.pointInGeoView = function(c, b, a) {
        a = a == undefined ? this.geoView : a;
        if (a.top >= b && a.bottom <= b && a.left <= c && a.right >= c) {
            return true
        }
        return false
    }
}

function ViewportControl(a) {
    this.viewportInfo = new ViewportInfo();
    this.defaultTool = new ViewportPanTool();
    this.activeTool = this.defaultTool;
    this.onDrag = false;
    this.initializeEvents = false;
    this.viewportLayer = new SDLayer("id_viewport_layer");
    this.zoomLayer = new ZoomObject();
    this.mapLayer = new MapObject();
    this.vectorLayer = new DrawingLayer();
    this.container = new SDLayer("id_container");
    this.container.div.style.position = "";
    this.mapContainer = new SDLayer("id_map_container");
    this.mapContainer.div.style.position = "";
    this.hintLayer = new SDLayer("id_hint_layer");
    this.infoWindow = new SD.genmap.GInfoWindow();
    this.markerStaticLayer = new MarkerStaticLayer();
    this.disableMouseWheel = false;
    this.dom = null;
    this.size = new Size(0, 0);
    this.canvasInfo = {};
    this.mapAPI = null;
    this.mapManager = null;
    this.projection = null;
    this.scrollwheel = true;
    this.enableDefaultLogo = true;
    this.bindEventOnSelf = false;
    this.control = null;
    this.tooltip = null;
    this.parentDiv = null;
    this.OnLevelChanged = new EventDelegates();
    this.OnDraw = new EventDelegates();
    this.OnEndDrag = new EventDelegates();
    this.OnEndMove = new EventDelegates();
    this.OnEndWheel = new EventDelegates();
    this.OnDoubleClick = new EventDelegates();
    this.init(a)
}
ViewportControl.prototype = {
    ActiveTool: function(a) {
        if (a != undefined) {
            this.activeTool = a
        } else {
            return this.activeTool
        }
    },
    requestForRedraw: function(a) {
        var b = this;
        if (a == 1) {
            setTimeout(function() {
                b.draw()
            }, 0)
        } else {
            if (a == 0) {
                setTimeout(function() {
                    b.moveViewport()
                }, 0)
            }
        }
    },
    getCenter: function(c) {
        var b = this.viewportInfo.centerGeo;
        var a = this.projection.geoToMetric(b.lon, b.lat);
        return this.projection.inflateVert(a, -c.x, -c.y, this.viewportInfo.scale)
    },
    setLevel: function(b) {
        if (this.mapManager != null) {
            var a = this.mapManager.getLength();
            if (b <= a && 1 <= b) {
                this.viewportInfo.levelIndex = b
            }
        } else {
            if (b > 0) {
                this.viewportInfo.levelIndex = b
            }
        }
    },
    setCenter: function(a, b) {
        this.viewportInfo.centerGeo = a;
        if (b == true) {
            this.updateMapLayerByLevel(this.viewportInfo.levelIndex);
            this.draw()
        }
    },
    getCenterOnWorldBound: function(f) {
        var e = this.viewportInfo.levelIndex < 6 ? this.viewportInfo.levelIndex - 1 : -1;
        var g = this.mapManager.layers[e];
        if (g == null) {
            return f
        }
        var c = f.x ? f.x : f.lon;
        var i = f.y ? f.y : f.lat;
        var a = f.x || f.y ? g.boundsMetric : g.bounds;
        if (c < a.left) {
            var h = a.left - c;
            c = a.right - h
        } else {
            if (c > a.right) {
                var h = a.right - c;
                c = a.left - h
            }
        }
        if (f.lon) {
            f.lon = c
        } else {
            f.x = c
        }
        return f
    },
    panCenter: function(c, b) {
        if (this.projection != null) {
            var a = this.projection.inflateVert(this.viewportInfo.centerMetric, -c.x, -c.y, this.viewportInfo.scale);
            a = this.getCenterOnWorldBound(a);
            this.viewportInfo.centerMetric = a
        }
    },
    wheelCenter: function(e, d, a) {
        if (this.projection != null && e > 0) {
            if (a == undefined || a == null) {
                a = this.viewportInfo.lastCursorLatLon
            }
            if (this.viewportInfo.lastCursorPosMove.x == 0 && this.viewportInfo.lastCursorPosMove.y == 0 && a.x != undefined && (d == undefined || d == null)) {
                var c = this.viewportInfo.lastCursorPosMove = {
                    x: a.x,
                    y: a.y
                };
                d = this.getCursorDistanceFromCenter(c)
            }
            if (d == undefined || d == null) {
                d = this.getCursorDistanceFromCenter()
            }
            var b = this.projection.inflateGeo(a, d.x, d.y, e);
            b = this.getCenterOnWorldBound(b);
            this.setCenter(b, false)
        }
    },
    getNextLevel: function(d) {
        var c = this.viewportInfo.levelIndex + (d ? 1 : -1);
        var a = this.mapManager.layers.length;
        c = c <= 0 ? 1 : a <= c ? a : c;
        var b = this.mapManager.getMapLayerByLevel(c, this.viewportInfo.lastCursorLatLon.lon, this.viewportInfo.lastCursorLatLon.lat);
        return b.scale == undefined ? -1 : b.scale
    },
    setScale: function(a, b) {
        if (a > 0 && !isNaN(a)) {
            this.viewportInfo.scale = a
        }
        if (b == true) {
            this.draw()
        }
    },
    updateMapLayerByLevel: function(b) {
        if (this.mapManager == null) {
            return
        }
        var a = this.mapManager.getMapLayerByLevel(b, this.viewportInfo.centerGeo.lon, this.viewportInfo.centerGeo.lat);
        if (!a) {
            return false
        }
        if (a.scale < 0) {
            return false
        }
        this.viewportInfo.mapConfig = a;
        this.viewportInfo.levelIndex = b;
        this.setScale(a.scale, false);
        this.projection = a.projection;
        this.mapLayer.clear();
        if (this.zoomLayer) {
            this.zoomLayer.clear()
        }
        this.levelChanged();
        if (this.OnLevelChanged) {
            this.OnLevelChanged.triggered(this.viewportInfo)
        }
    },
    updateMapLayerByNearest: function(b, c) {
        var a = this.mapManager.getMapLayerByNearest(b, (c ? this.viewportInfo.levelIndex : undefined), this.viewportInfo.centerGeo.lon, this.viewportInfo.centerGeo.lat);
        if (!a.layer || b <= 0) {
            a = this.mapManager.getMapLayerByNearest(b, (c ? this.viewportInfo.levelIndex : undefined), this.viewportInfo.lastCursorLatLon.lon, this.viewportInfo.lastCursorLatLon.lat);
            if (!a.layer || b <= 0) {
                return false
            }
        }
        if (a.layer.scale < 0) {
            return false
        }
        a.layer.ratio = 1;
        this.viewportInfo.levelIndex = a.layer.realLevel;
        this.projection = a.layer.projection;
        this.setScale(a.layer.scale, false);
        this.viewportInfo.mapConfig = a.layer;
        this.levelChanged();
        if (this.OnLevelChanged) {
            this.OnLevelChanged.triggered(this.viewportInfo)
        }
    },
    levelChanged: function() {
        this.mapLayer.isRender = true;
        this.markerStaticLayer.setDraw(true);
        if (this.mapAPI != null) {
            this.mapAPI._updateInfo(this)
        }
    },
    MouseWheel: function(b) {
        var c = 0;
        if (typeof b == "undefined") {
            b = window.event
        }
        if (b.wheelDelta) {
            c = b.wheelDelta / 120
        } else {
            if (b.detail) {
                c = -b.detail / 3
            }
        }
        this.control = typeof this.control === "undefined" ? document.control : this.control;
        if (this.control.disableMouseWheel) {
            return
        }
        SD.util.cancelEvent(b, true);
        var a = SD.util.getCursorPos(b, this.control.parentDiv);
        this.control.viewportInfo.lastCursorWheel = this.control.viewportInfo.viewportScreenToGeo(a.x, a.y);
        this.control.viewportInfo.lastCursorLatLon = this.control.viewportInfo.lastCursorWheel;
        this.control.viewportInfo.lastCursorDelta = c;
        if (this.control.activeTool) {
            if (this.control.scrollwheel) {
                this.control.activeTool.AnimatedMouseWheel(b, this.control)
            } else {
                this.control.activeTool.MouseWheel(b, this.control)
            }
        }
        return false
    },
    MouseDown: function(b) {
        if (typeof b == "undefined") {
            b = window.event
        }
        if (b.preventDefault) {
            b.preventDefault()
        }
        var a = SD.util.getCursorPos(b, this.control.parentDiv);
        this.control.onDrag = true;
        this.control.viewportInfo.lastCursorPosDown = a;
        this.control.viewportInfo.lastCursorPosMove = a;
        this.control.viewportInfo.lastCursorLatLon = this.control.viewportInfo.viewportScreenToGeo(a.x, a.y);
        document.control = this.control;
        if (this.control.activeTool) {
            this.control.activeTool.MouseDown(b, this.control)
        }
    },
    MouseMove: function(d) {
        if (typeof d == "undefined") {
            d = window.event
        }
        var c = typeof this.control === "undefined" ? document.control : this.control;
        var b = SD.util.getCursorPos(d, c.parentDiv);
        c.viewportInfo.lastCursorPosOffset = SD.util.offsetPoint(b, -c.viewportInfo.lastCursorPosMove.x, -c.viewportInfo.lastCursorPosMove.y);
        c.viewportInfo.lastCursorPosMove = b;
        if (c.onDrag) {
            var a = c.viewportInfo.viewportScreenToGeo(b.x, b.y);
            c.viewportInfo.lastCursorLatLon = a;
            if (!isNaN(a.lon) && !isNaN(a.lat)) {
                c.viewportInfo.lastCursorLatLon = c.getCenterOnWorldBound(a)
            }
        }
        if (c.activeTool) {
            c.activeTool.MouseMove(d, c)
        }
    },
    MouseUp: function(c) {
        if (typeof c == "undefined") {
            c = window.event
        }
        if (top != self && this.control == null) {
            this.control = self.document.control
        }
        var b = SD.util.getCursorPos(c, this.control.parentDiv);
        if (this.control.onDrag) {
            var a = this.control.viewportInfo.viewportScreenToGeo(b.x, b.y);
            if (!isNaN(a.lon) && !isNaN(a.lat)) {
                this.control.viewportInfo.lastCursorLatLon = this.control.getCenterOnWorldBound(a)
            }
            this.control.getInfo(true)
        }
        this.control.onDrag = false;
        this.control.viewportInfo.lastCursorPosUp = b;
        if (this.control.activeTool) {
            this.control.activeTool.MouseUp(c, this.control)
        }
    },
    MouseClick: function(a) {
        if (this.control.activeTool) {
            this.control.activeTool.MouseClick(a, this.control)
        }
    },
    MouseDblClick: function(a) {
        if (this.control.activeTool) {
            this.control.activeTool.MouseDblClick(a, this.control)
        }
    },
    GestureStart: function(a) {
        if (this.control.activeTool) {
            this.control.activeTool.GestureStart(a, this.control)
        }
    },
    GestureEnd: function(a) {
        if (this.control.activeTool) {
            this.control.activeTool.GestureEnd(a, this.control)
        }
    },
    GestureChange: function(a) {
        if (this.control.activeTool) {
            this.control.activeTool.GestureChange(a, this.control)
        }
    },
    zoomIn: function() {
        var a = this.viewportInfo.levelIndex + 1;
        if (a <= this.mapManager.getLength() && 1 <= a) {
            this.updateMapLayerByLevel(a);
            this.requestForRedraw(1)
        }
    },
    zoomOut: function() {
        var a = this.viewportInfo.levelIndex - 1;
        if (a <= this.mapManager.getLength() && 1 <= a) {
            this.updateMapLayerByLevel(a);
            this.requestForRedraw(1)
        }
    },
    getInfo: function(a) {
        this.viewportInfo.init(null, this.projection, a);
        this.rebuildCanvasInfo();
        if (this.mapAPI != null) {
            this.mapAPI._updateInfo(this)
        }
        return this.viewportInfo
    },
    rebuildCanvasInfo: function(j) {
        this.canvasInfo = SD.util.clone(this.viewportInfo);
        if (this.canvasInfo.centerScreen.x == 0 && this.canvasInfo.centerScreen.y == 0) {
            this.canvasInfo.init(null, this.projection)
        }
        var e = this.canvasInfo.getCanvasRect();
        var h = this.canvasInfo.getCanvasSize();
        var d = Math.ceil(e.left / h.x);
        var c = Math.ceil(e.top / h.y);
        var i = d + Math.ceil(this.canvasInfo.canvasSize.width / h.x);
        var f = c + Math.ceil(this.canvasInfo.canvasSize.height / h.y);
        var g = new Rectangle(0, 0, 0, 0);
        g.top = (c - 1) * h.y;
        g.left = (d - 1) * h.x;
        g.right = (i) * h.x;
        g.bottom = (f) * h.y;
        var a = new Rectangle(0, 0, 0, 0);
        a.left = g.left - e.left;
        a.top = g.top - e.top;
        a.setWidth((i - d + 1) * h.x);
        a.setHeight((f - c + 1) * h.y);
        this.canvasInfo.topLeftContainer = this.viewportLayer.rect;
        this.canvasInfo.offsetContainer = {
            x: Math.round(a.left - this.viewportLayer.rect.x),
            y: Math.round(a.top - this.viewportLayer.rect.y)
        };
        this.canvasInfo.mapConfigBounds = e;
        this.canvasInfo.topLeftOverlay = {
            x: this.canvasInfo.topLeftScreen.x + this.viewportLayer.rect.x,
            y: this.canvasInfo.topLeftScreen.y + this.viewportLayer.rect.y
        };
        this.canvasInfo.mapRowCols = new Rectangle(d, c, i, f);
        this.canvasInfo.pixelMargin = new Rectangle(-h.x, -h.y, (i - d) * h.x, (f - c) * h.y);
        this.canvasInfo.mapTileBounds = a;
        this.canvasInfo.mapTileSize = h;
        this.canvasInfo.recalculate();
        return this.canvasInfo
    },
    update: function() {
        this.container.update(this.canvasInfo)
    },
    draw: function() {
        if (this.viewportInfo.mapConfig == null) {
            return
        }
        this.dom.setDisplay(true);
        this.viewportLayer.setTopLeft({
            x: 0,
            y: 0
        });
        this.viewportInfo.mapConfig.ratio = 1;
        this.getInfo();
        var c = this.canvasInfo.mapRowCols;
        if (c != null && this.canvasInfo.mapConfig != null) {
            var b = this.canvasInfo.mapConfig;
            var a = b.createList(c.left, c.top, c.right, c.bottom);
            this.mapLayer.tiles.unReloadImg();
            this.mapLayer.clear();
            this.container.setEnable(true);
            if (this.mapLayer.cssName != null) {
                this.zoomLayer.setEnable(false)
            }
            this.mapContainer.setWidth(this.viewportInfo.canvasSize);
            this.zoomLayer.setWidth(this.viewportInfo.canvasSize);
            this.canvasInfo.layer = this.drawLayer;
            this.canvasInfo.mapList = a;
            this.viewportLayer.draw(this.canvasInfo, c.top, c.left, c.bottom, c.right)
        }
        if (this.OnDraw) {
            this.OnDraw.triggered(this.canvasInfo)
        }
    },
    drawAll: function() {},
    drawLayer: function(a) {
        this.modelLayers.setDisplay(true);
        this.modelLayers.refresh(a == undefined ? this.getContainerInfo() : a)
    },
    clearMap: function(a) {
        this.zoomLayer.isRender = true;
        this.zoomLayer.setDisplay(false);
        if (a) {
            this.zoomLayer.clear();
            this.zoomLayer.mapList = SD.util.clone(this.mapLayer.tiles);
            this.zoomLayer.setUnTransform()
        }
        this.mapLayer.setDisplay(false);
        this.viewportLayer.setTopLeft({
            x: 0,
            y: 0
        })
    },
    animateMap: function() {
        this.getInfo();
        this.zoomLayer.setEnable(true);
        this.mapLayer.setEnable(false);
        this.setLegendEnable(false);
        if (!SD.isIphone) {
            var a = this.canvasInfo.mapRowCols;
            this.viewportLayer.draw(this.canvasInfo, a.top, a.left, a.bottom, a.right)
        }
    },
    setLegendEnable: function(a) {
        this.markerStaticLayer.setEnable(a);
        this.vectorLayer.setEnable(a);
        this.hintLayer.setEnable(a)
    },
    moveViewport: function() {
        this.moveByOffset(this.viewportInfo.lastCursorPosOffset, true)
    },
    getCursorDistanceFromCenter: function(a) {
        if (a == undefined) {
            a = this.viewportInfo.lastCursorPosMove
        }
        return {
            x: -(a.x - this.viewportInfo.canvasSize.width / 2),
            y: -(a.y - this.viewportInfo.canvasSize.height / 2)
        }
    },
    endDrag: function() {
        this.moveByOffset({
            x: (this.viewportInfo.lastCursorPosUp.x - this.viewportInfo.lastCursorPosMove.x),
            y: (this.viewportInfo.lastCursorPosUp.y - this.viewportInfo.lastCursorPosMove.y)
        }, false)
    },
    moveByOffset: function(b, a) {
        this.panCenter(b, false);
        if (a) {
            this.viewportLayer.setOffset(b)
        } else {
            this.draw()
        }
    },
    animatePanBy: function(f, b) {
        if (!SD.isIphone && (Math.abs(f.x) > this.viewportInfo.canvasSize.width || Math.abs(f.y) > this.viewportInfo.canvasSize.height)) {
            this.panCenter({
                x: -f.x,
                y: -f.y
            }, false);
            this.getInfo(true);
            this.draw();
            if (this.OnEndMove) {
                this.OnEndMove.triggered(this.viewportInfo)
            }
            return
        }
        if (this.interval) {
            return
        }
        var c = 1,
            a = this,
            e = {
                ox: 0,
                oy: 0,
                x: 0,
                y: 0
            },
            d;
        this.interval = setInterval(function() {
            e.x = SD.util.easeInOut({
                first: 0,
                latest: f.x
            }, b, c);
            e.y = SD.util.easeInOut({
                first: 0,
                latest: f.y
            }, b, c);
            d = {
                x: e.ox - e.x,
                y: e.oy - e.y
            };
            a.moveByOffset(d, true);
            e.ox = e.x;
            e.oy = e.y;
            c++;
            if (c > b) {
                a.getInfo(true);
                a.update();
                if (a.OnEndMove) {
                    a.OnEndMove.triggered(a.viewportInfo)
                }
                window.clearInterval(a.interval);
                a.interval = false
            }
        }, 50)
    },
    animatePanTo: function(b, c) {
        var a = this.viewportInfo.viewportGeoToScreen(b);
        var d = {
            x: (a.x - this.viewportInfo.canvasSize.width / 2),
            y: (a.y - this.viewportInfo.canvasSize.height / 2)
        };
        this.animatePanBy(d, c == undefined ? 10 : c)
    },
    addControl: function(a) {
        this.realDiv.appendChild(a.getNavigation());
        this.control = a.control
    },
    setLogoToDefault: function() {
        var a = new SD.util.createImg("", SD.IMG_URL + "logo.gif", "0px", "0px", "30px", "30px", "absolute");
        if (this.setCustomLogo) {
            var a = this.setCustomLogo
        }
        var c = new SD.util.createDiv();
        var b = new SD.util.createImg("", SD.IMG_URL + "north.gif", "0px", "0px", "28px", "16px", "absolute");
        c.innerHTML = "(c) Streetdirectory.com";
        c.style.cssText = "position: absolute; left: 0px; bottom: 0px; background-color: #FFFFCC; font-family: arial; font-size: 11px; padding: 2px;";
        b.style.cssText = "position: absolute; right: 0px; bottom: 0px;";
        this.fakeDiv.appendChild(a);
        this.fakeDiv.appendChild(c);
        this.fakeDiv.appendChild(b)
    },
    getCompletedPercentage: function() {
        var c = this.mapLayer.tiles.getSumLoadedNodes(this.mapLayer.tiles.node);
        var b = this.mapLayer.tiles.node.length;
        var a = c * 100 / b;
        return a
    },
    getCursorPosition: function(a) {
        return SD.util.getCursorPos(a, this.parentDiv)
    },
    init: function(a) {
        SD.applyProperty(this, a);
        this.viewportInfo = new ViewportInfo();
        if (a.center) {
            this.setCenter(a.center)
        }
        if (a.zoom) {
            this.setLevel(a.zoom)
        }
        if (!a.draggable) {
            this.ActiveTool(false)
        }
        this.dom = new StdDiv();
        if (a.bingCredentials || a.enableGoogle) {
            if (a.enableGoogle) {
                a.dom.innerHTML = ""
            }
            this.dom.cleanAbsolute();
            this.dom.setId("sd_" + Math.round(Math.random() * 100));
            this.dom.appendToDom(a.dom);
            this.dom.setDisplay(false)
        } else {
            this.dom.div = typeof a.dom == "string" ? document.getElementById(a.dom) : a.dom
        }
        this.parentDiv = a.dom;
        this.initUI(this.dom.div, a)
    },
    initUI: function(f, e) {
        this.fakeDiv = typeof f == "string" ? document.getElementById(f) : f;
        var b = document.createElement("div");
        b.style.cssText = "position:absolute;left:0px;top:0px;width:100%;height:100%;overflow:hidden;background-color:#CCFFCC";
        this.realDiv = document.createElement("div");
        this.realDiv.setAttribute("id", "id_real_div");
        this.fakeDiv.style.overflow = "hidden";
        this.fakeDiv.style.position = "relative";
        this.fakeDiv.appendChild(this.realDiv);
        this.viewportInfo.div = this.realDiv;
        this.realDiv.appendChild(b);
        if (this.enableDefaultLogo) {
            this.setLogoToDefault()
        }
        var a = this.fakeDiv.clientWidth == 0 ? parseInt(this.fakeDiv.style.width) : this.fakeDiv.clientWidth,
            d = this.fakeDiv.clientHeight == 0 ? parseInt(this.fakeDiv.style.height) : this.fakeDiv.clientHeight;
        if (e) {
            if (e.resize) {
                a = e.resize.w;
                d = e.resize.h
            }
            this.mapAPI = e;
            this.infoWindow = new SD.genmap.GInfoWindow({
                size: {
                    width: 260,
                    height: 100
                },
                map: e
            });
            e.divCopyright = false
        }
        this.hintLayer.div.style.cursor = "default";
        this.mapContainer.div.style.whiteSpace = "nowrap";
        this.mapContainer.div.style.lineHeight = "0";
        this.mapContainer.addNode(this.zoomLayer);
        this.mapContainer.addNode(this.mapLayer);
        this.hintLayer.addNode(this.infoWindow);
        this.container.addNode(this.mapContainer);
        this.container.addNode(this.vectorLayer);
        this.container.addNode(this.markerStaticLayer);
        this.container.addNode(this.hintLayer);
        this.viewportLayer.addNode(this.container);
        b.appendChild(this.viewportLayer.div);
        this.mapControl = b;
        if (this.showCopyright) {
            var c = document.createElement("div");
            c.innerHTML = 'Streetdirectory.com App comes with offline maps of SG, JB, KL, Jakarta. <a href="http://www.streetdirectory.com/mobile" target="_blank" style="color: #0100FE; text-decoration: none;">Download Now</a>. Its Free';
            c.style.cssText = "z-index: 3; position: absolute; right: 0px; bottom: 0px; background-color: #FFFFCC; font-family: arial; font-size: 11px; white-space: nowrap; text-align: right; padding: 2px;";
            this.fakeDiv.appendChild(c);
            if (e) {
                e.divCopyright = c
            }
        }
        b.oncontextmenu = function() {
            return false
        };
        this.initEvents();
        this._resize(a, d, false);
        if (this.updateMapLayerByLevel(this.viewportInfo.levelIndex) == false) {
            return
        }
    },
    initEvents: function() {
        if (!this.initializeEvents) {
            var a = this.mapControl;
            a.control = this;
            document.control = this;
            if (SD.isTouchDevice()) {
                EventManager.add(a, "touchstart", this.MouseDown);
                EventManager.add(a, "touchmove", this.MouseMove);
                EventManager.add(a, "touchend", this.MouseUp);
                EventManager.add(a, "touchcancel", this.MouseUp);
                EventManager.add(a, "gesturechange", this.GestureChange);
                EventManager.add(a, "gesturestart", this.GestureStart);
                EventManager.add(a, "gestureend", this.GestureEnd);
                this.ActiveTool(new IphonePanTool())
            } else {
                EventManager.add(a, "mousedown", this.MouseDown);
                EventManager.add(document, "mousemove", this.MouseMove);
                EventManager.add(document, "mouseup", this.MouseUp);
                EventManager.add(document, "dblclick", this.MouseDblClick);
                EventManager.add(a, "DOMMouseScroll", this.MouseWheel);
                EventManager.add(a, "mousewheel", this.MouseWheel);
                if (top != self) {
                    EventManager.add(document, "mouseout", function(b) {
                        if (SD.util.checkMouseLeave(self.document.control.parentDiv, b)) {
                            self.document.control.MouseUp()
                        }
                    })
                }
            }
            this.initializeEvents = true
        }
    },
    _poolTimer: false,
    _resize: function(b, d, a) {
        var g = {
            x: -((b - this.size.width) / 2),
            y: -((d - this.size.height) / 2)
        };
        this.size.width = b;
        this.size.height = d;
        this.fakeDiv.style.width = b + "px";
        this.fakeDiv.style.height = d + "px";
        this.viewportInfo.canvasSize.width = b;
        this.viewportInfo.canvasSize.height = d;
        this.realDiv.style.position = "absolute";
        this.realDiv.style.width = this.viewportInfo.canvasSize.width + "px";
        this.realDiv.style.height = this.viewportInfo.canvasSize.height + "px";
        this.realDiv.style.left = "0px";
        this.realDiv.style.top = "0px";
        if (this.viewportInfo.mapConfig == null || (g.x == 0 && g.y == 0)) {
            return
        }
        this.vectorLayer.setDisplay(false);
        if (this._poolTimer) {
            clearTimeout(this._poolTimer);
            this._poolTimer = false
        }
        this.viewportInfo.canvasSize.width = b;
        this.viewportInfo.canvasSize.height = d;
        this.viewportLayer.setTopLeft({
            x: 0,
            y: 0
        });
        if (this.viewportInfo.centerMetric.x == 0) {
            return
        }
        this.panCenter(g);
        this.getInfo(true);
        var f = this.canvasInfo.mapRowCols;
        var e = this.viewportInfo.mapConfig.createList(f.left, f.top, f.right, f.bottom);
        this.canvasInfo.mapList = e;
        this.mapLayer.setEnable(true);
        this.mapLayer._draw(this.canvasInfo, f.top, f.left, f.bottom, f.right);
        var i = this,
            c = function() {
                i.getInfo(true);
                i.zoomLayer.setWidth(i.viewportInfo.canvasSize);
                i.mapContainer.setWidth(i.viewportInfo.canvasSize);
                i.markerStaticLayer.setEnable(true);
                i.container.draw(i.canvasInfo, f.top, f.left, f.bottom, f.right);
                i.vectorLayer.setDisplay(true)
            };
        this._poolTimer = setTimeout(c, 200)
    }
};
SD.genmap.BaseMap = function(b, a) {
    this.dom = typeof b == "string" ? document.getElementById(b) : b;
    this.zoom = 1;
    this.center = new GeoPoint(106.915305, -6.09949764);
    this.size = new Size(400, 400);
    this.bingCredentials = false;
    this.useGoogle = false;
    this.draggable = true;
    this.mapManager = new MapManager();
    this.scrollwheel = true;
    this.enableDefaultLogo = true;
    this.showCopyright = true;
    this.loadFromShift = false;
    this.navigation = null;
    this.nodes = {};
    this.navigation = [];
    this.__api = false;
    this.activeIndex = "";
    this.emptyLatLng = false;
    if (!a.center) {
        this.emptyLatLng = true
    }
    SD.apply(this, a);
    this.viewport = new ViewportControl(this);
    if (this.resize) {
        this.size.width = this.resize.w;
        this.size.height = this.resize.h
    }
    this.initialize()
};
SD.genmap.BaseMap.prototype = {
    initialize: function() {
        this.shiftingMap();
        if (EventManager._api == null) {
            EventManager._api = this
        }
    },
    getMapSd: function(f, e, d) {
        var c = f || this.zoom;
        var b = e || this.center.lon;
        var a = d || this.center.lat;
        return this.mapManager.getMapLayerByLevel(c, b, a)
    },
    isMapSd: function(d, c, b) {
        var a = this.getMapSd(d, c, b);
        return a && a.mapTileHeight <= 345
    },
    onLoad: function() {
        this.__call("onLoad")
    },
    shiftingMap: function(a) {
        this.viewportInfo = this.viewport.viewportInfo;
        this.canvasInfo = this.viewport.canvasInfo;
        var c = {
            dom: this.dom,
            viewport: this.viewport,
            viewportInfo: this.viewport.viewportInfo,
            canvasInfo: this.viewport.canvasInfo,
            zoom: this.zoom,
            center: this.center,
            size: this.size,
            mapManager: this.mapManager,
            draggable: this.draggable,
            baseApi: this,
            bingCredentials: this.bingCredentials,
            fromScroll: a ? true : false
        };
        if (this.isMapSd()) {
            this.__initApi("sd", c)
        } else {
            if (this.bingCredentials) {
                this.__initApi("bing", c)
            } else {
                var b = this.mapManager.getMapLayerByAllLevel(c.center.lon, c.center.lat);
                if (b) {
                    c.zoom = b.realLevel;
                    this.useGoogle = this.enableGoogle;
                    if (this.useGoogle) {
                        this.__initApi("google", c)
                    } else {
                        this.__initApi("sd", c)
                    }
                }
            }
        }
    },
    __initApi: function(index, o) {
        index = index.toUpperCase();
        if (!this.nodes.hasOwnProperty(index)) {
            var api = false;
            eval("api = SD.genmap." + index + "BaseMap");
            if (api) {
                this.__api = new api(o);
                this.nodes[index] = this.__api;
                if (this.navigation.length > 0 && !this.__api.navigation) {
                    for (var i = 0; i < this.navigation.length; i++) {
                        this.__api.addControl(new this.navigation[i].constructor(this))
                    }
                }
            }
        }
        this.loadFromShift = true;
        this.activeIndex = index;
        this.__api = this.nodes[index];
        this.__api.apply(o);
        this.showActive()
    },
    setCenterFromOffset: function(a, b) {
        if (a == null) {
            return
        }
        if (b == null || b == undefined) {
            b = this.viewport.viewportInfo.scale
        }
        this.viewport.wheelCenter(b, null, a);
        this.center = this.viewport.viewportInfo.centerGeo;
        if (this.viewport.projection == null) {
            this.viewport.updateMapLayerByLevel(this.zoom);
            this.viewport.wheelCenter(this.viewport.viewportInfo.scale, null, a);
            this.center = this.viewport.viewportInfo.centerGeo
        }
    },
    pushElement: function(a) {
        return this.__call("pushElement", a)
    },
    pushEvent: function(c, b, a) {
        this.__call("pushEvent", {
            el: c,
            type: b,
            fc: a
        })
    },
    removeElement: function(a) {
        return this.__call("removeElement", a)
    },
    showActive: function() {
        if (!this.loadFromShift) {
            return
        }
        this.loadFromShift = false;
        this.nodes[this.activeIndex].setDisplay(true);
        this.nodes[this.activeIndex].resizeViewport(this.size.width, this.size.height);
        for (var a in this.nodes) {
            if (this.nodes.hasOwnProperty(a) && a != this.activeIndex) {
                this.nodes[a].setDisplay(false)
            }
        }
    },
    __call: function() {
        var b = arguments,
            d = false;
        if (b.length > 0 && this.__api && this.__api[b[0]]) {
            if (b.length > 3) {
                var e = [];
                if (b.slice) {
                    e = b.slice(0, 1)
                } else {
                    for (var c = 1; c < b.length; c++) {
                        e.push(b[c])
                    }
                }
                d = this.__api[b[0]](e)
            } else {
                d = this.__api[b[0]](b[1] || null, b[2] || null)
            }
            this.__updateFromBase(this.__api)
        }
        return d
    },
    __updateFromBase: function(a) {
        if (this.viewport != undefined && a != null) {
            a.viewportInfo = this.viewport.viewportInfo;
            a.infoWindow = this.viewport.infoWindow;
            a.zoom = a.viewportInfo.levelIndex;
            a.center = a.viewportInfo.centerGeo;
            a.canvasInfo = this.viewport.canvasInfo
        }
    },
    refresh: function() {
        this.__call("refresh");
        this._updateInfo()
    },
    setDragging: function(a) {
        this.__call("setDragging", a)
    },
    _updateInfo: function(a) {
        if (a == undefined) {
            a = this.viewport
        }
        this.viewportInfo = a.viewportInfo;
        this.infoWindow = a.infoWindow;
        this.zoom = this.viewportInfo.levelIndex;
        this.center = this.viewportInfo.centerGeo;
        if (a.canvasInfo) {
            this.canvasInfo = a.canvasInfo
        }
    },
    zoomIn: function() {
        this.setZoom(this.zoom + 1, true)
    },
    zoomOut: function() {
        this.setZoom(this.zoom - 1, true)
    },
    fromLatLngToCanvasPixel: function(a) {
        return this.__call("fromLatLngToCanvasPixel", a)
    },
    fromLatLngToContainerPixel: function(a) {
        return this.__call("fromLatLngToContainerPixel", a)
    },
    fromContainerPixelToLatLng: function(a) {
        return this.__call("fromContainerPixelToLatLng", a)
    },
    isHaveMap: function(c, g, e) {
        var f = false;
        var b = g || this.center.lon;
        var a = e || this.center.lat;
        var h = this.mapManager.getMapLayerByLevel(c, b, a);
        if (h) {
            f = true
        } else {
            if (this.nodes.BING) {
                f = this.nodes.BING.zoomScale._scale[c] ? true : false
            } else {
                var d = new SD.genmap.BingScale();
                f = d._scale[c] ? true : false
            }
        }
        return f
    },
    setZoom: function(b, a) {
        var c = this.isHaveMap(b);
        if (c) {
            this.zoom = b;
            this.shiftingMap()
        }
        return c
    },
    getObject: function() {
        return this.__call("getObject")
    },
    setCenter: function(a, b) {
        this.__call("setCenter", a, b);
        this.zoom = b;
        this.center = a;
        this.shiftingMap()
    },
    getCenter: function() {
        return this.__call("getCenter")
    },
    setInfoWindow: function(a) {
        this.__call("setInfoWindow", a)
    },
    panBy: function(b, a) {
        this.__call("panBy", b, a)
    },
    panTo: function(a) {
        this.__call("panTo", a)
    },
    resizeViewport: function(a, b) {
        this.size = new Size(a, b);
        this.__call("resizeViewport", a, b);
        this.dom.style.width = a + "px";
        this.dom.style.height = b + "px"
    },
    getBounds: function() {
        return this.__call("getBounds")
    },
    addControl: function(a) {
        this.navigation.push(a);
        this.__call("addControl", a)
    },
    addLogo: function(c, b, a, d) {
        this.__call("addLogo", c, b, a, d)
    },
    disableScrollWheelZoom: function() {
        this.viewport.disableMouseWheel = true
    }
};
SD.genmap.Map = function(b, a) {
    return SD.genmap.Map.getInstance(b, a)
};
SD.genmap.Map.getIndex = function(a) {
    a = typeof a == "string" ? document.getElementById(a) : a;
    return a.id
};
SD.genmap.Map.getInstance = function(c, b) {
    var a = this.getIndex(c);
    if (SD.genmap.Map.instance[a] == null || !(SD.genmap.Map.instance[a] instanceof SD.genmap.BaseMap)) {
        SD.genmap.Map.i = new SD.genmap.BaseMap(c, b);
        SD.genmap.Map.instance[a] = SD.genmap.Map.i
    }
    return SD.genmap.Map.instance[a]
};
SD.genmap.Map.instance = [];
SD.genmap.Map.i = null;
SD.genmap.BingScale = function() {
    this._scale = {
        1: [1, 2],
        2: [3],
        3: [4],
        4: [5],
        5: [6, 7, 8],
        6: [9, 10],
        7: [11],
        8: [12],
        9: [13],
        10: [14],
        11: [15],
        12: [16],
        13: [17, 18, 19, 20]
    }
};
SD.genmap.Bingqueue = function() {
    this.obj = null;
    this.fn = null;
    this.params = []
};
SD.genmap.BingScale.prototype = {
    get: function(b) {
        var a = this._scale[b];
        if (a != undefined && a.length) {
            a = this._scale[b];
            return a[0]
        }
        return 1
    },
    getSd: function(c) {
        var e = parseInt(c.getZoom());
        for (var d in this._scale) {
            var a = parseInt(d);
            if (a > 0) {
                for (var b = 0; b < this._scale[d].length; b++) {
                    if (this._scale[d][b] == e) {
                        return a
                    }
                }
            }
        }
        return 1
    }
};

function onScriptLoadBing() {
    SD.genmap.Map.i.onLoad()
}
SD.genmap.BINGBaseMap = function(b) {
    this.zoomScale = new SD.genmap.BingScale();
    this.markers = new SD.genmap.OverlayManager();
    this.lines = new SD.genmap.OverlayManager();
    this.offsetCenter = null;
    this.offsetPt = {};
    this.prevZoom = -1;
    this.prevOpt = {};
    this.dom = new StdDiv();
    this.dom.cleanAbsolute();
    this.dom.setId("bing_" + Math.round(Math.random() * 100));
    this.dom.appendToDom(b.dom);
    this.queue = [];
    this.__b = false;
    var d = "http://ecn.dev.virtualearth.net/mapcontrol/mapcontrol.ashx?v=7.0&onScriptLoad=onScriptLoadBing";
    var c = document.getElementsByTagName("head")[0] || document.documentElement;
    var a = document.createElement("script");
    a.src = d;
    c.insertBefore(a, c.firstChild);
    this.viewport = {
        hintLayer: {},
        draw: function() {},
        OnLevelChanged: new EventDelegates(),
        OnDraw: new EventDelegates(),
        OnEndDrag: new EventDelegates(),
        OnEndMove: new EventDelegates()
    };
    delete b.dom;
    SD.apply(this, b)
};
SD.genmap.BINGBaseMap.prototype = {
    onLoad: function() {
        var a = {
            backgroundColor: Microsoft.Maps.Color.fromHex("#CCFFCC"),
            credentials: this.bingCredentials,
            zoom: this.zoomScale.get(this.zoom),
            center: new Microsoft.Maps.Location(this.center.lat, this.center.lon),
            enableSearchLogo: false,
            enableClickableLogo: false,
            showCopyright: false,
            showScalebar: false,
            showDashboard: false
        };
        this.__b = new Microsoft.Maps.Map(this.dom.div, a);
        this._initEvents();
        this._initLayers();
        if (this.size) {
            this.__b.setOptions({
                height: this.size.height,
                width: this.size.width
            })
        }
        this.apply(this.prevOpt);
        this.prevZoom = a.zoom;
        if (this.queue.length > 0) {
            this.runQueue()
        }
    },
    runQueue: function() {
        var b = "";
        var a = this.queue.length;
        for (var c = 0; c < a; c++) {
            this.queue[c].params.push(this.__g);
            this.queue[c].fn.apply(this.queue[c].obj, this.queue[c].params)
        }
        this.queue = []
    },
    _initLayers: function() {
        var c;
        for (var b = 0; b < SD.mgr.__marker.i; b++) {
            for (var a = 0; a < SD.mgr.__marker.a[b].node.length; a++) {
                c = SD.mgr.__marker.a[b].node[a];
                c.b = this._addMarker(c)
            }
        }
        for (b = 0; b < SD.mgr.__polyline.i; b++) {
            for (a = 0; a < SD.mgr.__polyline.a[b].node.length; a++) {
                c = SD.mgr.__polyline.a[b].node[a];
                this._addLine(c)
            }
        }
    },
    _initEvents: function() {
        var b = this;
        var c = false;
        Microsoft.Maps.Events.addHandler(this.__b, "viewchangeend", function() {
            b._updateInfo();
            if (b.viewport.OnLevelChanged) {
                b.viewport.OnLevelChanged.triggered({
                    levelIndex: b.zoomScale.getSd(b.__b)
                })
            }
            if (b.prevZoom != -1 && b.prevZoom != b.__b.getZoom()) {
                if (b.baseApi.isMapSd()) {
                    if (c) {
                        var e = b.baseApi.getMapSd().scale;
                        b.baseApi.setCenterFromOffset(b.geoCursor, e)
                    }
                    b.baseApi.shiftingMap()
                }
                b.prevZoom = b.__b.getZoom()
            }
        });
        Microsoft.Maps.Events.addHandler(this.__b, "mousewheel", function(g) {
            if (g.targetType == "map") {
                var f = new Microsoft.Maps.Point(g.pageX, g.pageY, Microsoft.Maps.PixelReference.page);
                var h = g.target.tryPixelToLocation(f, Microsoft.Maps.PixelReference.page);
                b.geoCursor = {
                    lon: h.longitude,
                    lat: h.latitude,
                    x: g.pageX,
                    y: g.pageY
                }
            }
            c = true
        });
        var d = {
            x: 0,
            y: 0
        };
        Microsoft.Maps.Events.addHandler(this.__b, "mousedown", function(f) {
            d.x = f.originalEvent.clientX;
            d.y = f.originalEvent.clientY
        });
        var a = false;
        Microsoft.Maps.Events.addHandler(this.__b, "mouseup", function(g) {
            if (g.originalEvent.clientX != d.x || g.originalEvent.clientY != d.y) {
                b._updateInfo();
                if (b.viewport.OnEndDrag) {
                    b.viewport.OnEndDrag.triggered({
                        levelIndex: b.zoomScale.getSd(b.__b)
                    })
                }
            } else {
                var f = new Date().getTime();
                var i = a || f + 1;
                var h = f - i;
                if (h < 500 && h > 1 && g.isSecondary) {
                    b.zoomOut()
                }
                a = f
            }
        });
        Microsoft.Maps.Events.addHandler(this.__b, "dblclick", function(f) {
            if (SD.isIPhone && f.isTouchEvent) {
                b.zoomOut()
            }
            c = false
        });
        Microsoft.Maps.Events.addHandler(this.__b, "tiledownloadcomplete", function() {
            if (b.baseApi && b.baseApi.__api instanceof SD.genmap.BINGBaseMap) {
                b.baseApi.showActive()
            }
        })
    },
    _initMarkerEvent: function(c, d) {
        if (c && d.events) {
            for (var a in d.events) {
                if (d.events.hasOwnProperty(a)) {
                    for (var b in d.events[a]) {
                        if (!Object.prototype[b]) {
                            EventManager.add(c, a, d.events[a][b])
                        }
                    }
                }
            }
            return true
        }
        return false
    },
    _addMarker: function(e) {
        if (e == undefined || e.position == null || !e.position.lon) {
            return false
        }
        var c = e.icon.getObject();
        var d = this.markers._isExist(e);
        if (d && c.events) {
            this._initMarkerEvent(d.div, c);
            return false
        }
        var l = new Microsoft.Maps.Location(e.position.lat, e.position.lon);
        var m = e.icon.__sprite ? (e.icon.iconSize.height < 30 ? 30 : e.icon.iconSize.height) : e.icon.iconSize.height;
        var b = e.icon.__sprite ? (e.icon.iconSize.width < 25 ? 25 : e.icon.iconSize.width) : e.icon.iconSize.width;
        var a = {
            height: m,
            width: b,
            anchor: new Microsoft.Maps.Point(e.icon.iconAnchor.x, e.icon.iconAnchor.y),
            draggable: e.draggable
        };
        if (e.icon) {
            if (!e.icon.__sprite) {
                a.icon = e.icon.image
            } else {
                a.icon = ""
            }
        }
        var g = new Microsoft.Maps.Pushpin(l, a);
        g._guid = e.guid;
        this.__b.entities.push(g);
        var h = this;
        var j = setInterval(function() {
            if (!e.icon.__sprite) {
                clearInterval(j)
            }
            if (e.icon.__sprite && g.cm1001_er_etr) {
                if (g.cm1001_er_etr.dom) {
                    var i = c.cloneNode(true);
                    i = SD.util.assignSpriteEvent(i);
                    i.setBWidth = function(n) {
                        g.setOptions({
                            width: n,
                            visible: true
                        })
                    };
                    i.setBHeight = function(n) {
                        g.setOptions({
                            height: n,
                            visible: true
                        })
                    };
                    if (i.events) {
                        i.events = null
                    }
                    g.div = i;
                    i.style.position = "";
                    i.style.top = "";
                    i.style.left = "";
                    i.style.cursor = "pointer";
                    g.cm1001_er_etr.dom.appendChild(i);
                    if (c.events) {
                        h._initMarkerEvent(g.div, c)
                    }
                }
                clearInterval(j)
            }
        }, 500);
        if (c.events && !e.icon.__sprite) {
            for (var f = 0; f < c.events.length; f++) {
                var k = c.events[f];
                Microsoft.Maps.Events.addHandler(g, k, g.div["on" + k[f]])
            }
        }
        this.markers._add(g);
        return g
    },
    _addLine: function(b) {
        if (b == undefined || b.points == null || b.points.length == 0) {
            return false
        }
        var c = b.convertPoints(Microsoft.Maps.Location, true);
        var a = new Microsoft.Maps.Polyline(c, {
            strokeColor: new Microsoft.Maps.Color(60, 42, 83, 247),
            strokeThickness: b.size * 4
        });
        this.__b.entities.push(a);
        this.lines._add(a);
        return a
    },
    apply: function(b) {
        this.prevOpt = b;
        if (!this.__b) {
            return
        }
        if (b.fromScroll && b.baseApi) {
            var a = b.viewport.getCursorDistanceFromCenter();
            this.__b.setView({
                centerOffset: new Microsoft.Maps.Point(-a.x, -a.y),
                center: new Microsoft.Maps.Location(b.center.lat, b.center.lon),
                zoom: this.zoomScale.get(b.zoom)
            })
        } else {
            this.setCenter(b.center, b.zoom)
        }
    },
    pushElement: function(a) {
        if (!this.__b) {
            return false
        }
        var b;
        if (a.icon && a.guid) {
            b = this._addMarker(a)
        } else {
            if (a._polyline) {
                b = this._addLine(a)
            } else {
                this.__b.entities.push(a);
                b = a
            }
        }
        return b
    },
    pushEvent: function(a) {
        if (!this.__b) {
            return
        }
        if (a != undefined) {
            if (a.el && a.el.icon && a.el.guid) {
                this._addMarker(a.el)
            } else {
                if (a.el._polyline) {
                    this._addLine(a.el)
                }
            }
        }
    },
    removeElement: function(a) {
        var b;
        if (a.icon && a.guid) {
            b = this.markers._isExist(a);
            this.markers._remove(a)
        } else {
            if (a._polyline) {
                b = this.lines._isExist(a);
                this.lines._remove(a)
            }
        }
        if (b) {
            this.__b.entities.remove(b)
        }
    },
    refresh: function() {},
    setDisplay: function(a) {
        this.dom.setDisplay(a)
    },
    setDragging: function(a) {
        this.__b.setOptions({
            disableMouseInput: a
        })
    },
    _getLocation: function(a) {
        if (!(a instanceof Microsoft.Maps.Location)) {
            a = new Microsoft.Maps.Location(a.lat, a.lon)
        }
        return a
    },
    _updateInfo: function() {
        if (this.baseApi && this.__b) {
            var a = this.__b;
            var c = this.__b.getBounds();
            this.baseApi.center = this.getCenter();
            this.baseApi.viewportInfo.geoView = new Rectangle(c.getWest(), c.getNorth(), c.getEast(), c.getSouth());
            this.baseApi.viewportInfo.centerGeo = this.baseApi.center;
            this.baseApi.canvasInfo = this.baseApi.viewportInfo;
            this.baseApi.size = {
                width: a.getWidth(),
                height: a.getHeight()
            };
            this.baseApi.zoom = this.zoomScale.getSd(a)
        }
    },
    zoomIn: function() {
        this.setZoom(this.zoom + 1, true)
    },
    zoomOut: function() {
        this.setZoom(this.zoom - 1, true)
    },
    fromLatLngToCanvasPixel: function(a) {
        return this.fromLatLngToContainerPixel(a)
    },
    fromLatLngToContainerPixel: function(b) {
        var a = this.__b.tryLocationToPixel(this._getLocation(b), Microsoft.Maps.PixelReference.page);
        if (a != null) {
            return a
        }
        return false
    },
    fromContainerPixelToLatLng: function(a) {
        var b = this.__b.tryPixelToLocation(new Microsoft.Maps.Point(a.x, a.y), Microsoft.Maps.PixelReference.page);
        if (b != null) {
            return new GeoPoint(b.longitude, b.latitude)
        }
        return false
    },
    setZoom: function(b, a) {
        if (b <= this.mapManager.getLength() && 1 <= b) {
            this.zoom = b;
            this.__b.setView({
                zoom: this.zoomScale.get(b)
            });
            if (this.baseApi) {
                this.baseApi.zoom = this.zoom
            }
        }
    },
    getObject: function() {
        return false
    },
    setCenter: function(a, b) {
        if (!this.__b) {
            return
        }
        if (!(a instanceof Microsoft.Maps.Location)) {
            a = new Microsoft.Maps.Location(a.lat, a.lon)
        }
        this.__b.setView({
            center: a,
            zoom: this.zoomScale.get(b)
        })
    },
    getCenter: function() {
        if (!this.__b) {
            return false
        }
        var a = this.__b.getCenter();
        return {
            lon: a.longitude,
            lat: a.latitude
        }
    },
    setInfoWindow: function(a) {
        this.viewport.hintLayer.replaceNode(this.viewport.infoWindow, a);
        this.viewport.infoWindow = a;
        this.infoWindow = a
    },
    panBy: function(b, a) {
        var c = this.__b.getCenter();
        this.__b.setView({
            animate: true,
            centerOffset: new Microsoft.Maps.Point(b, a),
            center: c
        })
    },
    panTo: function(a) {
        this.__b.setView({
            animate: true,
            center: new Microsoft.Maps.Location(a.lat, a.lon)
        })
    },
    resizeViewport: function(c, e, f) {
        if (!this.__b && !f) {
            var b = new SD.genmap.Bingqueue();
            b.obj = this;
            b.fn = this.resizeViewport;
            b.params.push(c, e);
            this.queue.push(b);
            return false
        }
        if (f) {
            this.__b = f
        }
        if (this.__b.getWidth() != c || this.__b.getHeight() != e) {
            var d = {
                height: e,
                width: c
            };
            this.dom.setWidth(d);
            this.__b.setOptions(d)
        }
    },
    getBounds: function() {
        return this.__b.getBounds()
    },
    addControl: function(a) {
        a.control = MapControl.getInstance(this.baseApi || this, this.dom);
        this.dom.add(a.getNavigation());
        this.navigation = a
    },
    addLogo: function() {
        var c = arguments[0] ? arguments[0] : arguments;
        var f = c[0],
            d = c[1],
            b = c[2],
            g = c[3];
        var e = new SD.util.createImg("", f, "", "", d.width + "px", d.height + "px", "absolute");
        if (b == SD.POSITION_TOP_RIGHT) {
            e.style.top = "0px";
            e.style.right = "0px"
        } else {
            if (b == SD.POSITION_TOP_LEFT) {
                e.style.top = "0px";
                e.style.left = "0px"
            } else {
                if (b == SD.POSITION_BOTTOM_RIGHT) {
                    e.style.bottom = "0px";
                    e.style.right = "0px"
                } else {
                    if (b == SD.POSITION_BOTTOM_LEFT) {
                        e.style.bottom = "0px";
                        e.style.left = "0px"
                    }
                }
            }
        }
        this.viewport.fakeDiv.appendChild(e);
        if (g) {
            e.style.cursor = "pointer";
            EventManager.add(e, "click", function() {
                window.open("http://" + g)
            })
        }
    }
};
SD.genmap.GOOGLEScale = {
    1: 1,
    2: 3,
    3: 4,
    4: 4,
    5: 8,
    6: 10,
    7: 11,
    8: 12,
    9: 14,
    10: 15,
    11: 15,
    12: 17,
    13: 17
};
SD.genmap.GOOGLEqueue = function() {
    this.obj = null;
    this.fn = null;
    this.params = []
};
SD.genmap.GOOGLEObject = {
    marker: null,
    infowindow: null
};
SD.genmap.GOOGLEBaseMap = function(b) {
    this.__g = false;
    this.__google = false;
    this.markers = [];
    this.queue = [];
    this.realDom = b.dom;
    this.dom = new StdDiv();
    this.dom.cleanAbsolute();
    this.dom.setId("google_" + Math.round(Math.random() * 100));
    this.dom.appendToDom(b.dom);
    var d = "http://maps.googleapis.com/maps/api/js?sensor=false&callback=googleOnLoad";
    var c = document.getElementsByTagName("head")[0] || document.documentElement;
    var a = document.createElement("script");
    a.src = d;
    c.insertBefore(a, c.firstChild);
    delete b.dom;
    SD.apply(this, b)
};

function googleOnLoad() {
    SD.genmap.Map.i.onLoad()
}
SD.genmap.GOOGLEBaseMap.prototype = {
    onLoad: function() {
        var b = new google.maps.LatLng(this.center.lat, this.center.lon);
        var a = {
            zoom: SD.genmap.GOOGLEScale[this.zoom],
            center: b,
            panControl: true,
            streetViewControl: false,
            mapTypeControl: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        this.__g = new google.maps.Map(this.dom.div, a);
        this._initLayers();
        if (this.queue.length > 0) {
            this.runQueue()
        }
    },
    setDisplay: function(a) {
        this.dom.setDisplay(a)
    },
    runQueue: function() {
        var b = "";
        var a = this.queue.length;
        for (var c = 0; c < a; c++) {
            this.queue[c].params.push(this.__g);
            this.queue[c].fn.apply(this.queue[c].obj, this.queue[c].params)
        }
        this.queue = []
    },
    _initLayers: function() {
        var c;
        for (var b = 0; b < SD.mgr.__marker.i; b++) {
            for (var a = 0; a < SD.mgr.__marker.a[b].node.length; a++) {
                c = SD.mgr.__marker.a[b].node[a];
                if (this.realDom.getAttribute("id") == SD.mgr.__marker.a[b].map.dom.getAttribute("id")) {
                    c.b = this._addMarker(c, b, a)
                }
            }
        }
    },
    apply: function(a) {
        if (!this.__g) {
            return
        }
    },
    resizeViewport: function(a, b) {
        if (!this.__g) {
            return
        }
        google.maps.event.trigger(this.__g, "resize")
    },
    setInfoWindow: function(b) {
        if (!this.__g) {
            return
        }
        if (!SD.genmap.GOOGLEObject.infowindow) {
            var a = new google.maps.InfoWindow({
                content: b.div.innerHTML
            });
            SD.genmap.GOOGLEObject.infowindow = a;
            b.div.parentNode.removeChild(b.div)
        }
        SD.genmap.GOOGLEObject.infowindow.open(this.__g, SD.genmap.GOOGLEObject.marker)
    },
    pushElement: function(a, b) {
        if (!this.__g && !b) {
            return false
        }
        if (b) {
            this.__g = b
        }
        var c;
        if (a.icon && a.guid) {
            c = this._addMarker(a)
        }
        return c
    },
    _addMarker: function(d) {
        var f = new google.maps.LatLng(d.position.lat, d.position.lon);
        var b = new google.maps.Marker({
            position: f,
            map: this.__g,
            icon: d.icon.image,
            draggable: d.draggable
        });
        var e = d.icon.getObject();
        if (d.draggable) {
            google.maps.event.addListener(b, "dragend", function() {
                d.setPosition({
                    lon: b.getPosition().lng(),
                    lat: b.getPosition().lat()
                })
            })
        }
        this.markers.push(b);
        SD.genmap.GOOGLEObject.marker = b;
        if (b && e.events) {
            for (var a in e.events) {
                if (e.events.hasOwnProperty(a)) {
                    for (var c in e.events[a]) {
                        if (!Object.prototype[c]) {
                            google.maps.event.addListener(b, a, e.events[a][c])
                        }
                    }
                }
            }
        }
        return b
    },
    setCenter: function(c, d, e) {
        if (!this.__g && !e) {
            var b = new SD.genmap.GOOGLEqueue();
            b.obj = this;
            b.fn = this.setCenter;
            b.params.push(c, d);
            return false
        }
        if (e) {
            this.__g = e
        }
        var f = new google.maps.LatLng(c.lat, c.lon);
        this.__g.setCenter(f);
        this.__g.setZoom(d)
    },
    pushEvent: function(b, a) {
        if (!this.__g && !a) {
            return
        }
    }
};
SD.genmap.SDBaseMap = function(a) {
    this.viewport = {
        draw: function() {}
    };
    SD.apply(this, a);
    this.size = new Size(0, 0);
    this.viewport.setLevel(a.zoom);
    this.viewport.setCenter(a.center, true);
    this._initEvents()
};
SD.genmap.SDBaseMap.prototype = {
    _initEvents: function() {
        var a = this;
        var b = function() {
            a.viewport.defaultTool.animateZoom.reset();
            a.viewport.defaultTool.animateZoom.go({
                viewport: a.viewport,
                step: 4,
                scaleIncrement: 0.8,
                callback: function(c) {
                    a.renderOnChangeLevel(c, true)
                }
            })
        };
        this.viewport.OnEndWheel.register(function(d) {
            var c = a.isBingMapAvailable(d, d.levelIndex);
            if (c) {
                b()
            }
        });
        this.viewport.OnDoubleClick.register(function(e) {
            var f = e.lastCursorDelta;
            var c = e.levelIndex + (f > 0 ? 1 : -1);
            var d = a.isBingMapAvailable(e, c);
            if (d) {
                b()
            }
        });
        this.viewport.mapLayer.OnCompleted.register(function(c) {
            if (a.baseApi && a.baseApi.isMapSd()) {
                a.baseApi.showActive()
            }
        });
        this.viewport.initEvents()
    },
    renderOnChangeLevel: function(b, a) {
        if (b) {
            if (b.mapConfig && b.mapConfig.mapTileHeight <= 345) {
                this.baseApi.zoom = b.levelIndex + (b.lastCursorDelta > 0 ? 1 : -1)
            } else {
                this.baseApi.zoom = b.levelIndex
            }
        }
        this.baseApi.center = a ? b.lastCursorWheel : b.centerGeo;
        b.levelIndex = this.baseApi.zoom;
        this.baseApi.shiftingMap(a)
    },
    isBingMapAvailable: function(f, a) {
        var b = this.mapManager.getLength();
        if (!(a > 1 && a < b)) {
            return false
        }
        var e = this.baseApi.isHaveMap(a, f.lastCursorLatLon.lon, f.lastCursorLatLon.lat);
        var c = this.viewport.defaultTool.animateZoom.aScale.inValid();
        var g = !this.baseApi.isMapSd(a, f.lastCursorLatLon.lon, f.lastCursorLatLon.lat);
        if (c && (a == b - 1 || a == b)) {
            return false
        }
        var d = (c || g);
        return d && e && a >= 4 && this.baseApi.bingCredentials
    },
    apply: function(a) {
        this.setCenter(a.center, a.zoom)
    },
    pushElement: function(a) {
        return false
    },
    removeElement: function(a) {
        return false
    },
    refresh: function() {
        this.viewport.draw()
    },
    setDisplay: function(a) {
        this.viewport.dom.setDisplay(a);
        this.viewport.markerStaticLayer.setEnable(a)
    },
    setDragging: function(a) {
        this.viewport.ActiveTool(a == true ? this.viewport.defaultTool : false)
    },
    zoomIn: function() {
        this.setZoom(this.zoom + 1, true)
    },
    zoomOut: function() {
        this.setZoom(this.zoom - 1, true)
    },
    fromLatLngToCanvasPixel: function(a) {
        return this.canvasInfo.canvasGeoToScreen(a)
    },
    fromLatLngToContainerPixel: function(a) {
        return this.viewportInfo.viewportGeoToScreen(a)
    },
    fromContainerPixelToLatLng: function(a) {
        if (a == undefined) {
            a = this.viewportInfo.lastCursorPosDown
        }
        return this.viewportInfo.viewportScreenToGeo(a.x, a.y)
    },
    setZoom: function(c, b) {
        if (c <= this.mapManager.getLength() && 1 <= c) {
            this.zoom = c;
            this.viewport.setLevel(this.zoom);
            var a = this.viewport.updateMapLayerByLevel(c);
            if (a == undefined && b == true) {
                this.refresh()
            }
        }
        if (this.baseApi) {
            this.baseApi.zoom = this.zoom
        }
    },
    getObject: function() {
        return this.viewport.fakeDiv
    },
    setCenter: function(a, b) {
        if (this.center != a || this.zoom != b) {
            this.center = a;
            this.viewport.setCenter(this.center, false);
            this.setZoom(b, true)
        }
    },
    getCenter: function() {
        return this.viewportInfo.centerGeo
    },
    setInfoWindow: function(a) {
        this.viewport.hintLayer.replaceNode(this.viewport.infoWindow, a);
        this.viewport.infoWindow = a;
        this.infoWindow = a
    },
    panBy: function(b, a) {
        this.viewport.animatePanBy({
            x: b,
            y: a
        }, 10)
    },
    panTo: function(a) {
        this.viewport.animatePanTo(a)
    },
    resizeViewport: function(a, b) {
        if (this.size.width != a || this.size.height != b) {
            this.size.width = a;
            this.size.height = b;
            this.viewport._resize(a, b)
        }
    },
    getBounds: function() {
        if (!isNaN(this.viewportInfo.centerGeo.lon) && !isNaN(this.viewportInfo.centerGeo.lat)) {
            return this.viewportInfo.geoView
        }
        return false
    },
    addControl: function(a) {
        a.control = MapControl.getInstance(this.baseApi || this, this.viewport.dom);
        this.viewport.realDiv.appendChild(a.getNavigation());
        this.navigation = a
    },
    addLogo: function() {
        var c = arguments[0];
        var f = c[0],
            d = c[1],
            b = c[2],
            g = c[3];
        var e = new SD.util.createImg("", f, "", "", d.width + "px", d.height + "px", "absolute");
        if (b == SD.POSITION_TOP_RIGHT) {
            e.style.top = "0px";
            e.style.right = "0px"
        } else {
            if (b == SD.POSITION_TOP_LEFT) {
                e.style.top = "0px";
                e.style.left = "0px"
            } else {
                if (b == SD.POSITION_BOTTOM_RIGHT) {
                    e.style.bottom = "0px";
                    e.style.right = "0px"
                } else {
                    if (b == SD.POSITION_BOTTOM_LEFT) {
                        e.style.bottom = "0px";
                        e.style.left = "0px"
                    }
                }
            }
        }
        this.viewport.fakeDiv.appendChild(e);
        if (g) {
            e.style.cursor = "pointer";
            EventManager.add(e, "click", function() {
                window.open("http://" + g)
            })
        }
    }
};
SD.ns("SD.serv", "SD.serv.geocode", "SD.serv.data");
SD.serv.geocode = function(b) {
    this.list = ["my", "sg", "id", "ph"];
    this.meta = null;
    SD.serv.geocode.map = b;
    var a = {
        mode: "search",
        act: "all",
        output: "js",
        callback: "set_data",
        start: 0,
        limit: 20,
        country: "sg",
        profile: "template_1",
        show_additional: 0,
        no_total: 1,
        q: "orchard"
    };
    this.requestData = function(g, e) {
        if (this.list[g - 1] == undefined || this.list[g - 1] == null || typeof e !== "object") {
            return false
        }
        e.country = this.list[g - 1];
        if (e.d == 1) {
            e.profile = "template_2"
        }
        if (e.ctype == 1) {
            e.act = "location"
        } else {
            if (e.ctype == 2) {
                e.act = "business"
            }
        }
        SD.apply(a, e);
        parameters = "";
        for (var f in a) {
            parameters += f + "=" + a[f] + "&"
        }
        if (parameters.length > 0) {
            parameters = parameters.substr(0, parameters.length - 1)
        }
        var d = e.domain ? e.domain : SD.API_URL;
        var c = d + "/api/?" + parameters;
        this.meta = SD.util.addScript(c);
        this.meta.current = this.meta;
        this.meta.onload = function() {
            if (this.current.parentNode) {
                SD.util.removeScript(this.current)
            }
        }
    };
    this.requestDetail = function(i, g, c) {
        return false;
        if (this.list[i - 1] == undefined || this.list[i - 1] == null || i - 1 != 1 || typeof g !== "object") {
            return false
        }
        var e = "";
        for (var h in g) {
            e += h + "=" + g[h] + "&"
        }
        if (e.length > 0) {
            e = e.substr(0, e.length - 1)
        }
        if (c == undefined) {
            c = "3a1cbdf12f0e021c5772f9692e67ab28958f89d2"
        }
        var f = g.domain ? g.domain : SD.API_URL;
        var d = f + "/api/search/" + this.list[i - 1] + "_adv.php?" + e + "&api=" + c;
        this.meta = SD.util.addScript(d);
        this.meta.current = this.meta;
        this.meta.onload = function() {
            if (this.current.parentNode) {
                SD.util.removeScript(this.current)
            }
        }
    };
    this.reverse = function(h, f) {
        if (this.list[h - 1] == undefined || this.list[h - 1] == null || typeof f !== "object") {
            return false
        }
        var c = {
            mode: "nearby",
            act: "location",
            output: "js",
            callback: "set_data",
            start: 0,
            limit: 1,
            country: "sg",
            profile: "template_1",
            x: 103.82583767630031,
            y: 1.3105922623683273,
            dist: 1
        };
        f.country = this.list[h - 1];
        if (f.d == 1) {
            f.profile = "template_2"
        }
        if (f.ctype == 1) {
            f.act = "location"
        } else {
            if (f.ctype == 2) {
                f.act = "business"
            }
        }
        SD.apply(c, f);
        parameters = "";
        for (var g in c) {
            parameters += g + "=" + c[g] + "&"
        }
        if (parameters.length > 0) {
            parameters = parameters.substr(0, parameters.length - 1)
        }
        var e = f.domain ? f.domain : SD.API_URL;
        var d = e + "/api/?" + parameters;
        this.meta = SD.util.addScript(d);
        this.meta.current = this.meta;
        this.meta.onload = function() {
            if (this.current.parentNode) {
                SD.util.removeScript(this.current)
            }
        }
    };
    this.removeMouseClick = function() {
        if (this.eventLabel && this.eventLabel != null) {
            EventManager.remove(this.eventLabel, true)
        }
    };
    this.showSuggestionForm = function(c) {
        if (c) {
            document.getElementById("form").style.display = "";
            document.getElementById("fullscreen").style.display = ""
        } else {
            document.getElementById("form").style.display = "none";
            document.getElementById("fullscreen").style.display = "none"
        }
    };
    this.submitSuggestion = function() {
        var h = SD.serv.geocode.map.canvasInfo,
            g = SD.serv.geocode.map.viewportInfo.projection,
            f = SD.serv.geocode.map.viewportInfo.lastCursorLatLon;
        mt = g.geoToMetric(f.lon, f.lat);
        var d = "http://test2.street-directory.com/api/index.php/suggestion/insert";
        var e = {
            street_no: document.getElementById("street_no").value,
            street_name: document.getElementById("street_name").value,
            place: document.getElementById("place").value,
            district: document.getElementById("district").value,
            postal: document.getElementById("postal").value,
            lon: f.lon,
            lat: f.lat,
            x: mt.x,
            y: mt.y,
            projection: g.name
        };
        requestNumber = JSONRequest.post(d, e, function(i, j, c) {
            console.log(i, j, c)
        })
    }
};
SD.serv.geocode.prototype.init = function() {
    var b = document.body.clientWidth,
        e = document.body.clientHeight;
    var c = e / 2 - 90,
        a = b / 2 - 200;
    var g = "<div id='form' style='background-color:#FFFFFF; width:350px; height:180px; padding:5px; z-index:999;position:absolute; display:none;top:" + c + "px;left:" + a + "px;'><table class='form' syle='font-family:Verdana, Arial, Helvetica, sans-serif;font-size:11px;' width='100%' border='0' cellpadding='2' cellspacing='0' bgcolor='#E9E9E9' style='border:1px solid #666666'><tr><td width='33%'>Street No </td><td width='1%'>&nbsp;</td><td width='66%'><input class='field' name='street_no' type='text' id='street_no'></td></tr><tr><td>Street Name </td><td>&nbsp;</td><td><input class='field' name='street_name' type='text' id='street_name'></td></tr><tr><td>Place Name </td><td>&nbsp;</td><td><input class='field' name='place' type='text' id='place'></td></tr><tr><td>District</td><td>&nbsp;</td><td><input class='field' name='district' type='text' id='district'></td></tr><tr><td>Postal</td><td>&nbsp;</td><td><input class='field' name='postal' type='text' id='postal'></td></tr><tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr><td>&nbsp;</td><td>&nbsp;</td><td><input name='Submit' type='button' id='Submit' value='Suggest' onClick='SD.serv.geocode.instance.submitSuggestion()'>&nbsp;<input name='Submit' type='button' id='Close' value='Close' onClick='SD.serv.geocode.instance.showSuggestionForm(false);'></td></tr></table></div><div id='fullscreen' style='position:absolute;top:0px;left:0px;width:100%;height:100%;background-color:#333333;opacity:.5;-moz-opacity: 0.50;filter: alpha(opacity=50);z-index:998;display:none;'></div>";
    var i = document.createElement("div");
    i.innerHTML = g;
    document.body.appendChild(i);
    var f = new SD.genmap.GInfoWindow({
        size: {
            width: 260,
            height: 100
        },
        map: SD.serv.geocode.map,
        content: ""
    });
    SD.serv.geocode.map.setInfoWindow(f);
    SD.serv.geocode.instance = this;
    return EventManager.add(SD.serv.geocode.map, "mousedown", function(j) {
        if (SD.util.getMouseButton(j) == "RIGHT") {
            var h = SD.serv.geocode.map.fromLatLngToCanvasPixel(SD.serv.geocode.map.viewportInfo.lastCursorLatLon);
            var d = SD.serv.geocode.map.viewportInfo.lastCursorLatLon.lon.toString().substr(0, 10);
            var k = SD.serv.geocode.map.viewportInfo.lastCursorLatLon.lat.toString().substr(0, 8);
            SD.serv.geocode.map.infoWindow.open(h, "Current position : " + d + "," + k + ", Level : " + SD.serv.geocode.map.zoom + " <br><input type='button' value='Suggest Address' onclick='SD.serv.geocode.instance.showSuggestionForm(true)' />");
            SD.serv.geocode.map.infoWindow.visible = false;
            SD.serv.geocode.map.infoWindow.marker = null
        }
    })
};
SD.serv.geocode.map = null;
SD.serv.geocode.MY = 1;
SD.serv.geocode.JB = 1;
SD.serv.geocode.KV = 1;
SD.serv.geocode.MLK = 1;
SD.serv.geocode.PNG = 1;
SD.serv.geocode.SG = 2;
SD.serv.geocode.ID = 3;
SD.serv.geocode.JKT = 3;
SD.serv.geocode.BALI = 3;
SD.serv.geocode.BATAM = 3;
SD.serv.geocode.PH = 4;
SD.serv.geocode.instance = null;
var SDGeocode = SD.serv.geocode;
SD.serv.data = function(b) {
    this.meta = null;
    SD.serv.data.map = b;
    var a = {
        mode: "search",
        act: "business",
        profile: "sd_mobile",
        country: "sg",
        q: "orchard",
        show_additional: 0,
        no_total: 1,
        output: "js",
        callback: "set_data"
    };
    this.requestData = function(g, c) {
        var e = "q=" + g;
        if (typeof g == "object") {
            SD.apply(a, g);
            e = "";
            for (var h in a) {
                e += h + "=" + a[h] + "&"
            }
            if (e.length > 0) {
                e = e.substr(0, e.length - 1)
            }
        }
        var f = g.domain ? g.domain : SD.API_URL;
        var d = f + "/api/?" + e + "&api=" + c;
        this.meta = SD.util.addScript(d);
        this.meta.current = this.meta;
        this.meta.onload = function() {
            if (this.current.parentNode) {
                SD.util.removeScript(this.current)
            }
        }
    }
};
SD.extend(SD.serv.data, SD.serv.geocode);
SD.serv.data.map = null;
SD.serv.data.instance = null;
var SDService = SD.serv.data;
SD.serv.Kml = function(a, e) {
    SD.apply(this, new MapObject());
    var b = "sd.com kml";
    var c = Aes.Ctr.encrypt(a, b, 256);
    var d = SD.util.addScript(SD.API_URL + "kml_service/cek_kml/?kml=" + c);
    d.current = d;
    d.onload = function() {
        if (this.current.parentNode) {
            SD.util.removeScript(this.current)
        }
    };
    this.draw = function(g, j, k, h, i) {
        if (!this.enable) {
            return
        }
        this.clear();
        this.tiles = g.mapConfig.createList(k, j, i, h);
        this.setDisplay(true);
        this._draw(g, j, k, h, i)
    };
    this.getTileUrl = function(i, h, g) {
        return SD.API_URL + "kml_service/read_kml/?row=" + i + "&col=" + h + "&name=" + g.name + "&level=" + g.tileLevel + "&kml=" + c
    };
    this.reloadImage = function(j, i, g, h) {
        if (g == null) {
            return
        }
        g.style.display = "none";
        g.onCompleted = this.OnCompleted;
        g.onload = function() {
            this.style.display = ""
        };
        g.src = this.getTileUrl(j, i, h);
        g.style.filter = "Progid:DXImageTransform.Microsoft.AlphaImageLoader(src='" + g.src + "')"
    };
    e.viewport.container.addNode(this);
    var f = e.canvasInfo.mapRowCols;
    this.draw(e.canvasInfo, f.top, f.left, f.bottom, f.right)
};
var SDServiceXml = SD.serv.Kml;
SD.serv.Basejourney = function(options) {
    this.draggableStart = true;
    this.draggableEnd = true;
    SD.apply(this, options);
    if (this.map == null || this.map == undefined) {
        return
    }
    var _map = this.map;
    var _ob = this.dom;
    var _methods = "driving";
    var _vehicle = "both";
    var _css_used = false;
    var _sd_api = false;
    var _mNumbers = [];
    var _no_line = false;
    var _optional_obj = {};
    var _callback = undefined;
    var _success = undefined;
    var _get_start_end = false;
    var _date = null;
    var _time = null;
    var _q = null;
    var _pid_aid1 = null;
    var _pid_aid2 = null;
    var _no_cache = false;
    var _draggable_start = true;
    var _draggable_end = true;
    var _shortest_walking = false;
    var _driving_type = false;
    var _direction_result = {
        all: {
            label: null,
            result: null
        },
        driving: {
            label: null,
            result: null
        },
        taxi: {
            label: null,
            result: null
        },
        bus: {
            label: null,
            result: null
        },
        bustrain: {
            label: null,
            result: null
        }
    };
    var _temp_res = {
        label: null,
        result: null
    };
    this.pManager = new SD.genmap.PolylineManager({
        map: _map
    });
    this.mManager = new SD.genmap.MarkerStaticManager({
        map: _map
    });
    this.jLines = this.pManager.add(null, {
        color: "#0000ff",
        size: 3,
        opacity: "0.80"
    });
    var icon = new SD.genmap.MarkerImage();
    icon.iconSize = new Size(46, 52);
    icon.iconAnchor = new Point(24, 52);
    icon.image = "http://x1.sdimgs.com/img/journey/Start.png";
    var _p = this;
    this.sIcon = this.mManager.add({
        icon: icon,
        draggable: this.draggableStart,
        draggableMethod: {
            MouseUp: function(e, vc) {
                _p.reload(_p.sIcon.position, _p.eIcon.position)
            }
        }
    });
    icon.image = "http://x1.sdimgs.com/img/journey/End.png";
    this.eIcon = this.mManager.add({
        icon: icon,
        draggable: this.draggableEnd,
        draggableMethod: {
            MouseUp: function(e, vc) {
                _p.reload(_p.sIcon.position, _p.eIcon.position)
            }
        }
    });
    this._add_s_icon = function(x, y) {
        var icon = new SD.genmap.MarkerImage();
        icon.iconSize = new Size(46, 52);
        icon.iconAnchor = new Point(24, 52);
        icon.image = "http://x1.sdimgs.com/img/journey/Start.png";
        _p.sIcon = _p.mManager.add({
            icon: icon,
            position: new GeoPoint(x, y),
            draggable: _p.draggableStart,
            draggableMethod: {
                MouseUp: function(e, vc) {
                    _p.reload(_p.sIcon.position, _p.eIcon.position)
                }
            }
        })
    };
    this._add_e_icon = function(x, y) {
        var icon = new SD.genmap.MarkerImage();
        icon.iconSize = new Size(46, 52);
        icon.iconAnchor = new Point(24, 52);
        icon.image = "http://x1.sdimgs.com/img/journey/End.png";
        _p.eIcon = _p.mManager.add({
            icon: icon,
            position: new GeoPoint(x, y),
            draggable: _p.draggableEnd,
            draggableMethod: {
                MouseUp: function(e, vc) {
                    _p.reload(_p.sIcon.position, _p.eIcon.position)
                }
            }
        })
    };
    this._add_jline = function() {
        _p.jLines = _p.pManager.add(null, {
            color: "#0000ff",
            size: 3,
            opacity: "0.80"
        })
    };
    this.isSdApi = function() {
        if (this.equal_ignore_case(_sd_api, "sd_api")) {
            return true
        }
        return false
    };
    this.delete_mNumbers = function() {
        for (var i = 0; i < _mNumbers.length; i++) {
            this.mManager.remove(_mNumbers[i])
        }
        _mNumbers = []
    };
    this.put_mNumbers = function(pos, lon, lat) {
        var icon = new SD.genmap.MarkerSprite({
            css: "dot",
            iconSize: new Size(pos.width, pos.height),
            bgPosLeft: pos.left,
            bgPosTop: pos.top,
            iconAnchor: new Point(pos.width / 2, pos.width / 2)
        });
        var marker = this.mManager.add({
            icon: icon,
            position: new GeoPoint(lon, lat),
            map: _map,
            labelOffset: new Point(-12, -12)
        });
        EventManager.add(marker, "mouseover", function(e) {
            var dom = marker.getObject();
            dom.removeAttribute("class");
            dom.setAttribute("class", "number")
        });
        EventManager.add(marker, "mouseout", function(e) {
            var dom = marker.getObject();
            dom.removeAttribute("class");
            dom.setAttribute("class", "dot")
        });
        _mNumbers.push(marker)
    };
    this.reload = function(st, ed) {
        var url = SD.API_URL + "api/?act=" + _sd_api + "&mode=journey_v2&output=js&startlon=" + st.lon + "&startlat=" + st.lat + "&endlon=" + ed.lon + "&endlat=" + ed.lat + "&methods=" + _methods + "&vehicle=" + _vehicle + "&info=1&callback=SDJourney.instance.go&shortest_walking=" + _shortest_walking + "&get_start_end=" + _get_start_end + "&alternative_bus=1&r=" + Math.floor(Math.random() * 1000);
        if (_driving_type) {
            url += "&driving_type=" + _driving_type
        }
        if (_no_cache) {
            url += "&no_cache=" + _no_cache
        }
        var label = this.getLabel(st.lon + "--" + st.lat + "--" + ed.lon + "--" + ed.lat, _methods, _vehicle, _date, _time);
        _temp_res = this.getDirRes();
        if (_temp_res.label == label) {
            this.go(_temp_res.result.data)
        } else {
            this.ro(url, st, ed)
        }
    };
    this.load = function(options) {
        var query = options.q;
        if (typeof urlencode == "function") {
            query = urlencode(query)
        }
        _q = query;
        var country = options.country;
        var methods = options.methods;
        var vehicle = options.vehicle;
        var sd_api = options.sd_api;
        var no_startend = options.no_startend;
        var date = options.date;
        _date = date;
        var time = options.time;
        _time = time;
        _no_line = options.no_line;
        _optional_obj = options.optional_obj;
        _callback = options.callback;
        _success = options.success;
        _shortest_walking = options.shortest_walking;
        _driving_type = options.driving_type;
        _no_cache = options.no_cache;
        var is_via = query.search("via") > -1;
        if (options.get_start_end) {
            _get_start_end = options.get_start_end
        } else {
            _get_start_end = 0
        }
        if (_shortest_walking) {
            _shortest_walking = "1"
        } else {
            _shortest_walking = "none"
        }
        if (methods == undefined) {
            methods = "driving"
        }
        if (sd_api == undefined || sd_api != true) {
            _sd_api = "none"
        } else {
            _sd_api = "sd_api"
        }
        if (no_startend == undefined || no_startend != true) {
            no_startend = "none"
        } else {
            no_startend = 1
        }
        _methods = methods;
        _vehicle = vehicle;
        var nofilter = "";
        if (location.search.search("nofilter=1") != -1 || global.no_bus_schedule != undefined) {
            nofilter = "&nofilter=1"
        }
        var url = SD.API_URL + "api/?act=" + _sd_api + "&mode=journey_v2&output=js&methods=" + _methods + "&vehicle=" + _vehicle + "&info=1&country=" + country + "&q=" + query + "&no_startend=" + no_startend + "&callback=SDJourney.instance.go&shortest_walking=" + _shortest_walking + "&get_start_end=" + _get_start_end + "&alternative_bus=1&r=" + Math.floor(Math.random() * 1000) + nofilter;
        if (date && time) {
            url += "&date=" + date + "&time=" + time
        }
        if (_driving_type) {
            url += "&driving_type=" + _driving_type
        }
        if (_no_cache) {
            url += "&no_cache=" + _no_cache
        }
        if (options.pid_aid1 && !is_via) {
            _pid_aid1 = options.pid_aid1;
            url += "&pid_aid1=" + _pid_aid1
        }
        if (options.pid_aid2 && !is_via) {
            _pid_aid2 = options.pid_aid2;
            url += "&pid_aid2=" + _pid_aid2
        }
        if (options.weight != undefined) {
            url += "&weight=" + options.weight
        }
        var label = this.getLabel(_q, _methods, _vehicle, _date, _time);
        _temp_res = this.getDirRes();
        if (_temp_res && _temp_res.label == label && options.shortest_walking == undefined) {
            this.go(_temp_res.result.data)
        } else {
            this.ro(url)
        }
    };
    this.getDirRes = function() {
        var res_obj = {
            label: null
        };
        if (this.equal_ignore_case(_methods, "driving") && !_driving_type) {
            res_obj = _direction_result.driving
        } else {
            if (this.equal_ignore_case(_methods, "taxi") && !_driving_type) {
                res_obj = _direction_result.taxi
            } else {
                if (this.equal_ignore_case(_methods, "bustrain") && this.equal_ignore_case(_vehicle, "bus")) {
                    res_obj = _direction_result.bus
                } else {
                    if (this.equal_ignore_case(_methods, "bustrain") && (this.equal_ignore_case(_vehicle, "both") || this.equal_ignore_case(_vehicle, "train"))) {
                        res_obj = _direction_result.bustrain
                    } else {
                        if (this.equal_ignore_case(_methods, "all")) {
                            res_obj = _direction_result.all
                        }
                    }
                }
            }
        }
        return res_obj
    };
    this.go = function(data) {
        var label = this.getLabel(_q, _methods, _vehicle, _date, _time);
        _temp_res = this.getDirRes();
        _temp_res.label = label;
        _temp_res.result = {
            data: data
        };
        if (_callback == undefined) {
            _p.ce(data)
        } else {
            _callback(data, _p, _ob, _optional_obj)
        }
        if (!_no_line) {
            this.drawLine(data);
            this.mManager.setAutoAdjust(true)
        }
        if (_success) {
            _success(data)
        }
    };
    this.getLabel = function(q, method, mode, date, time) {
        var label = "";
        label = q + "--" + method.toLowerCase() + "--" + mode.toLowerCase() + "--" + date + "--" + time;
        if (method == "all" || method == "driving" || method == "taxi") {}
        label += "--" + $j("input[name=cr_opt]:checked").val();
        return label
    };
    this.ro = function(url) {
        var meta = SD.util.addScript(url);
        meta.current = meta;
        meta.onload = function() {
            if (this.current.parentNode) {
                SD.util.removeScript(this.current)
            }
        }
    };
    this.drawLine = function(data, d_idx) {
        var routes = data.rs;
        if ((_p.isSdApi() && this.equal_ignore_case(_methods, "taxi") == false && this.equal_ignore_case(_methods, "all") == false) || this.equal_ignore_case(_methods, "bustrain")) {
            if (d_idx == undefined) {
                d_idx = 0
            }
            routes = data.rs[d_idx]
        }
        if (_p.sIcon) {
            _p.sIcon.setPosition({
                lon: routes[0].x,
                lat: routes[0].y
            });
            _p.eIcon.setPosition({
                lon: routes[routes.length - 1].x,
                lat: routes[routes.length - 1].y
            })
        } else {
            _p._add_s_icon(routes[0].x, routes[0].y);
            _p._add_e_icon(routes[routes.length - 1].x, routes[routes.length - 1].y)
        }
        if (_p.jLines) {} else {
            _p._add_jline()
        }
        _p.jLines.setPoints(routes);
        _p.jLines.draw(_p.map.canvasInfo)
    };
    this.iconpos = function(index, width, height) {
        var lft = (index % 10) - 1;
        if (lft < 0) {
            lft = 9
        }
        var left = width * lft;
        var tp = index % 10 > 0 ? Math.floor(index / 10) : (index / 10) - 1;
        var top = height * tp;
        return {
            top: top,
            left: left,
            width: width,
            height: height
        }
    };
    this.addcss = function() {
        var style = document.createElement("style");
        style.setAttribute("type", "text/css");
        var rule1 = document.createTextNode(".number_red {background: url('http://x1.sdimgs.com/img/journey/red99.png') repeat scroll 0 0 transparent;}");
        var rule2 = document.createTextNode(".number {background: url('http://x1.sdimgs.com/img/journey/white99.png') repeat scroll 0 0 transparent;}");
        var rule3 = document.createTextNode(".dot {background: url('http://x1.sdimgs.com/img/journey/dot.png') repeat scroll 0 0 transparent !important;}");
        var rule4 = document.createTextNode(".parking {background: url('http://x1.sdimgs.com/img/journey/parking-point.png') repeat scroll 0 0 transparent;}");
        var style = document.getElementsByTagName("style")[0];
        if (style != undefined) {
            if (style.styleSheet) {
                style.styleSheet.cssText += rule1.nodeValue + rule2.nodeValue + rule3.nodeValue + rule4.nodeValue
            } else {
                style.appendChild(rule1);
                style.appendChild(rule2);
                style.appendChild(rule3);
                style.appendChild(rule4)
            }
        } else {
            var head = document.getElementsByTagName("head")[0];
            style = document.createElement("style");
            style.type = "text/css";
            if (style.styleSheet) {
                style.styleSheet.cssText += rule1.nodeValue + rule2.nodeValue + rule3.nodeValue + rule4.nodeValue
            } else {
                style.appendChild(rule1);
                style.appendChild(rule2);
                style.appendChild(rule3);
                style.appendChild(rule4)
            }
            head.appendChild(style)
        }
        _css_used = true
    };
    this.bindEvent = function(el, eventName, eventHandler) {
        if (el.addEventListener) {
            el.addEventListener(eventName, eventHandler, false)
        } else {
            if (el.attachEvent) {
                el.attachEvent("on" + eventName, eventHandler)
            }
        }
    };
    this._get_str_time = function(hour) {
        var time = Math.ceil(hour) + " h";
        if (hour < 1) {
            var minute = hour * 60;
            time = Math.ceil(minute) + " min";
            if (minute < 1) {
                var second = minute * 60;
                time = Math.ceil(second) + " sec"
            }
        }
        return time
    };
    this.sum_taxi = function(data) {
        var infos = data.is;
        var roads = document.createElement("div");
        roads.setAttribute("id", "roads");
        var tbl = document.createElement("table");
        tbl.setAttribute("cellspacing", 0);
        tbl.setAttribute("cellpadding", 0);
        tbl.setAttribute("border", 0);
        var tbody1 = document.createElement("tbody");
        var tr1 = document.createElement("tr");
        var td1 = document.createElement("td");
        td1.setAttribute("class", "label");
        this.setStyle(td1, "width:170px; font-size:12px");
        td1.innerHTML = "Total Time : " + this._get_str_time(infos.ti.tc);
        tr1.appendChild(td1);
        td1 = document.createElement("td");
        td1.setAttribute("class", "label");
        td1.setAttribute("valign", "top");
        this.setStyle(td1, "width:170px; font-size:12px");
        var tbl2 = document.createElement("table");
        tbl2.setAttribute("id", "roadpath");
        var tbody2 = document.createElement("tbody");
        var tr2, td2;
        var len = infos.tf.length;
        tr2 = document.createElement("tr");
        td2 = document.createElement("td");
        td2.setAttribute("class", "label");
        td2.innerHTML = "Approx. Fare";
        tr2.appendChild(td2);
        td2 = document.createElement("td");
        td2.setAttribute("class", "label");
        td2.innerHTML = infos.tf[0].u + infos.tf[0].v;
        tr2.appendChild(td2);
        tbody2.appendChild(tr2);
        tbl2.appendChild(tbody2);
        td1.appendChild(tbl2);
        tr1.appendChild(td1);
        tbody1.appendChild(tr1);
        tbl.appendChild(tbody1);
        roads.appendChild(tbl);
        _ob.appendChild(roads)
    };
    this.equal_ignore_case = function(string1, string2) {
        return (string1.toUpperCase() === string2.toUpperCase())
    };
    this.rzCC = function(s) {
        for (var exp = /-([a-z])/; exp.test(s); s = s.replace(exp, RegExp.$1.toUpperCase())) {}
        return s
    };
    this.setStyle = function(element, declaration) {
        if (declaration.charAt(declaration.length - 1) == ";") {
            declaration = declaration.slice(0, -1)
        }
        var k, v;
        var splitted = declaration.split(";");
        for (var i = 0, len = splitted.length; i < len; i++) {
            k = this.rzCC(splitted[i].split(":")[0]);
            v = splitted[i].split(":")[1];
            eval("element.style." + k + "='" + v + "'")
        }
    };
    this.ce = function(data, ce_idx) {
        if (_ob == null || _ob == undefined) {
            return
        }
        while (_ob.hasChildNodes()) {
            _ob.removeChild(_ob.lastChild)
        }
        var head = document.getElementsByTagName("head")[0];
        var link = document.createElement("link");
        link.setAttribute("rel", "stylesheet");
        link.setAttribute("type", "text/css");
        link.setAttribute("href", SD.API_URL + "assets/styles/journey_style.css");
        head.appendChild(link);
        if (_css_used == false) {
            this.addcss()
        }
        if (this.equal_ignore_case(_methods, "taxi")) {
            this.sum_taxi(data)
        }
        var newdiv = document.createElement("div");
        _ob.appendChild(newdiv);
        var infodiv = document.createElement("div");
        infodiv.setAttribute("id", "infos");
        var table = document.createElement("table");
        var tbody = document.createElement("tbody");
        var tr, td_num, td_info, td_length, pos;
        var posimg;
        var num;
        var imgwidth = 25;
        var imgheight = 25;
        var idx;
        var start_end_div;
        var s_e_img;
        var span;
        tr = document.createElement("tr");
        tr.setAttribute("class", "information");
        td_num = document.createElement("td");
        this.setStyle(td_num, "width:10px");
        start_end_div = document.createElement("div");
        start_end_div.setAttribute("class", "s");
        s_e_img = document.createElement("img");
        s_e_img.setAttribute("src", "http://x1.sdimgs.com/img/journey/s.png");
        start_end_div.appendChild(s_e_img);
        td_num.appendChild(start_end_div);
        tr.appendChild(td_num);
        td_info = document.createElement("td");
        td_info.setAttribute("colspan", "2");
        this.setStyle(td_info, "width:290px");
        if (data.se[0].tt != "") {
            span = document.createElement("b");
            span.innerHTML = data.se[0].tt;
            td_info.appendChild(span);
            span = document.createElement("br");
            td_info.appendChild(span)
        }
        span = document.createElement("span");
        span.innerHTML = data.se[0].dc;
        td_info.appendChild(span);
        tr.appendChild(td_info);
        tbody.appendChild(tr);
        var journey = data.is;
        if (this.isSdApi() && this.equal_ignore_case(_methods, "taxi") == false) {
            if (ce_idx == undefined) {
                ce_idx = 0
            }
            journey = data.is.j[ce_idx]
        } else {
            if (this.equal_ignore_case(_methods, "taxi")) {
                journey = data.is.j
            } else {
                if (this.equal_ignore_case(_methods, "bustrain")) {
                    journey = data.is[0]
                }
            }
        }
        this.delete_mNumbers();
        for (var i = 0; i < journey.length; i++) {
            idx = i + 1;
            tr = document.createElement("tr");
            tr.setAttribute("class", "information");
            pos = this.iconpos(idx, imgwidth, imgheight);
            if (journey[i].x) {
                this.put_mNumbers(pos, journey[i].x, journey[i].y)
            }
            td_num = document.createElement("td");
            td_num.setAttribute("class", "td_num");
            this.setStyle(td_num, "width:10px");
            posimg = document.createElement("div");
            posimg.setAttribute("class", "number_" + idx);
            this.setStyle(posimg, "width:25px; height:25px; overflow:hidden; position:relative; left:8px;");
            num = document.createElement("div");
            num.setAttribute("class", "number");
            this.setStyle(num, "width:250px; height: 250px; position:absolute;top:-" + pos.top + "px;left:-" + pos.left + "px");
            posimg.appendChild(num);
            td_num.appendChild(posimg);
            tr.appendChild(td_num);
            td_info = document.createElement("td");
            td_info.setAttribute("class", "td_info");
            this.setStyle(td_info, "width:240px");
            if (this.equal_ignore_case(_methods, "bustrain")) {
                var tdiv = document.createElement("div");
                tdiv.setAttribute("class", "label");
                tdiv.innerHTML = journey[i].tt;
                td_info.appendChild(tdiv);
                td_info.appendChild(document.createElement("br"));
                var tspan = document.createElement("span");
                tspan.innerHTML = journey[i].dc;
                td_info.appendChild(tspan)
            } else {
                td_info.innerHTML = journey[i].dc
            }
            tr.appendChild(td_info);
            if (journey[i].unit != undefined) {
                td_length = document.createElement("td");
                td_length.setAttribute("class", "td_length");
                this.setStyle(td_length, "width:50px;");
                td_length.innerHTML = journey[i].unit;
                tr.appendChild(td_length)
            }
            tbody.appendChild(tr)
        }
        tr = document.createElement("tr");
        tr.setAttribute("class", "information");
        td_num = document.createElement("td");
        this.setStyle(td_num, "width:10px");
        start_end_div = document.createElement("div");
        start_end_div.setAttribute("class", "e");
        s_e_img = document.createElement("img");
        s_e_img.setAttribute("src", "http://x1.sdimgs.com/img/journey/e.png");
        start_end_div.appendChild(s_e_img);
        td_num.appendChild(start_end_div);
        tr.appendChild(td_num);
        td_info = document.createElement("td");
        td_info.setAttribute("colspan", "2");
        this.setStyle(td_info, "width:290px");
        if (data.se[1].tt != "") {
            span = document.createElement("b");
            span.innerHTML = data.se[1].tt;
            td_info.appendChild(span);
            span = document.createElement("br");
            td_info.appendChild(span)
        }
        span = document.createElement("span");
        span.innerHTML = data.se[1].dc;
        td_info.appendChild(span);
        tr.appendChild(td_info);
        tbody.appendChild(tr);
        table.appendChild(tbody);
        infodiv.appendChild(table);
        _ob.appendChild(infodiv)
    }
};
SDJourney.instance = null;

function SDJourney(a) {
    if (SDJourney.instance == null) {
        SDJourney.instance = new SD.serv.Basejourney(a)
    }
    return SDJourney.instance
};
SD.ns("SD.bld");
SD.bld.PanTool = function(a) {
    this.isActive = true;
    this.statusCompleted = false;
    var c = false;
    var g = this.isActive;
    var b = 100;
    setInterval(function() {
        if (g) {
            if (b == 5 && a) {
                a.reqOnViewport()
            }
            h();
            b++
        }
    }, 100);
    this.setActive = function(j) {
        this.isActive = j;
        g = j
    };
    this.setCount = function(j) {
        b = j
    };
    var d = false;
    var e = false;
    var f = false;
    var h = function() {
        if (d) {
            if (e) {
                e = false;
                return
            }
            d = false;
            if (a && a.req && f) {
                c = f.getCursorMoveRowCol();
                a.req(c)
            }
        }
    };
    this.MouseMove = function(l, k) {
        var j = k.viewportInfo.canvasSize;
        var n = k.viewportInfo.lastCursorPosMove;
        var m = l.target || l.srcElement;
        if (0 <= n.x && n.x <= j.width && 0 <= n.y && n.y <= j.height && ((m.nodeName.toLowerCase() == "img" && m.width == 256 && m.height == 256) || (m.nodeName.toLowerCase() == "img" && m.width == 258 && m.height == 258) || (m.nodeName.toLowerCase() == "img" && m.width == 250 && m.height == 250) || m.nodeName.toLowerCase() == "svg" || m.nodeName.toLowerCase() == "path" || m.nodeName.toLowerCase() == "polyline" || m.nodeName.toLowerCase() == "canvas")) {
            if (!k.onDrag && this.isActive) {
                f = k.viewportInfo;
                d = true;
                e = false
            } else {
                if (k.onDrag) {
                    this.statusCompleted = false
                }
            }
        }
        if (a.layer[0].div.style.display == "none") {
            a.hideTooltip();
            if (typeof a.display_landmark_marker == "function" && m.id != "blddir_marker" && m.id != "here_marker") {
                a.display_landmark_marker("hide")
            }
        }
    };
    this.SetTimer = function(j) {}
};
SD.extend(SD.bld.PanTool, DrawingTool);
SD.bld.QueueManager = function() {
    this.nodes = {};
    this.nodesIndex = new Array();
    this.max = 50;
    this.sp = "_";
    this.add = function(b) {
        if (b.r && b.c && b.l && b.nodes) {
            var a = this.getIndex(b);
            if (!this.nodes.hasOwnProperty(a)) {
                this.nodes[a] = b;
                this.nodesIndex.splice(0, 0, a);
                return b
            }
        }
        return false
    };
    this.addNode = function(b, a, c) {
        return this.add({
            r: b,
            c: a,
            l: c,
            nodes: true
        })
    };
    this.gc = function() {
        if (this.nodesIndex.length > this.max) {
            var c = this.nodesIndex.length - this.max;
            var a;
            for (var b = 0; b < c; b++) {
                a = this.nodesIndex.pop();
                if (this.nodes[a]) {
                    delete this.nodes[a]
                }
            }
        }
    };
    this.reIndex = function(l, d) {
        var g = [];
        for (var b = l.top; b <= l.bottom; b++) {
            for (var h = l.left; h <= l.right; h++) {
                if (this.get(b, h, d)) {
                    g.push(this.getIndex({
                        r: b,
                        c: h,
                        l: d
                    }))
                }
            }
        }
        if (g.length == 0) {
            return
        }
        var m, j = [];
        for (var f = 0; f < this.nodesIndex.length; f++) {
            m = false;
            for (var e = 0; e < g.length; e++) {
                if (this.nodesIndex[f] == g[e]) {
                    m = true;
                    break
                }
            }
            if (!m) {
                j.push(this.nodesIndex[f])
            }
        }
        if (j.length > 0) {
            for (var k = 0; k < j.length; k++) {
                g.push(j[k])
            }
        }
        this.nodesIndex = g
    };
    this.clear = function() {
        for (var a in this.nodes) {
            if (this.nodes.hasOwnProperty(a)) {
                delete this.nodes[a]
            }
        }
        this.nodes = {};
        this.nodesIndex = []
    };
    this.get = function(c, b, d) {
        var a = this.getIndex({
            r: c,
            c: b,
            l: d
        });
        if (this.nodes.hasOwnProperty(a)) {
            return this.nodes[a]
        }
        return false
    };
    this.getIndex = function(a) {
        return a.r + this.sp + a.c + this.sp + a.l
    }
};
SD.bld.ReqManager = function() {
    SD.apply(this, new SD.bld.QueueManager());
    this.addNode = function(e, a, f, b) {
        var d = {
            r: e,
            c: a,
            l: f,
            nodes: true,
            _requested: false,
            _loaded: false,
            _req: null,
            request: function(g) {
                if (this._requested || this._loaded) {
                    return
                }
                this._req = SD.util.addScript(g);
                this._req.current = this._req;
                this._req.onload = function() {
                    if (this.current.parentNode) {
                        SD.util.removeScript(this.current)
                    }
                    this.current._loaded = true
                };
                this._requested = true
            },
            abort: function() {
                if (this._req != null && !this._loaded && this._req.parentNode) {
                    SD.util.removeScript(this._req);
                    this._req = null
                }
            }
        };
        if (this.add(d)) {
            var c = this.getIndex(d);
            if (this.nodes.hasOwnProperty(c)) {
                this.nodes[c].request(b)
            }
            this.gc()
        }
    };
    this.abortPrevious = function() {
        if (this.nodesIndex.length == 0) {
            return
        }
        for (var a in this.nodes) {
            if (this.nodes.hasOwnProperty(a)) {
                this.nodes[a].abort()
            }
        }
    }
};
SD.bld.Service = function(c) {
    SD.apply(this, c);
    this.lastEndDrag = false;
    this.firstMouseOver = false;
    this.isDisplay = true;
    this.pm = new SD.genmap.PolylineManager({
        map: c.map
    });
    this.placeData = null;
    this.layer = [];
    this.layer_limit = 20;
    this.getStateConfig();
    var b = {
        color: "red",
        size: 1,
        opacity: 0.8,
        bgColor: "red",
        fillOpacity: 0.6,
        hideOnLevel: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    };
    for (var d = 0; d < this.layer_limit; d++) {
        this.layer[d] = this.pm.add([{
            x: 0,
            y: 0
        }], b);
        this.layer[d].useGeo = false;
        this.layer[d].setDisplay(false)
    }
    this.resetLayer(false);
    this.latestNode = {};
    this.latestParam = {
        r: 0,
        c: 0,
        l: 0
    };
    this.reqManager = new SD.bld.ReqManager();
    this.queueManager = new SD.bld.QueueManager();
    this.pt = new SD.bld.PanTool(this);
    this.map.viewport.OnEndWheel.register(this.OnEndWheel, this);
    this.map.viewport.OnLevelChanged.register(this.OnLevelChanged, this);
    this.map.viewport.mapLayer.OnCompleted.register(this.OnCompleted, this);
    this.map.viewport.OnDraw.register(this.OnDraw, this);
    this.map.viewport.OnEndDrag.register(this.OnEndDrag, this);
    this.tooltip = document.createElement("div");
    this.tooltip.id = "buildingVectorTooltip";
    this.tooltip.style.cssText = "position:absolute; z-index:0; display:none;";
    var a = document.createElement("img");
    a.src = "http://x1.sdimgs.com/img/map/arrow-b.gif";
    a.style.cssText = "position:absolute; z-index:-1; top:-5px; left:50px;";
    this.tooltip.appendChild(a);
    var e = document.createElement("div");
    e.style.cssText = "background-color:#252525; color:#FFFFFF; font-family:verdana; font-size:9px; height:12px; line-height: 12px; padding:5px; white-space:nowrap; z-index:0; -webkit-border-radius:5px; -moz-border-radius:5px; border-radius:5px;";
    this.tooltip.appendChild(e);
    this.map.viewportInfo.div.appendChild(this.tooltip)
};
SD.bld.Service.prototype.OnCompleted = function() {
    this.pt.statusCompleted = true
};
SD.bld.Service.prototype.OnDraw = function() {
    if (this.pt.isActive && !SD.isTouchDevice()) {
        this.OnEndDrag(true)
    }
};
SD.bld.Service.prototype.init = function() {
    this.map.viewport.defaultTool.SetCallback(this.pt);
    this.OnLevelChanged();
    var c = this;
    var e, d, b, a;
    EventManager.add(this.map.viewport.fakeDiv, "click", function(f) {
        if (Math.abs(b - e) <= 2 && Math.abs(a - d) <= 2) {
            c.triggerEvent()
        }
    });
    EventManager.add(this.map.viewport.fakeDiv, "mousedown", function(f) {
        e = f.clientX;
        d = f.clientY
    });
    EventManager.add(this.map.viewport.fakeDiv, "mouseup", function(f) {
        b = f.clientX;
        a = f.clientY
    });
    EventManager.add(this.map.viewport.fakeDiv, "mouseover", function(f) {
        if (c.reqManager.nodesIndex.length == 0) {
            c.firstMouseOver = true;
            c.OnDraw()
        }
    });
    EventManager.add(this.layer[0].div, "mouseout", function(f) {
        if (c.isSameBuilding) {
            c.mouseOut()
        }
    });
    EventManager.add(this.layer[0].div, "mouseover", function(f) {
        if (SD.util.checkMouseEnter(this, f)) {
            if (c.isSameBuilding) {
                c.mouseOver()
            }
        }
    })
};
SD.bld.Service.prototype.resetLayer = function(c, b) {
    var d = this.layer.length;
    if (d > 0) {
        for (var a = 0; a < d; a++) {
            if (typeof b !== "undefined" && b && a != 0) {
                continue
            }
            if (this.layer[a]) {
                this.layer[a].setDisplay(c)
            }
        }
    }
};
SD.bld.Service.prototype.isActiveLevel = function() {
    return this.map.zoom > 10
};
SD.bld.Service.prototype.OnEndDrag = function(c) {
    if (typeof c == "boolean" && c) {
        this.lastEndDrag = false
    }
    var a = new Date().getTime();
    var b = this.lastEndDrag || a - 1;
    var d = a - b;
    if (this.pt.isActive) {
        this.lastEndDrag = a;
        if (d != 1) {
            this.pt.setCount(0)
        }
        if (d == 1) {
            this.pt.setCount(100);
            this.reqOnViewport(this.map.canvasInfo.mapRowCols)
        }
    }
};
SD.bld.Service.prototype.OnEndWheel = function() {
    this.resetLayer(false)
};
SD.bld.Service.prototype.getStateConfig = function() {
    var b = this.map.zoom;
    var a = this.map.viewportInfo.centerGeo;
    this.cfgRegion = global.bldStateConfig.get(a.lon, a.lat, b);
    this.cfgState = false;
    for (i in this.activeConfig) {
        if (this.activeConfig[i].sid == this.cfgRegion.sid && this.activeConfig[i].cid == this.cfgRegion.cid) {
            this.cfgState = this.activeConfig[i].src;
            return
        }
    }
};
SD.bld.Service.prototype.OnLevelChanged = function() {
    this.hideTooltip();
    this.resetLayer(false);
    this.getStateConfig();
    var b = this.map.viewportInfo.lastCursorPosDown;
    var a = this.isActiveLevel();
    this.pt.setActive(false);
    if (this.cfgState && a && this.isDisplay) {
        this.pt.setActive(true)
    }
};
SD.bld.Service.prototype.triggerEvent = function() {
    if (this.latestNode.vc == undefined) {
        return
    }
    var d = this.map.viewportInfo.lastCursorPosDown;
    var c = this.map.viewportInfo.viewportScreenToMetric(d.x, d.y);
    var b = this.isIn(this.latestNode.vc, c.x, c.y);
    if (this.callback && (this.layer[0].isDisplayed() || this.layer[0].div.style.display == "block") && b) {
        this.callback(this.latestNode, this.layer[0]);
        if (typeof google_analytic == "function") {
            var a = "/stats/" + this.cfgRegion.cp + "/building_vector/click/" + this.latestNode.pid + "/" + this.latestNode.aid;
            google_analytic(a)
        }
    }
};
SD.bld.Service.prototype.mouseOut = function(a) {
    if (this.animate_zoomout) {
        this.animate_zoomout(this.layer[0])
    }
};
SD.bld.Service.prototype.mouseOver = function(b) {
    if (this.latestNode.vc == undefined) {
        return
    }
    var a = (this.layer[0].boundMetric.right - this.layer[0].boundMetric.left) * (this.layer[0].boundMetric.top - this.layer[0].boundMetric.bottom);
    a = a / 1000;
    if (this.layer[0].isDisplayed() && this.animate_zoomin && a <= 1000) {
        if (this.latestNode.ib == 1) {
            newOpt = {
                color: "red",
                size: 1,
                opacity: 0.6,
                bgColor: "red",
                fillOpacity: 0.4,
                hideOnLevel: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            };
            this.animate_zoomin(this.layer[0], "", 1, 5, false, newOpt, false)
        } else {
            this.animate_zoomin(this.layer[0], "", 1.2, 5, false, "", true);
            if (typeof this.display_landmark_marker == "function") {
                this.display_landmark_marker("show")
            }
        }
    }
};
SD.bld.Service.prototype.showTooltip = function(a) {
    var d = this.map.viewportInfo.lastCursorPosMove;
    if (d.x != 0 && d.y != 0) {
        var c = this.map.viewportInfo.viewportScreenToMetric(d.x, d.y);
        var b = this.isIn(this.latestNode.vc, c.x, c.y);
        if (b) {
            if (a.title != "") {
                this.tooltip.childNodes[1].innerHTML = a.title
            } else {
                this.tooltip.childNodes[1].innerHTML = this.latestNode.tbiz + " businesses inside"
            }
            this.tooltip.style.top = (d.y + 20) + "px";
            this.tooltip.style.left = (d.x - 40) + "px";
            this.tooltip.style.display = "block"
        }
    }
};
SD.bld.Service.prototype.hideTooltip = function() {
    if (this.tooltip != undefined) {
        this.tooltip.style.display = "none"
    }
};
SD.bld.Service.prototype.isIn = function(c, b, h) {
    var a = 1,
        g = c.length;
    var d = g - 1;
    for (var f = 0; f < g; f++) {
        if ((parseFloat(c[f].y) <= h && h < parseFloat(c[d].y)) || (parseFloat(c[d].y) <= h && h < parseFloat(c[f].y))) {
            var e = (parseFloat(c[d].x) - parseFloat(c[f].x)) * (h - parseFloat(c[f].y)) / (parseFloat(c[d].y) - parseFloat(c[f].y)) + parseFloat(c[f].x);
            if (b < e) {
                a = 1 - a
            }
        }
        d = f
    }
    return a != 1
};
SD.bld.Service.prototype.setDisplay = function(b) {
    this.isDisplay = b;
    this.resetLayer(false);
    this.pt.setActive(b);
    for (var a = 0; a < this.layer_limit; a++) {
        if (this.layer[a]) {
            this.layer[a].setDisplay(b)
        }
    }
};
SD.bld.Service.prototype.reqOnViewport = function(d) {
    if (this.firstMouseOver == false) {
        return
    }
    if (d == undefined) {
        d = this.map.canvasInfo.mapRowCols
    }
    var a = this.map.viewportInfo.mapConfig;
    a.realLevel = a.realLevel == 14 ? 13 : a.realLevel;
    for (var b = d.top; b <= d.bottom; b++) {
        for (var f = d.left; f <= d.right; f++) {
            var e = this.reqManager.addNode(b, f, a.realLevel, this.getSingleUri(b, f, a.realLevel, this.cfgState))
        }
    }
    this.reqManager.reIndex(d, a.realLevel)
};
SD.bld.Service.prototype.syncQueue = function() {
    if (this.reqManager.nodesIndex.length == this.queueManager.nodesIndex.length) {
        var a = this.map.viewportInfo.mapConfig;
        this.queueManager.reIndex(this.map.canvasInfo.mapRowCols, a.realLevel)
    }
};
SD.bld.Service.prototype.req = function(c) {
    var a = this.map.viewportInfo.mapConfig;
    this.latestParam.r = c.row;
    this.latestParam.c = c.col;
    this.latestParam.l = a.realLevel == 14 ? 13 : a.realLevel;
    var b = this.queueManager.get(c.row, c.col, this.latestParam.l);
    if (b) {
        this.populate(b)
    }
    if (SD.bld.ServiceIns == null) {
        SD.bld.ServiceIns = this
    }
};
SD.bld.Service.prototype.getSingleUri = function(b, e, a, d) {
    if (window.location.hash == "#boundary" && d == "sg") {
        return SD.API_URL + "api/?mode=building_vector&v=" + SD.MAP_VERSION + "&row=" + b + "&col=" + e + "&l=" + a + "&src=" + d + "&boundary=1&type=" + global.bld_type + "&callback=SD.bld.ServiceIns.goSingle&output=js" + (this.debug ? "&no_cache=1" : "") + (this.api ? "&api=" + this.api : "")
    } else {
        return SD.API_URL + "api/?mode=building_vector&v=" + SD.MAP_VERSION + "&row=" + b + "&col=" + e + "&l=" + a + "&src=" + d + "&type=" + global.bld_type + "&callback=SD.bld.ServiceIns.goSingle&output=js" + (this.debug ? "&no_cache=1" : "") + (this.api ? "&api=" + this.api : "")
    }
};
SD.bld.Service.prototype.getPAUri = function(d) {
    if (typeof d == "object") {
        var b = "src=" + this.cfgState + "&v=" + SD.MAP_VERSION + "&";
        for (var e in d) {
            b += e + "=" + d[e] + "&"
        }
        if (b.length > 0) {
            b = b.substr(0, b.length - 1)
        }
        var c = d.domain ? d.domain : SD.API_URL;
        var a = c + "api/?" + b;
        return a
    }
    return d
};
SD.bld.Service.prototype.reqUri = function(a) {
    var b = SD.util.addScript(a);
    b.current = b;
    b.onload = function() {
        if (this.current.parentNode) {
            SD.util.removeScript(this.current)
        }
    }
};
SD.bld.Service.prototype.populate = function(m) {
    if (!m) {
        return
    }
    this.resetLayer(false);
    var e;
    if (this.layer[0].div) {
        if (this.layer[0].div.parentNode) {
            if (this.layer[0].div.parentNode.parentNode) {
                e = this.layer[0].div.parentNode.parentNode
            }
        }
    }
    var n = this.map.viewportInfo.lastCursorPosMove,
        l = false;
    var g = this.map.viewportInfo.viewportScreenToMetric(n.x, n.y);
    for (var f = 0; f < m.nodes.length; f++) {
        if (typeof m.nodes[f].vc == "string") {
            m.nodes[f].vc = Utf8.gdecode(m.nodes[f].vc, false, "xy")
        }
        if (this.isIn(m.nodes[f].vc, g.x, g.y)) {
            l = true;
            if (e) {
                e.style.cursor = "pointer"
            }
            if (this.latestNode == m.nodes[f]) {
                this.resetLayer(true, true);
                this.isSameBuilding = true;
                if (typeof this.display_landmark_marker == "function") {
                    this.display_landmark_marker("show")
                }
                break
            }
            this.isSameBuilding = false;
            this.mouseOut();
            this.latestNode = m.nodes[f];
            this.layer[0].div.parentNode.style.zIndex = "";
            this.layer[0].setPoints(m.nodes[f].vc);
            this.layer[0].draw(this.map.canvasInfo);
            this.mouseOver();
            var h = [];
            for (var d = 0; d < m.nodes.length; d++) {
                if (!m.nodes[f].paid) {
                    continue
                }
                if (m.nodes[f].pid == m.nodes[d].pid && m.nodes[f].aid == m.nodes[d].aid && d != f) {
                    h.push(m.nodes[d])
                }
            }
            if (h.length > 1 && h.length < this.layer_limit) {
                var a = h.length;
                for (var c = 0; c < a; c++) {
                    var b = c + 1;
                    if (this.layer[b]) {
                        this.layer[b].setPoints(h[c].vc);
                        this.layer[b].draw(this.map.canvasInfo)
                    }
                }
            }
            break
        }
    }
    if (!l && e) {
        e.style.cursor = ""
    }
};
SD.bld.Service.prototype.goSingle = function(b) {
    if (b == null || !b.d || b.d.length == undefined) {
        return
    }
    if (b.d) {
        var d = {
            r: b.r,
            c: b.c,
            l: b.l,
            nodes: []
        };
        b.d = this.comparePlace(b.d);
        for (var a = 0; a < b.d.length; a++) {
            if (b.d[a].paid && !b.d[a].pid) {
                b.d[a].pid = b.d[a].paid[0].p;
                b.d[a].aid = b.d[a].paid[0].a
            }
            d.nodes.push(b.d[a])
        }
        var c = this.queueManager.add(d);
        if (c) {
            this.populate(c)
        }
        this.queueManager.gc()
    }
};
SD.bld.Service.prototype.comparePlace = function(f) {
    if (this.placeData != null && (f != null || f.length != undefined)) {
        var a = this.placeData.d;
        for (var e = 0, h = f.length; e < h; e++) {
            for (var b = 0, g = a.length; b < g; b++) {
                if (a[b].oid == f[e].oid) {
                    f[e].pid = this.placeData.p;
                    f[e].aid = this.placeData.a
                }
            }
        }
    }
    return f
};
SD.bld.Service.prototype.goPlaceAddress = function(b) {
    if (b == null || !b.d || b.d.length == undefined) {
        return
    }
    if (b.d.length > 0 && b.d.length < this.layer_limit) {
        this.placeData = b;
        for (var a = 0; a < b.d.length; a++) {
            if (typeof b.d[a].vc == "string") {
                b.d[a].vc = Utf8.gdecode(b.d[a].vc, false, "xy")
            }
            this.pm.add(b.d[a].vc, {
                color: "red",
                size: 1,
                opacity: 0.8,
                bgColor: "red",
                fillOpacity: 0.6,
                projection: this.map.viewportInfo.projection,
                hideOnLevel: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            })
        }
    }
};
SD.bld.Service.prototype.goMulti = function(b) {
    if (b == null || b.length == undefined) {
        return
    }
    for (var a = 0; a < b.length; a++) {
        this.queueManager.add(b[a])
    }
    this.queueManager.gc()
};
if (typeof SD.bld.ServiceIns == "undefined") {
    SD.bld.ServiceIns = null
}

function BuildingService(a) {
    if (SD.bld.ServiceIns == null) {
        SD.bld.ServiceIns = new SD.bld.Service(a);
        SD.bld.ServiceIns.init()
    }
    return SD.bld.ServiceIns
};
var sdGa = {
    sdGaUrl: "",
    hostname: location.hostname
};
sdGa.isLocal = function() {
    if (this.hostname == "localhost" || this.hostname == "sdcom" || this.hostname.search("172.16.0.") >= 0 || this.hostname.search("streetdirectory") >= 0 || this.hostname.search("street-directory") >= 0 || this.hostname.search("businessfinder") >= 0 || this.hostname.search("sdbackoffice") >= 0 || this.sdGaUrl.search("&noga=1") >= 0) {
        return true
    }
    return false
};
sdGa.addUtmn = function() {
    var a = Math.floor(Math.random() * 2147483647);
    this.sdGaUrl += "&utmn=" + a
};
sdGa.addUtmr = function() {
    var a = (document.referrer != "") ? encodeURIComponent(document.referrer) : "-";
    this.sdGaUrl += "&utmr=" + a
};
sdGa.addGoogleAnalytic = function() {
    if (!sdGa.isLocal()) {
        this.addUtmn();
        this.addUtmr();
        this.sdGaUrl = this.sdGaUrl.replace("replace_this", this.hostname);
        var a = document.createElement("img");
        a.src = this.sdGaUrl;
        a.style.cssText = "display:none";
        var b = document.getElementsByTagName("html")[0];
        b.appendChild(a)
    }
};
if (SD.GA_URL != undefined) {
    sdGa.sdGaUrl = SD.GA_URL;
    sdGa.addGoogleAnalytic()
};