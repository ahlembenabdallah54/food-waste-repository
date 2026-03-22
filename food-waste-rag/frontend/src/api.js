import axios from 'axios'

const api = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' }
})

export async function askQuestion(question, lang = 'en') {
  const { data } = await api.post('/ask', { question, lang })
  return data
}