    async function request(url) {
        try {
            const response = await fetch(url)
            const data = await response.json()

            return data
        } catch (error) {
            console.error(error)
            return null
        }

    }
    const api = {
        user: {
            async getCurrentUser() {
                return await request('/system_admin/user/current_user')
            }
        },
        system: {
            async getAppList() {
                let data = await request('/system_admin/admin/app_list')
                return data
            },
            async getPagesList() {
                let data = await request('/system_admin/admin/pages_list')
                return data
            }
        }
    }
    module.exports = api