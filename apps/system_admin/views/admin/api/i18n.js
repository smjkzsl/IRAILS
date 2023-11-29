const { createI18n,useI18n } = require("vue-i18n_global")
const { nextTick } = require("vue")
 

const i18n = {
    t (...args) { 
        let t = useI18n()
         
        return t(...args)
    },
    _i18n:null,
    SUPPORT_LOCALES: ['en', 'ja'],
    locales_path:'../locales',
    setupI18n(options ={} ) {
        
        let opt = {
            locale: 'zh', // set locale
            fallbackLocale: 'en', // set fallback locale
            messages: {
                 
            }
            ,...options
        }
        const _i18n = createI18n(opt)
        app.use(_i18n)
        // app.mixin({
        //     beforeCreate() {
        //         this.t = (...args) => this.$i18n.t(...args);
               
        //     }})
         
        i18n._i18n = _i18n 
        i18n.setI18nLanguage(_i18n, opt.locale)
        
    },
    async setI18nLanguage(_i18n, locale) {
        // load locale messages
        
        if (!_i18n.global.availableLocales.includes(locale)) {
            await i18n.loadLocaleMessages(_i18n, locale)
        }else{
            if (_i18n.mode === 'legacy') {
                _i18n.global.locale = locale
            } else {
                _i18n.global.locale.value = locale
            }
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
        const url =`${i18n.locales_path}/${locale}.json` ;
        const res = await fetch(url);
        if (!res.ok)
            throw Object.assign(new Error(url + ' ' + res.statusText), { res });
        const messages = await res.json(); 
            
        // set locale and locale message
        _i18n.global.setLocaleMessage(locale, messages )

        
    }

}
module.exports = i18n