<template>
  <EvalDashboard v-if="showEval" @back="showEval = false" />
  <div v-else class="app" :dir="lang === 'ar' ? 'rtl' : 'ltr'">

    <!-- Floating leaves background -->
    <div class="bg-leaves">
      <span v-for="i in 8" :key="i" class="leaf" :class="`leaf-${i}`">🍃</span>
    </div>

    <!-- ── HEADER ── -->
    <header class="header">
      <div class="header-inner">
        <div class="logo">
          <img src="/robot.png" alt="FoodWise" class="logo-img" />
          <span class="logo-text">FoodWise <em>AI</em></span>
        </div>
        <div class="header-right">
          <div class="header-badge">🌱 {{ t.badge }}</div>
          <button class="eval-btn" @click="showEval = true">📊 Evaluation</button>
          <!-- Language switcher -->
          <div class="lang-switcher">
            <button
              v-for="l in languages" :key="l.code"
              class="lang-btn"
              :class="{ active: lang === l.code }"
              @click="lang = l.code"
            >
              {{ l.flag }} {{ l.label }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="container">

      <!-- ── HERO ── -->
      <section class="hero">
        <div class="hero-content">
          <div class="hero-text">
            <div class="hero-tag">🌿 {{ t.heroTag }}</div>
            <h1>{{ t.heroTitle }}<br/><span class="accent">{{ t.heroAccent }}</span></h1>
            <p>{{ t.heroSub }}</p>
          </div>
          <div class="hero-visual">
            <div class="robot-ring">
              <img src="/robot.png" alt="FoodWise Robot" class="hero-robot" />
              <div class="ring ring-1"></div>
              <div class="ring ring-2"></div>
              <div class="ring ring-3"></div>
            </div>
          </div>
        </div>
        <div class="stats-bar">
          <div class="stat"><span class="stat-num">{{ documents.length || 0 }}</span><span class="stat-label">{{ t.statPdfs }}</span></div>
          <div class="stat-div"></div>
          <div class="stat"><span class="stat-num">FAO</span><span class="stat-label">{{ t.statFao }}</span></div>
          <div class="stat-div"></div>
          <div class="stat"><span class="stat-num">UNEP</span><span class="stat-label">{{ t.statUnep }}</span></div>
          <div class="stat-div"></div>
          <div class="stat"><span class="stat-num">RAG</span><span class="stat-label">{{ t.statRag }}</span></div>
        </div>
      </section>

      <!-- ── SEARCH ── -->
      <section class="search-section">
        <div class="search-box">
          <div class="search-icon">🔍</div>
          <input
            v-model="query"
            type="text"
            :placeholder="t.placeholder"
            class="search-input"
            @keydown.enter="handleAsk"
          />
          <button class="ask-btn" :disabled="loading || !query.trim()" @click="handleAsk">
            <span v-if="!loading">{{ t.askBtn }}</span>
            <span v-else class="spinner-wrap"><span class="spinner"></span> {{ t.thinking }}</span>
          </button>
        </div>
        <div class="hint-chips">
          <button
            v-for="hint in t.hints" :key="hint.label"
            class="chip"
            @click="query = hint.query; handleAsk()"
          >
            {{ hint.icon }} {{ hint.label }}
          </button>
        </div>
      </section>

      <!-- ── UPLOAD ── -->
      <section class="upload-section">
        <div class="upload-header" @click="showUpload = !showUpload">
          <span>📄 {{ t.uploadTitle }}</span>
          <span class="upload-toggle">{{ showUpload ? '▲' : '▼' }}</span>
        </div>
        <Transition name="fade">
          <div v-if="showUpload" class="upload-body">
            <div
              class="drop-zone"
              :class="{ dragging: isDragging, uploading: uploading }"
              @dragover.prevent="isDragging = true"
              @dragleave="isDragging = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
            >
              <input ref="fileInput" type="file" accept=".pdf" style="display:none" @change="handleFileChange" />
              <div v-if="!uploading">
                <div class="drop-icon">📂</div>
                <p class="drop-text">{{ t.dropText }}</p>
                <p class="drop-sub">{{ t.dropSub }}</p>
              </div>
              <div v-else class="upload-progress">
                <div class="spinner"></div>
                <p>{{ t.uploading }}</p>
              </div>
            </div>

            <!-- Upload result -->
            <Transition name="fade">
              <div v-if="uploadResult" class="upload-result" :class="uploadResult.error ? 'error' : 'success'">
                <span>{{ uploadResult.error ? '❌' : '✅' }}</span>
                <div>
                  <strong>{{ uploadResult.filename }}</strong>
                  <p>{{ uploadResult.message }}</p>
                </div>
              </div>
            </Transition>

            <!-- Document list -->
            <div v-if="documents.length" class="doc-list">
              <div class="doc-list-title">{{ t.docList }} ({{ documents.length }})</div>
              <div v-for="doc in documents" :key="doc" class="doc-item">
                📄 {{ doc }}
              </div>
            </div>
          </div>
        </Transition>
      </section>

      <!-- ── LOADING ── -->
      <Transition name="fade">
        <div v-if="loading" class="loading-card">
          <div class="loading-robot">
            <img src="/robot.png" alt="thinking" class="thinking-robot" />
            <div class="thought-bubbles">
              <span class="bubble b1"></span>
              <span class="bubble b2"></span>
              <span class="bubble b3"></span>
            </div>
          </div>
          <div class="loading-text">
            <p class="loading-title">{{ t.loadingTitle }}</p>
            <div class="loading-bar"><div class="loading-fill"></div></div>
            <p class="loading-sub">{{ t.loadingSub }}</p>
          </div>
        </div>
      </Transition>

      <!-- ── ERROR ── -->
      <Transition name="fade">
        <div v-if="error" class="error-card">
          <span class="error-icon">⚠️</span>
          <div>
            <strong>{{ t.errorTitle }}</strong>
            <p>{{ error }}</p>
          </div>
        </div>
      </Transition>

      <!-- ── CHAT HISTORY ── -->
      <div class="chat-history" v-if="history.length">
        <div class="history-label">💬 {{ t.conversation }}</div>
        <TransitionGroup name="slide-up" tag="div">
          <div v-for="(item, idx) in history" :key="idx" class="chat-item">
            <div class="chat-question">
              <div class="q-avatar">{{ t.you }}</div>
              <div class="q-bubble">{{ item.question }}</div>
            </div>
            <div class="chat-answer">
              <div class="a-avatar">
                <img src="/robot.png" alt="AI" class="a-robot-img" />
              </div>
              <div class="a-content">
                <!-- Confidence score -->
                <div class="confidence-bar">
                  <div class="confidence-header">
                    <span class="confidence-label">{{ lang === 'ar' ? 'مستوى الثقة' : lang === 'fr' ? 'Niveau de confiance' : 'Confidence Score' }}</span>
                    <span class="confidence-value" :class="confidenceClass(item.confidence)">{{ item.confidence }}%</span>
                  </div>
                  <div class="confidence-track">
                    <div class="confidence-fill" :class="confidenceClass(item.confidence)" :style="{ width: item.confidence + '%' }"></div>
                  </div>
                </div>
                <div class="a-bubble" v-html="renderMarkdown(item.answer)"></div>
                <div v-if="item.sources?.length" class="sources-row">
                  <span class="sources-label">{{ t.sources }}:</span>
                  <span
                    v-for="(src, si) in item.sources" :key="si"
                    class="source-tag" :title="src.snippet"
                  >
                    📄 {{ src.source.split('\\').pop().replace('.pdf','') }}
                    <span class="src-score">{{ src.score }}%</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>
        <button class="clear-btn" @click="history = []">🗑 {{ t.clearHistory }}</button>
      </div>

    </main>

    <footer class="footer">
      <div class="footer-inner">
        <span>🌿 FoodWise AI</span>
        <span>·</span>
        <span>LLaMA 3.2 · FAISS · LangChain · Vue 3</span>
        <span>·</span>
        <span>{{ t.footerSlogan }}</span>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import EvalDashboard from './EvalDashboard.vue'
import { askQuestion } from './api.js'

const showEval = ref(false)
const query   = ref('')
const showUpload   = ref(false)
const isDragging   = ref(false)
const uploading    = ref(false)
const uploadResult = ref(null)
const documents    = ref([])
const loading = ref(false)
const error   = ref(null)
const history = ref([])
const lang    = ref('en')

const languages = [
  { code: 'en', label: 'EN', flag: '🇬🇧' },
  { code: 'fr', label: 'FR', flag: '🇫🇷' },
  { code: 'ar', label: 'AR', flag: '🇹🇳' },
]

const translations = {
  en: {
    badge: 'Eco Intelligence',
    heroTag: 'Powered by RAG + LLaMA',
    heroTitle: 'Fight Food Waste',
    heroAccent: 'Intelligently',
    heroSub: 'Ask anything about food waste reduction, composting, policy, and sustainable practices — backed by real research.',
    placeholder: 'Ask about food waste, composting, policies...',
    askBtn: 'Ask →',
    thinking: 'Thinking...',
    loadingTitle: 'Searching knowledge base...',
    loadingSub: 'Reading through FAO & UNEP reports 📄',
    errorTitle: 'Something went wrong',
    conversation: 'Conversation',
    you: 'You',
    sources: 'Sources',
    clearHistory: 'Clear history',
    footerSlogan: 'Fighting food waste with intelligence',
    statPdfs: 'Research PDFs',
    statFao: 'Data Source',
    statUnep: 'Reports',
    statRag: 'AI System',
    uploadTitle: '📄 Upload a PDF Document',
    dropText: 'Click or drag & drop a PDF here',
    dropSub: 'The document will be instantly added to the knowledge base',
    uploading: 'Processing document...',
    docList: 'Knowledge base documents',
    hints: [
      { icon: '🥦', label: 'Household waste',   query: 'How can households reduce food waste at home?' },
      { icon: '🏪', label: 'Supermarkets',       query: 'What are supermarket surplus food solutions?' },
      { icon: '♻️', label: 'Composting',         query: 'What are the best composting practices?' },
      { icon: '📜', label: 'Tunisia policy',     query: 'What food waste policies exist in Tunisia?' },
      { icon: '📊', label: 'FAO statistics',     query: 'What does the FAO report say about food waste?' },
    ],
  },
  fr: {
    badge: 'Intelligence Écologique',
    heroTag: 'Propulsé par RAG + LLaMA',
    heroTitle: 'Luttez Contre le\nGaspillage',
    heroAccent: 'Intelligemment',
    heroSub: 'Posez toutes vos questions sur la réduction du gaspillage alimentaire, le compostage, les politiques et les pratiques durables.',
    placeholder: 'Posez une question sur le gaspillage alimentaire...',
    askBtn: 'Demander →',
    thinking: 'Réflexion...',
    loadingTitle: 'Recherche dans la base de connaissances...',
    loadingSub: 'Lecture des rapports FAO & PNUE 📄',
    errorTitle: "Une erreur s'est produite",
    conversation: 'Conversation',
    you: 'Vous',
    sources: 'Sources',
    clearHistory: "Effacer l'historique",
    footerSlogan: 'Lutter contre le gaspillage avec intelligence',
    statPdfs: 'PDFs de Recherche',
    statFao: 'Source de Données',
    statUnep: 'Rapports',
    statRag: 'Système IA',
    uploadTitle: '📄 Télécharger un document PDF',
    dropText: 'Cliquez ou glissez un PDF ici',
    dropSub: 'Le document sera ajouté instantanément à la base de connaissances',
    uploading: 'Traitement du document...',
    docList: 'Documents dans la base',
    hints: [
      { icon: '🥦', label: 'Ménages',            query: 'Comment les ménages peuvent-ils réduire le gaspillage alimentaire?' },
      { icon: '🏪', label: 'Supermarchés',        query: 'Quelles sont les solutions pour les surplus alimentaires en supermarché?' },
      { icon: '♻️', label: 'Compostage',          query: 'Quelles sont les meilleures pratiques de compostage?' },
      { icon: '📜', label: 'Politique Tunisie',   query: 'Quelles politiques sur le gaspillage alimentaire existent en Tunisie?' },
      { icon: '📊', label: 'Statistiques FAO',    query: 'Que dit le rapport FAO sur le gaspillage alimentaire?' },
    ],
  },
  ar: {
    badge: 'الذكاء البيئي',
    heroTag: 'مدعوم بـ RAG + LLaMA',
    heroTitle: 'قاوم هدر الطعام',
    heroAccent: 'بذكاء',
    heroSub: 'اسأل عن تقليل هدر الطعام والتسميد والسياسات والممارسات المستدامة — مدعوم بأبحاث حقيقية.',
    placeholder: 'اسأل عن هدر الطعام، التسميد، السياسات...',
    askBtn: 'اسأل ←',
    thinking: 'جاري التفكير...',
    loadingTitle: 'البحث في قاعدة المعرفة...',
    loadingSub: 'قراءة تقارير FAO و UNEP 📄',
    errorTitle: 'حدث خطأ ما',
    conversation: 'المحادثة',
    you: 'أنت',
    sources: 'المصادر',
    clearHistory: 'مسح المحادثة',
    footerSlogan: 'محاربة هدر الطعام بالذكاء',
    statPdfs: 'ملفات بحثية',
    statFao: 'مصدر البيانات',
    statUnep: 'تقارير',
    statRag: 'نظام ذكاء',
    uploadTitle: '📄 رفع ملف PDF',
    dropText: 'انقر أو اسحب ملف PDF هنا',
    dropSub: 'سيتم إضافة الوثيقة فوراً إلى قاعدة المعرفة',
    uploading: 'جاري معالجة الوثيقة...',
    docList: 'وثائق قاعدة المعرفة',
    hints: [
      { icon: '🥦', label: 'المنازل',            query: 'كيف يمكن للأسر تقليل هدر الطعام في المنزل؟' },
      { icon: '🏪', label: 'المتاجر الكبرى',     query: 'ما هي حلول الفائض الغذائي في المتاجر الكبرى؟' },
      { icon: '♻️', label: 'التسميد',            query: 'ما هي أفضل ممارسات التسميد؟' },
      { icon: '📜', label: 'سياسة تونس',         query: 'ما هي سياسات هدر الطعام الموجودة في تونس؟' },
      { icon: '📊', label: 'إحصاءات FAO',        query: 'ماذا يقول تقرير الفاو عن هدر الطعام؟' },
    ],
  },
}

const t = computed(() => translations[lang.value])

async function fetchDocuments() {
  try {
    const res = await fetch('http://localhost:8000/documents')
    const data = await res.json()
    documents.value = data.documents || []
  } catch {}
}

async function uploadFile(file) {
  if (!file || !file.name.endsWith('.pdf')) {
    uploadResult.value = { error: true, filename: file?.name || '', message: 'Only PDF files allowed!' }
    return
  }
  uploading.value = true
  uploadResult.value = null
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await fetch('http://localhost:8000/upload', { method: 'POST', body: formData })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Upload failed')
    uploadResult.value = { error: false, filename: data.filename, message: data.message }
    await fetchDocuments()
  } catch (e) {
    uploadResult.value = { error: true, filename: file.name, message: e.message }
  } finally {
    uploading.value = false
  }
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) uploadFile(file)
}

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) uploadFile(file)
}

