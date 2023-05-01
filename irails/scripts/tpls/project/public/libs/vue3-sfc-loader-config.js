const vue3_loader_options = {

    moduleCache: {
        vue: Vue,
    },

    async getFile(url) {

        // if (url === '/myComponent.vue')
        //     return Promise.resolve(componentSource);

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
}