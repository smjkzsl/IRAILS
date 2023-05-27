    const api = {
        user: {
            async getCurrentUser() {
                try {
                    const response = await fetch('/system_admin/user/current_user')
                    const data = await response.json()
                    return data.username
                } catch (error) {
                    console.error(error)
                    return null
                }
            }
        }
    }
    module.exports = api