// Load documents on mount
fetchDocuments()

async function handleAsk() {
  if (!query.value.trim() || loading.value) return
  const q = query.value.trim()
  query.value = ''
  loading.value = true
  error.value = null
  try {
    const result = await askQuestion(q, lang.value)
    history.value.unshift({ question: q, answer: result.answer, sources: result.sources, confidence: parseFloat(result.confidence) || 0 })
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Backend not reachable. Is it running on port 8000?'
  } finally {
    loading.value = false
  }
}

function confidenceClass(score) {
  if (score >= 70) return 'high'
  if (score >= 40) return 'mid'
  return 'low'
}

function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^(\d+\.\s)/gm, '<br>$1')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@400;500;700;800&family=Lora:ital,wght@0,400;0,600;1,400&family=Tajawal:wght@300;400;500;700&display=swap');

.app {
  --forest:   #1a3a1e;
  --moss:     #2d5a32;
  --sage:     #4a8c52;
  --mint:     #7bc47f;
  --cream:    #f4f0e6;
  --warm:     #ede6d6;
  --paper:    #faf7f0;
  --text:     #1a2e1c;
  --text-mid: #4a6b4c;
  --text-lt:  #7a9a7c;
  --white:    #ffffff;
  min-height: 100vh;
  background: var(--cream);
  font-family: 'Cabinet Grotesk', sans-serif;
  color: var(--text);
  position: relative;
  overflow-x: hidden;
}

