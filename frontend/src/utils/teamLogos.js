import mapPositions from '../components/Map/mapd.json'

export const DEFAULT_TEAM_LOGO = '/static/images/teams/default_logo.png'

const normalizeTeamName = (name = '') =>
  name
    .toLowerCase()
    .replace(/football club/g, '')
    .replace(/\butd\b/g, 'united')
    .replace(/\bafc\b/g, '')
    .replace(/\bfc\b/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

export const resolveTeamInfo = (teamName) => {
  if (!teamName) return null
  if (mapPositions[teamName]) return mapPositions[teamName]

  const normalized = normalizeTeamName(teamName)
  if (!normalized) return null

  for (const [key, info] of Object.entries(mapPositions)) {
    const normalizedKey = normalizeTeamName(key)
    if (!normalizedKey) continue
    if (
      normalized === normalizedKey ||
      normalized.includes(normalizedKey) ||
      normalizedKey.includes(normalized)
    ) {
      return info
    }
  }

  return null
}

export const findTeamLogo = (teamName) =>
  resolveTeamInfo(teamName)?.logo || DEFAULT_TEAM_LOGO
