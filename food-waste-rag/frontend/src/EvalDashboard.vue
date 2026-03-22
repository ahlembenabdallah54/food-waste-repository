<template>
  <div class="eval-page">

    <div class="bg-leaves">
      <span v-for="i in 6" :key="i" class="leaf" :class="`leaf-${i}`">🍃</span>
    </div>

    <!-- Header -->
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <img src="/robot.png" alt="FoodWise" class="logo-img" />
          <span class="logo-text">FoodWise <em>AI</em></span>
        </div>
        <div class="header-right">
          <button class="back-btn" @click="$emit('back')">← Back to Chat</button>
        </div>
      </div>
    </header>

    <main class="container">

      <!-- Title -->
      <div class="page-title">
        <h1>📊 RAG Evaluation Dashboard</h1>
        <p>Measure and monitor the performance of your knowledge retrieval system</p>
      </div>

      <!-- Run evaluation button -->
      <div class="run-section">
        <button class="run-btn" :disabled="running" @click="runEvaluation">
          <span v-if="!running">▶ Run Evaluation Suite</span>
          <span v-else class="spinner-wrap"><span class="spinner"></span> Running tests...</span>
        </button>
        <p class="run-note">Runs {{ testQuestions.length }} predefined test questions and measures system performance</p>
      </div>

      <!-- Summary cards -->
      <div v-if="results.length" class="summary-grid">
        <div class="summary-card">
          <div class="s-icon">🎯</div>
          <div class="s-value" :class="avgConfidenceClass">{{ avgConfidence }}%</div>
          <div class="s-label">Avg Confidence</div>
          <div class="s-bar"><div class="s-fill" :class="avgConfidenceClass" :style="{ width: avgConfidence + '%' }"></div></div>
        </div>
        <div class="summary-card">
          <div class="s-icon">⚡</div>
          <div class="s-value green">{{ avgTime }}s</div>
          <div class="s-label">Avg Response Time</div>
          <div class="s-bar"><div class="s-fill green" :style="{ width: Math.min(avgTime * 20, 100) + '%' }"></div></div>
        </div>
        <div class="summary-card">
          <div class="s-icon">✅</div>
          <div class="s-value green">{{ passRate }}%</div>
          <div class="s-label">Pass Rate (≥50%)</div>
          <div class="s-bar"><div class="s-fill green" :style="{ width: passRate + '%' }"></div></div>
        </div>
        <div class="summary-card">
          <div class="s-icon">📄</div>
          <div class="s-value green">{{ totalDocs }}</div>
          <div class="s-label">Documents in KB</div>
          <div class="s-bar"><div class="s-fill green" :style="{ width: Math.min(totalDocs * 10, 100) + '%' }"></div></div>
        </div>
      </div>

      <!-- Confidence chart -->
      <div v-if="results.length" class="chart-card">
        <div class="chart-title">📈 Confidence Score per Question</div>
        <div class="bar-chart">
          <div
            v-for="(r, i) in results" :key="i"
            class="bar-wrap"
            :title="`${r.question}\nConfidence: ${r.confidence}%\nTime: ${r.time}s`"
          >
            <div class="bar-label">Q{{ i + 1 }}</div>
            <div class="bar-track">
              <div
                class="bar-fill"
                :class="scoreClass(r.confidence)"
                :style="{ height: r.confidence + '%' }"
              ></div>
            </div>
            <div class="bar-value" :class="scoreClass(r.confidence)">{{ r.confidence }}%</div>
          </div>
        </div>
        <div class="chart-legend">
          <span class="legend-item high">🟢 High (≥70%)</span>
          <span class="legend-item mid">🟠 Medium (40-70%)</span>
          <span class="legend-item low">🔴 Low (&lt;40%)</span>
        </div>
      </div>

      <!-- Detailed results table -->
      <div v-if="results.length" class="results-card">
        <div class="results-title">🧪 Detailed Test Results</div>
        <div class="results-table">
          <div class="table-header">
            <span>Question</span>
            <span>Confidence</span>
            <span>Time</span>
            <span>Top Source</span>
            <span>Status</span>
          </div>
          <div v-for="(r, i) in results" :key="i" class="table-row">
            <span class="q-cell" :title="r.question">{{ r.question.substring(0, 45) }}{{ r.question.length > 45 ? '...' : '' }}</span>
            <span class="conf-cell">
              <span class="conf-badge" :class="scoreClass(r.confidence)">{{ r.confidence }}%</span>
            </span>
            <span class="time-cell">{{ r.time }}s</span>
            <span class="src-cell" :title="r.topSource">{{ r.topSource.split('\\').pop().replace('.pdf','').substring(0,20) }}...</span>
            <span class="status-cell">
              <span class="status-badge" :class="r.confidence >= 50 ? 'pass' : 'fail'">
                {{ r.confidence >= 50 ? '✅ Pass' : '❌ Fail' }}
              </span>
            </span>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="!results.length && !running" class="empty-state">
        <div class="empty-icon">🔬</div>
        <h3>No evaluation run yet</h3>
        <p>Click "Run Evaluation Suite" to test your RAG system with predefined questions and measure its performance.</p>
      </div>

      <!-- Running state -->
      <div v-if="running" class="running-state">
        <div v-for="(q, i) in testQuestions" :key="i" class="test-item" :class="testStatus[i]">
          <span class="test-icon">
            <span v-if="testStatus[i] === 'done'">✅</span>
            <span v-else-if="testStatus[i] === 'running'" class="mini-spinner"></span>
            <span v-else>⏳</span>
          </span>
          <span class="test-q">{{ q.question }}</span>
          <span v-if="testStatus[i] === 'done'" class="test-score" :class="scoreClass(results[i]?.confidence)">
            {{ results[i]?.confidence }}%
          </span>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

