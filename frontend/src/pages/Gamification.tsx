import { useEffect, useState } from 'react'
import { useAuth } from '../store/auth'
import { gamificationApi, staffApi, type GamificationStats, type Achievement, type LeaderboardEntry, type Challenge } from '../api/client'
import { Trophy, Flame, Star, Medal, Target, Zap } from 'lucide-react'

export function GamificationPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<GamificationStats | null>(null)
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const [myAchievements, setMyAchievements] = useState<{ name: string; description: string; icon: string; earned_at: string }[]>([])
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    Promise.all([
      gamificationApi.stats(user.staff_id),
      gamificationApi.achievements(),
      gamificationApi.myAchievements(user.staff_id),
      gamificationApi.leaderboard(),
      gamificationApi.challenges(),
    ]).then(([s, a, ma, lb, ch]) => {
      setStats(s)
      setAchievements(a)
      setMyAchievements(ma)
      setLeaderboard(lb)
      setChallenges(ch)
    }).finally(() => setLoading(false))
  }, [user])

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-600 border-t-transparent" />
      </div>
    )
  }

  const earnedNames = new Set(myAchievements.map((a) => a.name))

  return (
    <div className="space-y-6">
      <div className="page-header">
        <h1 className="page-title">Gamification</h1>
        <p className="page-description">Earn XP, unlock achievements, and climb the leaderboard</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 dark:bg-brand-500/10">
            <Star className="h-5 w-5 text-brand-600" />
          </div>
          <div className="stat-value">{stats?.level || 1}</div>
          <div className="stat-label">Level</div>
        </div>
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 dark:bg-amber-500/10">
            <Zap className="h-5 w-5 text-amber-600" />
          </div>
          <div className="stat-value">{stats?.xp || 0}</div>
          <div className="stat-label">Total XP</div>
        </div>
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-50 dark:bg-orange-500/10">
            <Flame className="h-5 w-5 text-orange-600" />
          </div>
          <div className="stat-value">{stats?.current_streak || 0}</div>
          <div className="stat-label">Day Streak</div>
        </div>
        <div className="stat-card">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-500/10">
            <Trophy className="h-5 w-5 text-emerald-600" />
          </div>
          <div className="stat-value">{stats?.total_achievements || 0}</div>
          <div className="stat-label">Achievements</div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Leaderboard */}
        <div className="card lg:col-span-1">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2"><Medal className="h-5 w-5 text-amber-500" /> Leaderboard</h3>
          </div>
          <div className="space-y-3">
            {leaderboard.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">No data yet</p>
            ) : (
              leaderboard.slice(0, 10).map((entry, i) => (
                <div key={entry.staff_id} className={`flex items-center gap-3 rounded-lg p-2.5 ${entry.staff_id === user?.staff_id ? 'bg-brand-50 dark:bg-brand-500/10' : ''}`}>
                  <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                    i === 0 ? 'bg-amber-100 text-amber-700' : i === 1 ? 'bg-gray-100 text-gray-600' : i === 2 ? 'bg-orange-100 text-orange-700' : 'bg-gray-50 text-gray-400'
                  }`}>
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium">{entry.name}</div>
                    <div className="text-xs text-gray-400">Lv. {entry.level}</div>
                  </div>
                  <div className="text-sm font-semibold">{entry.xp} XP</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Challenges */}
        <div className="card lg:col-span-2">
          <div className="card-header">
            <h3 className="card-title flex items-center gap-2"><Target className="h-5 w-5 text-brand-500" /> Challenges</h3>
          </div>
          <div className="space-y-3">
            {challenges.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">No active challenges</p>
            ) : (
              challenges.slice(0, 6).map((ch) => (
                <div key={ch.id} className="rounded-lg border p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium">{ch.title}</h4>
                      <p className="text-sm text-gray-500 mt-0.5">{ch.description}</p>
                    </div>
                    <span className="badge-purple">+{ch.xp_reward} XP</span>
                  </div>
                  <div className="mt-3">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>{ch.goal_type}: {ch.goal_value}</span>
                      <span>Ends: {new Date(ch.ends_at).toLocaleDateString()}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-100 dark:bg-gray-800">
                      <div className="h-2 rounded-full bg-brand-500 transition-all" style={{ width: '0%' }} />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Achievements */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title flex items-center gap-2"><Trophy className="h-5 w-5 text-amber-500" /> Achievements</h3>
          <span className="text-sm text-gray-500">{myAchievements.length}/{achievements.length} unlocked</span>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {achievements.map((a) => {
            const earned = earnedNames.has(a.name)
            return (
              <div
                key={a.id}
                className={`rounded-xl border p-4 transition-all ${
                  earned
                    ? 'border-amber-200 bg-amber-50/50 dark:border-amber-500/20 dark:bg-amber-500/5'
                    : 'opacity-50 grayscale'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="text-2xl">{a.icon || '🏆'}</div>
                  <div>
                    <h4 className="text-sm font-semibold">{a.name}</h4>
                    <p className="text-xs text-gray-500">{a.description}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
