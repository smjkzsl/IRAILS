    async function request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            body: null,
            headers: {
                'Content-Type': 'application/json'
            }
        }

        const opts = {...defaultOptions, ...options }
        if (opts['method'] == 'GET' && opts['body']) {
            const queryString = Object.entries(opts['body']).map(([key, value]) =>
                `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join('&');
            opts.body = null
            if (url.indexOf('?') > 0) {
                url = url + queryString
            } else {
                url = `${url}?${queryString}`
            }

        }
        try {
            const response = await fetch(url, opts)
            const data = await response.json()

            return data
        } catch (error) {
            console.error(error)
            return null
        }

    }
    const api = {
        user: {
            path: '/system_admin/user',
            async getCurrentUser() {

                return await request(`${this.path}/current_user`)
            }
        },
        system: {
            path: '/system_admin/admin',
            async request(url, options) {
                let data = await request(`${this.path}/${url}`, options)
                return data
            },
            async getAppList(t) {

                let data = await this.request('app_list', { body: { 't': t } })
                return data
            },
            async getPagesList() {

                let data = await this.request(`pages_list`)
                return data
            },
            async uninstall_app(app_name) {
                let body = { 'app_name': app_name }
                let ret = await this.request('uninstall', { method: "POST", body: JSON.stringify(body) })
                return ret
            },
            async install_app(app_name) {
                let body = { 'app_name': app_name }
                let ret = await this.request('install', { method: "POST", body: JSON.stringify(body) })
                return ret
            },
        }
    }
    module.exports = api