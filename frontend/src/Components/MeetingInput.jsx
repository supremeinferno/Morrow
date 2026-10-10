import { useState } from 'react'

import { createMeetingFromLink, uploadMeeting } from '../api.js'
import { ArrowIcon, FileIcon, LinkIcon, UploadIcon } from './Icons.jsx'

const MODES = [
  { id: 'link', label: 'Paste a link', icon: LinkIcon },
  { id: 'upload', label: 'Upload a file', icon: UploadIcon },
]

const ACCEPTED_FILES = 'audio/*,video/*,.mkv,.m4a,.opus'

function formatSize(bytes) {
  const megabytes = bytes / 1024 / 1024
  return megabytes >= 1 ? `${megabytes.toFixed(1)} MB` : `${Math.ceil(bytes / 1024)} KB`
}

/** Lets the user submit a meeting as a video link or an uploaded recording. */
export default function MeetingInput({ onCreated }) {
  const [mode, setMode] = useState('link')
  const [url, setUrl] = useState('')
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(null)
  const [error, setError] = useState(null)

  const canSubmit = !isSubmitting && (mode === 'link' ? url.trim() : file)

  const chooseFile = (chosen) => {
    if (!chosen) return
    setFile(chosen)
    setError(null)
  }

  const onDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    chooseFile(event.dataTransfer.files[0])
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    if (!canSubmit) return

    setIsSubmitting(true)
    setError(null)

    try {
      const meeting = mode === 'link'
        ? await createMeetingFromLink(url.trim())
        : await uploadMeeting(file, setUploadProgress)

      onCreated(meeting)
      setUrl('')
      setFile(null)
    } catch (submitError) {
      setError(submitError.message)
    } finally {
      setIsSubmitting(false)
      setUploadProgress(null)
    }
  }

  const buttonLabel = uploadProgress !== null
    ? `Uploading ${Math.round(uploadProgress * 100)}%`
    : isSubmitting ? 'Starting...' : 'Analyze'

  return (
    <form className="meeting-input" onSubmit={onSubmit}>
      <div className="mode-tabs" role="tablist" aria-label="Meeting source">
        {MODES.map(({ id, label, icon: ModeIcon }) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={mode === id}
            className={`mode-tab ${mode === id ? 'is-active' : ''}`}
            onClick={() => {
              setMode(id)
              setError(null)
            }}
          >
            <ModeIcon size={16} />
            {label}
          </button>
        ))}
      </div>

      {mode === 'link' ? (
        <div className="input-row">
          <input
            className="text-input"
            type="url"
            inputMode="url"
            placeholder="https://www.youtube.com/watch?v=..."
            aria-label="Meeting video link"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            required
          />
          <button className="button button-primary" type="submit" disabled={!canSubmit}>
            {buttonLabel}
            {!isSubmitting && <ArrowIcon size={18} />}
          </button>
        </div>
      ) : (
        <div className="input-row input-row-upload">
          <label
            className={`dropzone ${isDragging ? 'is-dragging' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={(event) => {
              event.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
          >
            <input
              className="visually-hidden"
              type="file"
              accept={ACCEPTED_FILES}
              onChange={(event) => chooseFile(event.target.files[0])}
            />
            {file ? <FileIcon size={20} /> : <UploadIcon size={20} />}
            <span className="dropzone-text">
              {file ? (
                <>
                  <strong>{file.name}</strong>
                  <span>{formatSize(file.size)} · click to change</span>
                </>
              ) : (
                <>
                  <strong>Drop a recording here</strong>
                  <span>or click to browse · MP4, MOV, MP3, WAV, M4A</span>
                </>
              )}
            </span>
            {uploadProgress !== null && (
              <span className="upload-bar" style={{ '--progress': uploadProgress }} />
            )}
          </label>
          <button className="button button-primary" type="submit" disabled={!canSubmit}>
            {buttonLabel}
            {!isSubmitting && <ArrowIcon size={18} />}
          </button>
        </div>
      )}

      {error ? (
        <p className="input-error" role="alert">{error}</p>
      ) : (
        <p className="input-hint">
          {mode === 'link'
            ? 'YouTube and most video sites work. Long meetings take a few minutes.'
            : 'Your recording is transcribed locally with Whisper.'}
        </p>
      )}
    </form>
  )
}
