const vue3_loader_options = {

    moduleCache: {

    },

    async getFile(url) {
        const allowed_exts = ['js', 'vue', 'css', 'json']
        const ext = url.split(".").slice(-1)[0]
        if (ext) {
            if (!allowed_exts.includes(ext)) {
                url += ".js"
            }
        }

        const res = await fetch(url);
        if (!res.ok)
            throw Object.assign(new Error(url + ' ' + res.statusText), { res });
        return await res.text();
    },

    addStyle(textContent) {

        const style = Object.assign(document.createElement('style'), { textContent });
        const ref = document.head.getElementsByTagName('style')[0] || null;
        document.head.insertBefore(style, ref);
    },

    log(type, ...args) {

        console[type](...args);
    },
    compiledCache: {
        set(key, str) {

            // naive storage space management
            for (; ;) {

                try {

                    // doc: https://developer.mozilla.org/en-US/docs/Web/API/Storage
                    window.localStorage.setItem(key, str);
                    break;
                } catch (ex) {

                    // handle: Uncaught DOMException: Failed to execute 'setItem' on 'Storage': Setting the value of 'XXX' exceeded the quota

                    window.localStorage.removeItem(window.localStorage.key(0));
                }
            }
        },
        get(key) {

            return window.localStorage.getItem(key);
        }
    },
    async handleModule(type, getContentData, path, options) {
        switch (type) {
            case '.css':
                options.addStyle(await getContentData(false));
                return null;
            case '.json':
                const text = getContentData(false) ;
                return JSON.parse(text);
                

        }
    }
}