    async function request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            body: null,
            headers: {
                'Content-Type': 'application/json'
            }
        }
        const opts = {...defaultOptions, ...options }

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
            async getAppList() {
                let data = await this.request('app_list')
                return data
            },
            async getPagesList() {
                let data = await request(`${this.path}/pages_list`)
                return data
            },
            async uninstall_app(app_name) {

                let body = { 'app_name': app_name }
                let ret = await this.request('uninstall', { method: "POST", body: JSON.stringify(body) })
                return ret
            }
        }
    }
    module.exports = api