defineEmits(['back'])

const running    = ref(false)
const results    = ref([])
const testStatus = ref([])
const totalDocs  = ref(0)

const testQuestions = [
  { question: "What are the main causes of food waste in the world?",          lang: "en" },
  { question: "How can households reduce food waste at home?",                  lang: "en" },
  { question: "What does the FAO report say about food waste?",                 lang: "en" },
  { question: "What food waste policies exist in Tunisia?",                     lang: "en" },
  { question: "What are the best composting practices?",                        lang: "en" },
  { question: "What are the environmental impacts of food waste?",              lang: "en" },
  { question: "How can restaurants reduce food waste?",                         lang: "en" },
  { question: "What is the global percentage of food wasted each year?",        lang: "en" },
  { question: "Comment réduire le gaspillage alimentaire dans les restaurants?", lang: "fr" },
  { question: "ما هي أسباب هدر الطعام في العالم؟",                             lang: "ar" },
]

const avgConfidence = computed(() => {
  if (!results.value.length) return 0
  return Math.round(results.value.reduce((a, b) => a + b.confidence, 0) / results.value.length)
})

const avgTime = computed(() => {
  if (!results.value.length) return 0
  return (results.value.reduce((a, b) => a + b.time, 0) / results.value.length).toFixed(1)
})

const passRate = computed(() => {
  if (!results.value.length) return 0
  return Math.round(results.value.filter(r => r.confidence >= 50).length / results.value.length * 100)
})

const avgConfidenceClass = computed(() => scoreClass(avgConfidence.value))

function scoreClass(score) {
  if (score >= 70) return 'high'
  if (score >= 40) return 'mid'
  return 'low'
}

async function runEvaluation() {
  running.value  = true
  results.value  = []
  testStatus.value = testQuestions.map(() => 'pending')

  // Fetch doc count
  try {
    const r = await fetch('http://localhost:8000/documents')
    const d = await r.json()
    totalDocs.value = d.total || 0
  } catch {}

  for (let i = 0; i < testQuestions.length; i++) {
    testStatus.value[i] = 'running'
    const start = Date.now()
    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testQuestions[i])
      })
      const data = await res.json()
      const time = ((Date.now() - start) / 1000).toFixed(1)
      results.value.push({
        question:   testQuestions[i].question,
        confidence: parseFloat(data.confidence) || 0,
        time:       parseFloat(time),
        topSource:  data.sources?.[0]?.source || 'N/A',
        answer:     data.answer
      })
    } catch {
      results.value.push({ question: testQuestions[i].question, confidence: 0, time: 0, topSource: 'Error', answer: '' })
    }
    testStatus.value[i] = 'done'
  }
  running.value = false
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@400;500;700;800&family=Lora:ital,wght@0,600;1,400&display=swap');

.eval-page {
  --forest: #1a3a1e; --moss: #2d5a32; --sage: #4a8c52; --mint: #7bc47f;
  --cream: #f4f0e6;  --warm: #ede6d6; --white: #ffffff;
  --text: #1a2e1c;   --text-mid: #4a6b4c; --text-lt: #7a9a7c;
  min-height: 100vh; background: var(--cream);
  font-family: 'Cabinet Grotesk', sans-serif; color: var(--text);
  position: relative; overflow-x: hidden;
}

