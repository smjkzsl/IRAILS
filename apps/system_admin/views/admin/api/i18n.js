const { createI18n, useI18n } = require("vue-i18n_global")
const { nextTick } = require("vue")
const { user, request } = require("/system_admin/admin/api/api.js")

const i18n = {
    t(...args) {
        let t = useI18n()

        return t(...args)
    },

     
    default_locales_json_path: '../locales',
    
    async fetch_i18n_list(_i18n,default_locale) {
        const i18n_list = await user.get_i18n_list()
        console.log('i18n_list', i18n_list)
        // 遍历 i18n_list，为每个语言环境设置翻译字典
        for (const locale in i18n_list) {
            if (i18n_list.hasOwnProperty(locale)) {
                const messages = i18n_list[locale]
                // 使用 setLocaleMessage 方法更新翻译字典
                _i18n.global.setLocaleMessage(locale, messages)
            }
        } 
        await i18n.setI18nLanguage(_i18n, default_locale)
    },
    async setupI18n(options = {}) {

        if (app._i18n) return app._i18n
        console.log("setuping i18n...")

        let opt = {
            locale: 'zh', // set locale
            fallbackLocale: 'en', // set fallback locale
            messages: {
                zh: {}, en: {}
            }
            , ...options
        }

        const _i18n = createI18n(opt)
        app.use(_i18n)
        // app.mixin({
        //     beforeCreate() {
        //         console.log(this,'before_create')
        //         this.t = (...args) => this.$i18n.t(...args);

        //     }})

        app._i18n = _i18n


        i18n.fetch_i18n_list(_i18n,opt.locale)
        return app._i18n
    },
    async setI18nLanguage(_i18n, locale) {
        // load locale messages
        await i18n.loadLocaleMessages(_i18n, locale)
        if (_i18n.mode === 'legacy') {
            _i18n.global.locale = locale
        } else {
            _i18n.global.locale.value = locale
        }


        /**
         * NOTE:
         * If you need to specify the language setting for headers, such as the `fetch` API, set it here.
         * The following is an example for axios.
         *
         * axios.defaults.headers.common['Accept-Language'] = locale
         */
        document.querySelector('html').setAttribute('lang', locale)
        return nextTick()
    },
    async loadLocaleMessages(_i18n, locale) {
        // load locale messages with dynamic import
        const url = `${i18n.default_locales_json_path}/${locale}.json`;
        const res = await fetch(url);
        if (!res.ok)
            throw Object.assign(new Error(url + ' ' + res.statusText), { res });
        const messages = await res.json();

        const old_messages = _i18n.global.getLocaleMessage(locale)
        const new_message = {
            ...old_messages,
            ...messages
        }
        // set locale and locale message
        _i18n.global.setLocaleMessage(locale, new_message)


    }

}
module.exports = i18n