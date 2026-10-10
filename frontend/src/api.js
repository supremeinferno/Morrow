// Calls go to VITE_API_URL when set (e.g. https://morrow.onrender.com/api), otherwise to
// same-origin /api, which the Vite dev proxy or the vercel.json rewrite forwards.
const API_BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/+$/, '')

const SERVER_ERROR = "Couldn't reach the Morrow server. Make sure the API is running."

function errorMessage(status, data) {
  if (typeof data?.detail === 'string') return data.detail
  if (status >= 500) return SERVER_ERROR
  return `Request failed (${status}).`
}

async function request(path, options) {
  let response

  try {
    response = await fetch(`${API_BASE}${path}`, options)
  } catch {
    throw new Error(SERVER_ERROR)
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(errorMessage(response.status, data))
  }

  return data
}

export function createMeetingFromLink(url) {
  const form = new FormData()
  form.append('url', url)
  return request('/meetings', { method: 'POST', body: form })
}

/** Upload a recording, reporting progress (0–1) as it goes. */
export function uploadMeeting(file, onProgress) {
  // fetch() can't report upload progress, so this uses XMLHttpRequest.
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    const form = new FormData()
    form.append('file', file)

    xhr.open('POST', `${API_BASE}/meetings`)
    xhr.responseType = 'json'

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress?.(event.loaded / event.total)
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) resolve(xhr.response)
      else reject(new Error(errorMessage(xhr.status, xhr.response)))
    }

    xhr.onerror = () => reject(new Error(SERVER_ERROR))
    xhr.send(form)
  })
}

export function getMeeting(meetingId) {
  return request(`/meetings/${meetingId}`)
}

export function askQuestion(meetingId, question) {
  return request(`/meetings/${meetingId}/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
}