/* Arabic font override */
.app[dir="rtl"] { font-family: 'Tajawal', sans-serif; }
.app[dir="rtl"] .hero-text h1 { font-family: 'Tajawal', sans-serif; font-weight: 700; }
.app[dir="rtl"] .q-bubble { border-radius: 18px 18px 18px 4px; }
.app[dir="rtl"] .a-bubble { border-radius: 18px 4px 18px 18px; }
.app[dir="rtl"] .chat-question { flex-direction: row-reverse; }
.app[dir="rtl"] .chat-answer { flex-direction: row-reverse; }

/* ── Floating leaves ── */
.bg-leaves { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.leaf { position: absolute; font-size: 1.5rem; opacity: 0.07; animation: leafFloat linear infinite; }
.leaf-1 { left: 5%;  top: 10%; animation-duration: 18s; font-size: 2rem; }
.leaf-2 { left: 85%; top: 20%; animation-duration: 22s; animation-delay: 3s; font-size: 1.2rem; }
.leaf-3 { left: 15%; top: 60%; animation-duration: 16s; animation-delay: 6s; }
.leaf-4 { left: 70%; top: 70%; animation-duration: 20s; animation-delay: 1s; font-size: 1.8rem; }
.leaf-5 { left: 40%; top: 5%;  animation-duration: 25s; animation-delay: 8s; }
.leaf-6 { left: 90%; top: 50%; animation-duration: 19s; animation-delay: 4s; font-size: 1.1rem; }
.leaf-7 { left: 25%; top: 85%; animation-duration: 23s; animation-delay: 2s; font-size: 2.2rem; }
.leaf-8 { left: 60%; top: 40%; animation-duration: 17s; animation-delay: 9s; font-size: 1.3rem; }
@keyframes leafFloat {
  0%,100% { transform: translateY(0px) rotate(0deg); opacity: 0.07; }
  50%      { transform: translateY(-30px) rotate(15deg); opacity: 0.12; }
}

/* ── Header ── */
.header {
  position: sticky; top: 0; z-index: 100;
  background: rgba(244,240,230,0.88);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(74,140,82,0.2);
  padding: 0.9rem 0;
}
.header-inner {
  max-width: 900px; margin: 0 auto; padding: 0 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.logo { display: flex; align-items: center; gap: 0.6rem; }
.logo-img { width: 36px; height: 36px; object-fit: contain; }
.logo-text { font-size: 1.2rem; font-weight: 800; color: var(--forest); letter-spacing: -0.5px; }
.logo-text em { font-style: normal; color: var(--sage); }
.header-right { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; justify-content: flex-end; }
.header-badge {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  color: var(--moss); font-size: 0.75rem; font-weight: 700;
  padding: 0.3rem 0.8rem; border-radius: 20px;
  border: 1px solid rgba(74,140,82,0.3); letter-spacing: 0.03em;
}

/* ── Eval button ── */
.eval-btn {
  background: linear-gradient(135deg, var(--sage), var(--moss));
  color: white; border: none; border-radius: 10px;
  padding: .35rem .9rem; font-family: inherit;
  font-size: .78rem; font-weight: 700;
  cursor: pointer; transition: opacity .2s;
}
.eval-btn:hover { opacity: .85; }

/* ── Language switcher ── */
.lang-switcher { display: flex; gap: 0.3rem; background: var(--warm); border-radius: 10px; padding: 0.25rem; border: 1px solid rgba(74,140,82,0.2); }
.lang-btn {
  background: transparent; border: none;
  color: var(--text-mid); font-size: 0.78rem; font-weight: 600;
  font-family: 'Cabinet Grotesk', sans-serif;
  padding: 0.3rem 0.65rem; border-radius: 7px;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
}
.lang-btn:hover { background: rgba(74,140,82,0.1); color: var(--moss); }
.lang-btn.active { background: var(--moss); color: white; box-shadow: 0 2px 8px rgba(45,90,50,0.3); }

/* ── Container ── */
.container { max-width: 900px; margin: 0 auto; padding: 2rem 1.5rem; position: relative; z-index: 1; }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, var(--forest) 0%, var(--moss) 50%, #3d7a45 100%);
  border-radius: 28px; padding: 3rem 3rem 0;
  margin-bottom: 2rem; overflow: hidden; position: relative;
  box-shadow: 0 20px 60px rgba(26,58,30,0.3);
}
.hero::before {
  content: ''; position: absolute; inset: 0; pointer-events: none;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E");
}
.hero-content { display: flex; align-items: center; gap: 2rem; margin-bottom: 2.5rem; }
.hero-text { flex: 1; }
.hero-tag {
  display: inline-block; background: rgba(255,255,255,0.15);
  color: #a8d5aa; font-size: 0.75rem; font-weight: 700;
  padding: 0.35rem 0.9rem; border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.2); margin-bottom: 1rem; letter-spacing: 0.05em;
}
.hero-text h1 {
  font-family: 'Lora', serif; font-size: 2.8rem; font-weight: 600;
  color: #ffffff; line-height: 1.15; margin-bottom: 1rem; letter-spacing: -0.5px;
}
.hero-text h1 .accent { color: var(--mint); font-style: italic; }
.hero-text p { color: rgba(255,255,255,0.7); font-size: 1rem; line-height: 1.7; }
.hero-visual { flex-shrink: 0; }
.robot-ring { position: relative; width: 180px; height: 180px; display: flex; align-items: center; justify-content: center; }
.hero-robot { width: 140px; height: 140px; object-fit: contain; position: relative; z-index: 2; animation: float 3s ease-in-out infinite; filter: drop-shadow(0 10px 30px rgba(0,0,0,0.3)); }
.ring { position: absolute; border-radius: 50%; border: 1px solid rgba(255,255,255,0.15); animation: pulse 3s ease-in-out infinite; }
.ring-1 { width: 160px; height: 160px; }
.ring-2 { width: 185px; height: 185px; animation-delay: 0.5s; border-color: rgba(123,196,127,0.2); }
.ring-3 { width: 210px; height: 210px; animation-delay: 1s;   border-color: rgba(123,196,127,0.1); }

