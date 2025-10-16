// En Docker, el backend está detrás de nginx, no directamente accesible
// El nginx hace proxy de /api/* al backend:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || ''

// Gestión de tokens JWT en localStorage
export const tokenManager = {
    getAccessToken: () => localStorage.getItem('access_token'),
    getRefreshToken: () => localStorage.getItem('refresh_token'),
    setTokens: (accessToken, refreshToken) => {
        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
    },
    clearTokens: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    }
}

// Función para refrescar el access token
const refreshAccessToken = async () => {
    const refreshToken = tokenManager.getRefreshToken()
    if (!refreshToken) {
        throw new Error('No refresh token available')
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken })
        })

        if (!response.ok) {
            throw new Error('Failed to refresh token')
        }

        const data = await response.json()
        tokenManager.setTokens(data.access, refreshToken)
        return data.access
    } catch (error) {
        tokenManager.clearTokens()
        throw error
    }
}

export const apiRequest = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}/api${endpoint}`
    const accessToken = tokenManager.getAccessToken()

    const defaultOptions = {
        headers: {},
    }

    // Solo agregar Content-Type si NO es FormData
    if (!options.isFormData) {
        defaultOptions.headers['Content-Type'] = 'application/json'
    }

    // Agregar token JWT si existe
    if (accessToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${accessToken}`
    }

    const config = { ...defaultOptions, ...options }

    // Solo stringify si NO es FormData
    if (config.body && typeof config.body === 'object' && !options.isFormData) {
        config.body = JSON.stringify(config.body)
    }

    // Remover la bandera isFormData antes de hacer fetch
    delete config.isFormData

    let response = await fetch(url, config)

    // Si el token expiró (401), intentar refrescar y reintentar
    if (response.status === 401 && accessToken) {
        try {
            const newAccessToken = await refreshAccessToken()
            config.headers['Authorization'] = `Bearer ${newAccessToken}`
            response = await fetch(url, config)
        } catch (refreshError) {
            // Si falla el refresh, redirigir al login
            tokenManager.clearTokens()
            throw { response: { status: 401, data: { error: 'Sesión expirada' } } }
        }
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw { response: { status: response.status, data: error } }
    }

    return response.json()
}