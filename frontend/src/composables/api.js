import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('vantage_token')
  if (token) cfg.headers.Authorization = `Token ${token}`
  return cfg
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('vantage_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