.bg-leaves { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.leaf { position: absolute; font-size: 1.5rem; opacity: 0.06; animation: leafFloat linear infinite; }
.leaf-1 { left: 5%;  top: 10%; animation-duration: 18s; font-size: 2rem; }
.leaf-2 { left: 85%; top: 20%; animation-duration: 22s; animation-delay: 3s; }
.leaf-3 { left: 15%; top: 60%; animation-duration: 16s; animation-delay: 6s; }
.leaf-4 { left: 70%; top: 70%; animation-duration: 20s; animation-delay: 1s; font-size: 1.8rem; }
.leaf-5 { left: 40%; top: 5%;  animation-duration: 25s; animation-delay: 8s; }
.leaf-6 { left: 90%; top: 50%; animation-duration: 19s; animation-delay: 4s; }
@keyframes leafFloat { 0%,100% { transform: translateY(0) rotate(0deg); opacity:.06; } 50% { transform: translateY(-30px) rotate(15deg); opacity:.1; } }

.header { position: sticky; top: 0; z-index: 100; background: rgba(244,240,230,0.88); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(74,140,82,0.2); padding: .9rem 0; }
.header-inner { max-width: 960px; margin: 0 auto; padding: 0 1.5rem; display: flex; align-items: center; justify-content: space-between; }
.logo { display: flex; align-items: center; gap: .6rem; }
.logo-img { width: 36px; height: 36px; object-fit: contain; }
.logo-text { font-size: 1.2rem; font-weight: 800; color: var(--forest); }
.logo-text em { font-style: normal; color: var(--sage); }
.back-btn { background: var(--warm); border: 1px solid rgba(74,140,82,0.3); color: var(--moss); border-radius: 10px; padding: .4rem 1rem; font-family: inherit; font-size: .85rem; font-weight: 600; cursor: pointer; transition: all .2s; }
.back-btn:hover { background: #dff0e0; }

.container { max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; position: relative; z-index: 1; }

.page-title { margin-bottom: 2rem; }
.page-title h1 { font-family: 'Lora', serif; font-size: 2rem; color: var(--forest); margin-bottom: .4rem; }
.page-title p { color: var(--text-mid); font-size: 1rem; }

.run-section { display: flex; align-items: center; gap: 1.2rem; margin-bottom: 2rem; flex-wrap: wrap; }
.run-btn { background: linear-gradient(135deg, var(--sage), var(--forest)); color: white; border: none; border-radius: 14px; padding: .9rem 2rem; font-family: inherit; font-size: 1rem; font-weight: 700; cursor: pointer; transition: opacity .2s, transform .15s; box-shadow: 0 6px 20px rgba(26,58,30,0.25); display: flex; align-items: center; gap: .5rem; }
.run-btn:hover:not(:disabled) { opacity: .9; transform: translateY(-1px); }
.run-btn:disabled { opacity: .6; cursor: not-allowed; }
.run-note { font-size: .82rem; color: var(--text-lt); }

/* Summary cards */
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.summary-card { background: var(--white); border: 1px solid rgba(74,140,82,0.15); border-radius: 18px; padding: 1.5rem 1.2rem; text-align: center; box-shadow: 0 4px 16px rgba(26,58,30,0.06); }
.s-icon { font-size: 1.8rem; margin-bottom: .4rem; }
.s-value { font-size: 2rem; font-weight: 800; margin-bottom: .2rem; }
.s-value.green { color: #2e7d32; }
.s-value.high  { color: #2e7d32; }
.s-value.mid   { color: #e65100; }
.s-value.low   { color: #c62828; }
.s-label { font-size: .75rem; color: var(--text-lt); text-transform: uppercase; letter-spacing: .08em; margin-bottom: .6rem; }
.s-bar { height: 5px; background: #e8f5e9; border-radius: 3px; overflow: hidden; }
.s-fill { height: 100%; border-radius: 3px; transition: width .8s ease; }
.s-fill.green { background: linear-gradient(90deg, #66bb6a, #2e7d32); }
.s-fill.high  { background: linear-gradient(90deg, #66bb6a, #2e7d32); }
.s-fill.mid   { background: linear-gradient(90deg, #ffa726, #e65100); }
.s-fill.low   { background: linear-gradient(90deg, #ef5350, #c62828); }

/* Chart */
.chart-card { background: var(--white); border: 1px solid rgba(74,140,82,0.15); border-radius: 18px; padding: 1.8rem; margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(26,58,30,0.06); }
.chart-title { font-weight: 700; font-size: 1rem; color: var(--forest); margin-bottom: 1.5rem; }
.bar-chart { display: flex; align-items: flex-end; gap: .6rem; height: 180px; padding-bottom: 2rem; border-bottom: 1px solid #e8f5e9; }
.bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: .3rem; height: 100%; justify-content: flex-end; }
.bar-label { font-size: .68rem; color: var(--text-lt); font-weight: 600; }
.bar-track { width: 100%; flex: 1; background: #f0f7f0; border-radius: 6px 6px 0 0; display: flex; align-items: flex-end; overflow: hidden; }
.bar-fill { width: 100%; border-radius: 6px 6px 0 0; transition: height .8s cubic-bezier(.22,.68,0,1.2); min-height: 4px; }
.bar-fill.high { background: linear-gradient(180deg, #66bb6a, #2e7d32); }
.bar-fill.mid  { background: linear-gradient(180deg, #ffa726, #e65100); }
.bar-fill.low  { background: linear-gradient(180deg, #ef5350, #c62828); }
.bar-value { font-size: .7rem; font-weight: 700; }
.bar-value.high { color: #2e7d32; }
.bar-value.mid  { color: #e65100; }
.bar-value.low  { color: #c62828; }
.chart-legend { display: flex; gap: 1.5rem; margin-top: 1rem; }
.legend-item { font-size: .78rem; color: var(--text-mid); }

/* Results table */
.results-card { background: var(--white); border: 1px solid rgba(74,140,82,0.15); border-radius: 18px; padding: 1.8rem; margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(26,58,30,0.06); }
.results-title { font-weight: 700; font-size: 1rem; color: var(--forest); margin-bottom: 1.2rem; }
.results-table { width: 100%; }
.table-header { display: grid; grid-template-columns: 3fr 1fr 1fr 2fr 1fr; gap: .5rem; padding: .6rem .8rem; background: #f0f7f0; border-radius: 8px; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: var(--text-lt); margin-bottom: .4rem; }
.table-row { display: grid; grid-template-columns: 3fr 1fr 1fr 2fr 1fr; gap: .5rem; padding: .7rem .8rem; border-bottom: 1px solid #f0ece3; font-size: .85rem; align-items: center; transition: background .15s; }
.table-row:hover { background: #fafaf6; }
.table-row:last-child { border-bottom: none; }
.q-cell { color: var(--text); }
.conf-badge { padding: .2rem .6rem; border-radius: 8px; font-size: .78rem; font-weight: 700; }
.conf-badge.high { background: #e8f5e9; color: #2e7d32; }
.conf-badge.mid  { background: #fff3e0; color: #e65100; }
.conf-badge.low  { background: #ffebee; color: #c62828; }
.time-cell { color: var(--text-mid); }
.src-cell { color: var(--text-lt); font-size: .78rem; }
.status-badge { padding: .2rem .6rem; border-radius: 8px; font-size: .78rem; font-weight: 600; }
.status-badge.pass { background: #e8f5e9; color: #2e7d32; }
.status-badge.fail { background: #ffebee; color: #c62828; }

/* Empty / running state */
.empty-state { text-align: center; padding: 4rem 2rem; }
.empty-icon { font-size: 4rem; margin-bottom: 1rem; }
.empty-state h3 { font-family: 'Lora', serif; font-size: 1.5rem; color: var(--forest); margin-bottom: .5rem; }
.empty-state p { color: var(--text-lt); max-width: 400px; margin: 0 auto; line-height: 1.6; }

.running-state { display: flex; flex-direction: column; gap: .6rem; background: var(--white); border-radius: 18px; padding: 1.5rem; border: 1px solid rgba(74,140,82,0.15); }
.test-item { display: flex; align-items: center; gap: .8rem; padding: .6rem .8rem; border-radius: 10px; font-size: .88rem; transition: background .2s; }
.test-item.running { background: #f0f7f0; }
.test-item.done    { background: #fafafa; color: var(--text-lt); }
.test-icon { flex-shrink: 0; width: 20px; text-align: center; }
.test-q { flex: 1; }
.test-score { font-weight: 700; font-size: .82rem; }
.test-score.high { color: #2e7d32; }
.test-score.mid  { color: #e65100; }
.test-score.low  { color: #c62828; }

.mini-spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(74,140,82,0.3); border-top-color: var(--sage); border-radius: 50%; animation: spin .7s linear infinite; }

.spinner-wrap { display: flex; align-items: center; gap: .5rem; }
.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin .7s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 650px) {
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
  .table-header, .table-row { grid-template-columns: 2fr 1fr 1fr; }
  .table-header span:nth-child(4), .table-row span:nth-child(4),
  .table-header span:nth-child(5), .table-row span:nth-child(5) { display: none; }
}
</style>