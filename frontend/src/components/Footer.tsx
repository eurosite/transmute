import { useEffect, useState } from 'react'
import { FaGithub, FaExternalLinkAlt, FaBook } from 'react-icons/fa'
import { publicFetch as fetch } from '../utils/api'

const RELEASE_VERSION_PATTERN = /^v\d+\.\d+\.\d+$/
const COMMIT_SHA_PATTERN = /^[0-9a-f]{7}$/i

function getVersionHref(version: string): string | null {
  if (version === 'dev') return null
  if (RELEASE_VERSION_PATTERN.test(version)) {
    return `https://github.com/transmute-app/transmute/releases/tag/${version}`
  }
  if (COMMIT_SHA_PATTERN.test(version)) {
    return `https://github.com/transmute-app/transmute/commit/${version}`
  }
  return null
}

function Footer() {
  const [appInfo, setAppInfo] = useState<{ name: string; version: string } | null>(null)
  const versionHref = appInfo?.version ? getVersionHref(appInfo.version) : null

  useEffect(() => {
    fetch('/api/health/info')
      .then(res => res.json())
      .then(data => setAppInfo(data))
      .catch(() => { }) // Silently fail if API is unavailable
  }, [])

  return (
    <footer className="mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-center gap-2 text-text-muted text-sm">
          <a href="https://github.com/transmute-app/transmute" target="_blank" rel="noopener noreferrer" className="hover:text-text transition-colors" aria-label="GitHub" title="Source Code">
            <FaGithub size={16} />
          </a>
          <span className="text-text-muted/30">|</span>
          <span>
            {appInfo?.name || 'Transmute'}
            {appInfo?.version && (
              versionHref ? (
                <a
                  href={versionHref}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-2 text-text-muted/60 hover:text-text transition-colors"
                  title={appInfo.version === 'dev' ? 'Development build' : `Version ${appInfo.version}`}
                >
                  {appInfo.version}
                </a>
              ) : (
                <span className="ml-2 text-text-muted/60">{appInfo.version}</span>
              )
            )}
          </span>
          <span className="text-text-muted/30">|</span>
          <a href="/api/docs" className="hover:text-text transition-colors" aria-label="API Docs" title="API Documentation">
            <FaBook size={14} />
          </a>
          <span className="text-text-muted/30">|</span>
          <a href="https://transmute.sh" target="_blank" rel="noopener noreferrer" className="hover:text-text transition-colors" aria-label="Website" title="Transmute Website">
            <FaExternalLinkAlt size={13} />
          </a>
        </div>
      </div>
    </footer>
  )
}

export default Footer
