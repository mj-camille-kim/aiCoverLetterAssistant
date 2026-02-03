const DEFAULT_BASE_URL = import.meta.env.VITE_APP_API_URL ?? 'http://localhost:8000'
const DEFAULT_POLL_INTERVAL_MS = 60 * 1000  // 1분마다 결과 조회
const DEFAULT_MAX_POLL_TIME_MS = 5 * 60 * 1000  // 최대 5분 대기

/**
 * 채용공고 링크로 분석 요청 후 보고서 HTML을 받아옵니다.
 * @param {Object} params
 * @param {string} params.targetUrl - 채용공고 URL
 * @param {string} params.selectedJob - 직무 (예: 백엔드 개발자)
 * @param {string} params.experienceLevel - 경력 (예: 신입, 1-3년)
 * @param {Object} [options]
 * @param {string} [options.baseUrl] - API Base URL
 * @param {number} [options.pollIntervalMs] - 결과 조회 폴링 간격(ms)
 * @param {number} [options.maxPollTimeMs] - 최대 대기 시간(ms)
 * @returns {Promise<string>} 보고서 HTML
 * @throws {Error} 요청 실패, job_id 없음, 타임아웃, 결과 조회 실패 시
 */
export async function fetchAnalysisReport(
  { targetUrl, selectedJob, experienceLevel },
  options = {}
) {
  const baseUrl = options.baseUrl ?? DEFAULT_BASE_URL
  const pollIntervalMs = options.pollIntervalMs ?? DEFAULT_POLL_INTERVAL_MS
  const maxPollTimeMs = options.maxPollTimeMs ?? DEFAULT_MAX_POLL_TIME_MS

  let res
  try {
    res = await fetch(`${baseUrl}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_url: targetUrl,
        selected_job: selectedJob,
        experience_level: experienceLevel
      })
    })
  } catch (networkErr) {
    if (networkErr?.message === 'Failed to fetch' || networkErr?.name === 'TypeError') {
      throw new Error(
        '분석 서버(포트 8000)에 연결할 수 없습니다. aiServer를 실행한 뒤 다시 시도해 주세요. (예: aiServer 폴더에서 python -m uvicorn main:app --reload --port 8000)'
      )
    }
    throw networkErr
  }

  const data = await res.json().catch(() => ({}))
  if (!res.ok && res.status !== 202) {
    throw new Error(data.detail || data.message || `요청 실패 (${res.status})`)
  }

  const jobId = data.job_id
  if (!jobId) {
    throw new Error('분석 작업 ID를 받지 못했습니다.')
  }

  const pollStart = Date.now()
  while (true) {
    if (Date.now() - pollStart > maxPollTimeMs) {
      throw new Error('분석 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.')
    }

    const result = await fetch(`${baseUrl}/analyze/result/${jobId}`)
    if (result.status === 200) {
      return await result.text()
    }
    if (result.status === 202) {
      await new Promise((r) => setTimeout(r, pollIntervalMs))
      continue
    }

    const errData = await result.json().catch(() => ({}))
    throw new Error(
      errData.detail || errData.message || '분석 결과 조회에 실패했습니다.'
    )
  }
}
