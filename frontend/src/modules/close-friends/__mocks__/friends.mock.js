
export const avatarFor = (seed) =>
  `https://robohash.org/${encodeURIComponent(seed)}.png?set=set4&size=128x128`

const clamp01 = (n) => Math.max(0, Math.min(100, Number.isFinite(+n) ? +n : 0))

const mockFriends = [
  {
    id: 'f_1',
    name: 'Alicia Tan',
    handle: '@alicia',
    avatar: avatarFor('alicia'),
    phone: '+65 8123 4567',
    email: 'alicia@example.com',
    relationship: 'Classmate',
    tags: ['Buddy', 'Study'],
    emergencyContact: true,
    notifyOn: { redFlags: true, lowMoodStreak: true, sleepDrop: false },
    status: 'active',
    emotions: { mood: 82, energy: 67, sleep: 74 }, // 0–100
  },
  {
    id: 'f_2',
    name: 'Marcus Lee',
    handle: '@marcus',
    avatar: avatarFor('marcus'),
    phone: '+65 8989 1212',
    email: 'marcus@example.com',
    relationship: 'Cousin',
    tags: ['Family'],
    emergencyContact: false,
    notifyOn: { redFlags: true, lowMoodStreak: false, sleepDrop: true },
    status: 'active',
    emotions: { mood: 0, energy: 15, sleep: 39 },
  },
  {
    id: 'f_3',
    name: 'Pending Invite – Jo',
    handle: '@jo',
    avatar: avatarFor('jo'),
    phone: '',
    email: 'jo@example.com',
    relationship: '',
    tags: [],
    emergencyContact: false,
    notifyOn: { redFlags: false, lowMoodStreak: false, sleepDrop: false },
    status: 'pending',
    emotions: { mood: 50, energy: 50, sleep: 50 },
  },
]

let _friends = [...mockFriends]
const delay = (ms = 200) => new Promise((r) => setTimeout(r, ms))

export async function listFriends(q = '') {
  await delay()
  const query = q.toLowerCase()
  return _friends.filter(
    (f) =>
      f.name.toLowerCase().includes(query) ||
      (f.handle || '').toLowerCase().includes(query) ||
      (f.relationship || '').toLowerCase().includes(query) ||
      (f.tags || []).join(',').toLowerCase().includes(query)
  )
}

export async function createFriend(payload) {
  await delay()
  const id = 'f_' + Math.random().toString(36).slice(2, 8)
  // Stable seed (handle > name > id), strip @ if present
  const seed = (payload.handle || payload.name || id).replace(/^@/, '')
  const defaults = {
    status: 'pending',
    emergencyContact: false,
    notifyOn: { redFlags: true, lowMoodStreak: true, sleepDrop: false },
    tags: [],
    emotions: {
      mood: clamp01(payload?.emotions?.mood ?? 60),
      energy: clamp01(payload?.emotions?.energy ?? 60),
      sleep: clamp01(payload?.emotions?.sleep ?? 60),
    },
  }
  const friend = {
    id,
    avatar: payload.avatar || avatarFor(seed), // allow override
    ...defaults,
    ...payload,
    // ensure emotions are clamped if provided
    emotions: {
      ...defaults.emotions,
      ...(payload.emotions
        ? {
            mood: clamp01(payload.emotions.mood),
            energy: clamp01(payload.emotions.energy),
            sleep: clamp01(payload.emotions.sleep),
          }
        : {}),
    },
  }
  _friends.unshift(friend)
  return friend
}

function deepMergeFriend(orig, patch) {
  return {
    ...orig,
    ...patch,
    notifyOn: { ...orig.notifyOn, ...(patch.notifyOn || {}) },
    emotions: {
      ...orig.emotions,
      ...(patch.emotions
        ? {
            mood: clamp01(patch.emotions.mood ?? orig.emotions?.mood),
            energy: clamp01(patch.emotions.energy ?? orig.emotions?.energy),
            sleep: clamp01(patch.emotions.sleep ?? orig.emotions?.sleep),
          }
        : {}),
    },
  }
}

export async function updateFriend(id, patch) {
  await delay()
  _friends = _friends.map((f) => (f.id === id ? deepMergeFriend(f, patch) : f))
  return _friends.find((f) => f.id === id)
}

export async function deleteFriend(id) {
  await delay()
  _friends = _friends.filter((f) => f.id !== id)
  return { ok: true }
}

export async function approveInvite(id) {
  await delay()
  return updateFriend(id, { status: 'active' })
}

export async function resendInvite(id) {
  await delay(300)
  return { ok: true }
}

export async function revokeInvite(id) {
  await delay(300)
  _friends = _friends.filter((f) => f.id !== id)
  return { ok: true }
}

export async function setEmotion(id, key, value) {
  if (!['mood', 'energy', 'sleep'].includes(key)) return { ok: false }
  return updateFriend(id, { emotions: { [key]: clamp01(value) } })
}

export async function bumpEmotion(id, key, delta) {
  const f = _friends.find((x) => x.id === id)
  if (!f || !['mood', 'energy', 'sleep'].includes(key)) return { ok: false }
  const next = clamp01((f.emotions?.[key] ?? 0) + (delta ?? 0))
  return updateFriend(id, { emotions: { [key]: next } })
}