/* Stats bar */
.stats-bar {
  display: flex; align-items: center;
  background: rgba(0,0,0,0.2); border-top: 1px solid rgba(255,255,255,0.1);
  padding: 1rem 3rem; margin: 0 -3rem;
}
.stat { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stat-num { font-size: 1.1rem; font-weight: 800; color: var(--mint); }
.stat-label { font-size: 0.68rem; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.1rem; }
.stat-div { width: 1px; height: 30px; background: rgba(255,255,255,0.15); }

/* ── Search ── */
.search-section { margin-bottom: 2rem; }
.search-box {
  display: flex; align-items: center; gap: 0.75rem;
  background: var(--white); border: 2px solid rgba(74,140,82,0.25);
  border-radius: 18px; padding: 0.5rem 0.5rem 0.5rem 1.2rem;
  box-shadow: 0 4px 20px rgba(26,58,30,0.08);
  transition: border-color 0.2s, box-shadow 0.2s; margin-bottom: 1rem;
}
.search-box:focus-within { border-color: var(--sage); box-shadow: 0 4px 20px rgba(74,140,82,0.2), 0 0 0 4px rgba(74,140,82,0.08); }
.search-icon { font-size: 1.1rem; flex-shrink: 0; }
.search-input {
  flex: 1; border: none; outline: none;
  font-family: inherit; font-size: 1rem; color: var(--text); background: transparent; padding: 0.6rem 0;
}
.search-input::placeholder { color: #aab8ab; }
.ask-btn {
  background: linear-gradient(135deg, var(--sage), var(--moss));
  color: white; border: none; border-radius: 12px; padding: 0.8rem 1.6rem;
  font-family: inherit; font-size: 0.95rem; font-weight: 700;
  cursor: pointer; white-space: nowrap; transition: opacity 0.2s, transform 0.15s;
  box-shadow: 0 4px 14px rgba(45,90,50,0.3); display: flex; align-items: center; gap: 0.5rem;
}
.ask-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.ask-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.hint-chips { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.chip {
  background: var(--warm); border: 1px solid rgba(74,140,82,0.2);
  color: var(--text-mid); border-radius: 20px; padding: 0.4rem 0.9rem;
  font-size: 0.82rem; font-weight: 500; font-family: inherit;
  cursor: pointer; transition: all 0.2s;
}
.chip:hover { background: #dff0e0; border-color: var(--sage); color: var(--moss); transform: translateY(-1px); }

/* ── Loading ── */
.loading-card {
  background: var(--white); border: 1px solid rgba(74,140,82,0.2);
  border-radius: 20px; padding: 2rem; display: flex; align-items: center; gap: 1.5rem;
  box-shadow: 0 4px 20px rgba(26,58,30,0.07); margin-bottom: 1.5rem;
}
.loading-robot { position: relative; flex-shrink: 0; }
.thinking-robot { width: 60px; height: 60px; object-fit: contain; animation: float 1.5s ease-in-out infinite; }
.thought-bubbles { position: absolute; top: -8px; right: -12px; display: flex; gap: 3px; align-items: flex-end; }
.bubble { border-radius: 50%; background: var(--mint); animation: bubblePop 1.2s ease-in-out infinite; }
.b1 { width: 6px; height: 6px; }
.b2 { width: 9px; height: 9px; animation-delay: 0.2s; }
.b3 { width: 12px; height: 12px; animation-delay: 0.4s; }
.loading-text { flex: 1; }
.loading-title { font-weight: 700; color: var(--forest); margin-bottom: 0.6rem; font-size: 0.95rem; }
.loading-bar { background: #e8f5e9; border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 0.5rem; }
.loading-fill { height: 100%; background: linear-gradient(90deg, var(--mint), var(--sage)); border-radius: 4px; animation: loadingSlide 1.5s ease-in-out infinite; }
.loading-sub { font-size: 0.82rem; color: var(--text-lt); }

/* ── Error ── */
.error-card {
  background: #fff5f5; border: 1px solid #fcc; border-left: 4px solid #e05;
  border-radius: 14px; padding: 1rem 1.2rem; display: flex; align-items: flex-start; gap: 0.8rem; margin-bottom: 1.5rem;
}
.error-icon { font-size: 1.2rem; flex-shrink: 0; }
.error-card strong { color: #7a1f1f; display: block; margin-bottom: 0.2rem; }
.error-card p { color: #a05050; font-size: 0.88rem; }

/* ── Chat ── */
.chat-history { display: flex; flex-direction: column; gap: 1.5rem; }
.history-label { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-lt); padding-bottom: 0.5rem; border-bottom: 1px solid rgba(74,140,82,0.15); }
.chat-item { display: flex; flex-direction: column; gap: 0.8rem; }
.chat-question { display: flex; align-items: flex-start; gap: 0.75rem; justify-content: flex-end; }
.q-avatar { background: var(--warm); border: 1px solid rgba(74,140,82,0.2); color: var(--text-mid); font-size: 0.68rem; font-weight: 700; padding: 0.3rem 0.5rem; border-radius: 8px; flex-shrink: 0; margin-top: 0.2rem; letter-spacing: 0.05em; }
.q-bubble { background: linear-gradient(135deg, var(--moss), var(--forest)); color: white; border-radius: 18px 18px 4px 18px; padding: 0.9rem 1.2rem; font-size: 0.95rem; line-height: 1.5; max-width: 75%; box-shadow: 0 4px 14px rgba(26,58,30,0.2); }
.chat-answer { display: flex; align-items: flex-start; gap: 0.75rem; }
.a-avatar { flex-shrink: 0; margin-top: 0.2rem; }
.a-robot-img { width: 36px; height: 36px; object-fit: contain; }
.a-content { flex: 1; }
.a-bubble { background: var(--white); border: 1px solid rgba(74,140,82,0.18); border-radius: 4px 18px 18px 18px; padding: 1rem 1.3rem; font-size: 0.95rem; line-height: 1.75; color: var(--text); white-space: pre-wrap; box-shadow: 0 2px 12px rgba(26,58,30,0.06); margin-bottom: 0.5rem; }
.sources-row { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.sources-label { font-size: 0.7rem; color: var(--text-lt); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.source-tag { background: #e8f5e9; color: var(--moss); border: 1px solid rgba(74,140,82,0.25); border-radius: 8px; padding: 0.2rem 0.6rem; font-size: 0.75rem; font-weight: 500; }
.clear-btn { align-self: center; background: transparent; border: 1px solid rgba(74,140,82,0.25); color: var(--text-lt); border-radius: 10px; padding: 0.4rem 1rem; font-size: 0.8rem; font-family: inherit; cursor: pointer; transition: all 0.2s; margin-top: 0.5rem; }
.clear-btn:hover { background: #fff0f0; border-color: #fcc; color: #c05; }

/* ── Confidence bar ── */
.confidence-bar { margin-bottom: 0.8rem; }
.confidence-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem; }
.confidence-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-lt); }
.confidence-value { font-size: 0.82rem; font-weight: 800; }
.confidence-value.high { color: #2e7d32; }
.confidence-value.mid  { color: #e65100; }
.confidence-value.low  { color: #c62828; }
.confidence-track { height: 6px; background: #e8f5e9; border-radius: 4px; overflow: hidden; }
.confidence-fill { height: 100%; border-radius: 4px; transition: width 0.8s cubic-bezier(.22,.68,0,1.2); }
.confidence-fill.high { background: linear-gradient(90deg, #66bb6a, #2e7d32); }
.confidence-fill.mid  { background: linear-gradient(90deg, #ffa726, #e65100); }
.confidence-fill.low  { background: linear-gradient(90deg, #ef5350, #c62828); }
.src-score { background: rgba(74,140,82,0.15); color: var(--moss); border-radius: 4px; padding: 0 0.3rem; font-size: 0.7rem; font-weight: 700; margin-left: 0.3rem; }

/* ── Upload section ── */
.upload-section {
  background: var(--white);
  border: 1px solid rgba(74,140,82,0.2);
  border-radius: 18px;
  margin-bottom: 2rem;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(26,58,30,0.05);
}
.upload-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.5rem; cursor: pointer;
  font-size: 0.9rem; font-weight: 700; color: var(--moss);
  transition: background 0.2s;
}
.upload-header:hover { background: #f0f7f0; }
.upload-toggle { color: var(--text-lt); font-size: 0.75rem; }
.upload-body { padding: 0 1.5rem 1.5rem; }

.drop-zone {
  border: 2px dashed rgba(74,140,82,0.35);
  border-radius: 14px; padding: 2rem;
  text-align: center; cursor: pointer;
  transition: all 0.2s; background: #f8fbf8;
}
.drop-zone:hover, .drop-zone.dragging {
  border-color: var(--sage);
  background: #edf7ee;
  transform: scale(1.01);
}
.drop-zone.uploading { opacity: 0.7; cursor: not-allowed; }
.drop-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.drop-text { font-weight: 700; color: var(--moss); margin-bottom: 0.3rem; }
.drop-sub { font-size: 0.82rem; color: var(--text-lt); }
.upload-progress { display: flex; flex-direction: column; align-items: center; gap: 0.8rem; color: var(--text-mid); font-size: 0.9rem; }

.upload-result {
  display: flex; align-items: flex-start; gap: 0.8rem;
  padding: 0.9rem 1.1rem; border-radius: 12px; margin-top: 0.8rem;
  font-size: 0.88rem;
}
.upload-result.success { background: #e8f5e9; border: 1px solid #a5d6a7; color: #1b5e20; }
.upload-result.error   { background: #ffebee; border: 1px solid #ef9a9a; color: #b71c1c; }
.upload-result strong  { display: block; margin-bottom: 0.2rem; }

.doc-list { margin-top: 1rem; }
.doc-list-title { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-lt); margin-bottom: 0.5rem; }
.doc-item { font-size: 0.83rem; color: var(--text-mid); padding: 0.4rem 0; border-bottom: 1px solid #f0ece3; }
.doc-item:last-child { border-bottom: none; }

/* ── Footer ── */
.footer { background: var(--forest); color: rgba(255,255,255,0.5); padding: 1.2rem; margin-top: 3rem; position: relative; z-index: 1; }
.footer-inner { max-width: 900px; margin: 0 auto; display: flex; align-items: center; justify-content: center; gap: 0.8rem; font-size: 0.75rem; flex-wrap: wrap; }
.footer-inner span:first-child { color: var(--mint); font-weight: 700; }

/* ── Spinner ── */
.spinner-wrap { display: flex; align-items: center; gap: 0.5rem; }
.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block; }

/* ── Transitions ── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-8px); }
.slide-up-enter-active { animation: slideUp 0.4s cubic-bezier(.22,.68,0,1.2); }

/* ── Keyframes ── */
@keyframes float    { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
@keyframes pulse    { 0%,100% { transform: scale(1); opacity: 0.5; } 50% { transform: scale(1.05); opacity: 1; } }
@keyframes spin     { to { transform: rotate(360deg); } }
@keyframes bubblePop { 0%,100% { transform: scale(1); opacity: 0.6; } 50% { transform: scale(1.3); opacity: 1; } }
@keyframes loadingSlide { 0% { width: 0%; margin-left: 0; } 50% { width: 70%; } 100% { width: 0%; margin-left: 100%; } }
@keyframes slideUp  { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes leafFloat { 0%,100% { transform: translateY(0px) rotate(0deg); opacity: 0.07; } 50% { transform: translateY(-30px) rotate(15deg); opacity: 0.12; } }

/* ── Responsive ── */
@media (max-width: 650px) {
  .hero-content { flex-direction: column; text-align: center; }
  .hero-text h1 { font-size: 2rem; }
  .robot-ring { width: 130px; height: 130px; }
  .hero-robot { width: 100px; height: 100px; }
  .hero { padding: 2rem 1.5rem 0; }
  .stats-bar { padding: 0.8rem 1.5rem; margin: 0 -1.5rem; }
  .search-box { flex-wrap: wrap; }
  .ask-btn { width: 100%; justify-content: center; }
  .header-right { gap: 0.4rem; }
  .header-badge { display: none; }
}
</style>