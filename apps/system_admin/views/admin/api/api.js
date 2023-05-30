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
            async getAppList() {
                let data = await request(`${this.path}/app_list`)
                return data
            },
            async getPagesList() {
                let data = await request(`${this.path}/pages_list`)
                return data
            }
        }
    }
    module.exports = api