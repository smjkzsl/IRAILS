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
        modelManager: {
            path: '/system_admin/model_manager',
            async getModelMeta(model_name) {
                model_name = model_name || ""
                return await request(`${this.path}/model_meta?model_name=${model_name}`)
            },
            async fetchModelData(module_name, model_name, currentPage, pageSize) {
                currentPage = currentPage || 1
                pageSize = pageSize || ""
                const data = await request(`${this.path}/model_data?module=${module_name}&model=${model_name}&page_size=${pageSize}&page_num=${currentPage}`)
                if (data.status == 200) {
                    return data.data
                } else {
                    return []
                }
            }
        },
        system: {
            path: '/system_admin/admin',
            async request(url, options) {
                let data = await request(`${this.path}/${url}`, options)
                return data
            },
            async getAppList(t) {
                t = t || ""
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
            async get_configs(cfg_domain) {

                let body = { 'domain': cfg_domain || "" }
                return await this.request('get_configs', { method: "GET", body: (body) })
            },
            async save_configs(domain, data) {
                const body = { 'domain': domain, 'data': data }
                return await this.request("save_configs", { method: "POST", body: JSON.stringify(body) })
            },

        }
    }
    module.exports = api