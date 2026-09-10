// Vyapar Mitra Frontend Application Logic & Ultra-Premium Multilingual Engine

const API_BASE = (window.location.protocol === 'file:' || !window.location.origin || window.location.origin === 'null') 
  ? 'http://127.0.0.1:8000' 
  : '';

let currentLang = "marathi";
let sessionId = localStorage.getItem("vm_session_id") || ("session_" + Math.random().toString(36).substring(2, 9));
localStorage.setItem("vm_session_id", sessionId);

let currentPeriod = "daily";
let salesChartInstance = null;

let signals = {
  upi_set_up: true,
  google_maps_listed: true,
  ondc_listed: true,
  scheme_registered: false
};

let vendorProfile = {
  store_name: "Camp Fresh Fruits",
  owner_name: "Ramesh Patil",
  category: "Fresh Fruits & Seasonal Specials",
  specialities: "Bananas, Apples, Seasonal Alphonso Mangoes, Papayas, Pomegranates",
  location: "Near Main Market Road & MG Road, Camp, Pune",
  operating_hours: "7:00 AM - 8:00 PM",
  upi_id: "campfruits@upi",
  phone: "+91 98765 43210",
  agent_name: "Vyapar Mitra (व्यापार मित्र)",
  agent_tone: "warm",
  custom_discount_rule: "10% off on ripe fruits after 6:30 PM",
  daily_profit_goal: 1000.0
};

let activePosterSvg = "";
let recognition = null;
let isRecording = false;

// Comprehensive Multilingual UI Translations (Marathi, Hindi, English)
const I18N = {
  marathi: {
    agentTitle: "व्यापार मित्र AI सहाय्यक",
    agentSub: "वैयक्तिकृत सहाय्यक: ",
    voiceListening: "मराठी मध्ये ऐकत आहे... कृपया आता स्पष्ट बोला",
    voiceLang: "मराठी (Marathi)",
    chatPlaceholder: "बोला किंवा टाईप करा (उदा. ५०० रुपयांची केळी विकली... / स्वनिधी कर्ज अर्ज...)",
    welcomeHeader: (name) => `नमस्ते ${name} जी! मी आपला व्यापार मित्र AI सहाय्यक आहे 🙏`,
    welcomeText: "मी पथविक्रेत्यांना डिजिटल होण्यास मदत करतो: **पीएम स्वनिधी कर्ज अर्ज (₹१५,००० - ७% व्याज अनुदान)**, दैनंदिन विक्री व नफा हिशोब, **ONDC Beckn 1.2.0** कॅटलॉग आणि छापील UPI QR स्टँडी तयार करणे.",
    quickStart: "सुरुवात करा:",
    quickSaleBtn: "नवीन विक्री",
    clearChatBtn: "साफ करा",
    tabs: {
      chat: "AI सहाय्यक",
      reports: "📊 विक्री व हिशोब",
      loan: "🏛️ पीएम स्वनिधी कर्ज",
      ondc: "🌐 ONDC कॅटलॉग",
      maps: "🍉 APMC मंडी व नकाशे",
      studio: "🎨 क्यूआर व पोस्टर",
      score: "📈 डिजिटल स्कोअर",
      store: "🏪 माझे दुकान"
    },
    chips: [
      { text: "🚀 ऑनबोर्डिंग किट", prompt: "संपूर्ण डिजिटल ऑनबोर्डिंग किट तयार करा", color: "bg-blue-600/90" },
      { text: "🏛️ स्वनिधी कर्ज ₹१५k", prompt: "पीएम स्वनिधी पहिल्या हप्त्याचे कर्ज ₹१५,००० साठी अर्ज करा", color: "bg-purple-600/90" },
      { text: "📊 विक्री अहवाल", prompt: "साप्ताहिक विक्री आणि नफा अहवाल दाखवा", color: "bg-emerald-600/90" },
      { text: "🌐 ONDC कॅटलॉग", prompt: "ओएनडीसी (ONDC) डिजिटल स्टोअर कॅटलॉग तयार करा", color: "bg-sky-600/90" },
      { text: "🗺️ गुगल मॅप्स", prompt: "गुगल मॅप्स स्थान आणि लोकल एसईओ दाखवा", color: "bg-rose-600/90" },
      { text: "💰 हिशोब नोंदवा", prompt: "५०० रुपयांची केळी विकली, ८० रुपयांचा बर्फ घेतला", color: "bg-amber-600/90" },
      { text: "📈 डिजिटल स्कोअर", prompt: "माझा डिजिटल स्कोअर किती आहे?", color: "bg-indigo-600/90" },
      { text: "🍉 पुणे मंडी भाव", prompt: "पुणे APMC फळ मंडीचे आजचे भाव दाखवा", color: "bg-teal-600/90" },
      { text: "🎨 बॅनर प्रिंट", prompt: "स्टॉल मार्केटिंग बॅनर आणि UPI QR स्टँडी तयार करा", color: "bg-orange-600/90" },
      { text: "💬 व्हॉट्सॲप मेसेज", prompt: "व्हॉट्सॲप प्रचार संदेश तयार करा", color: "bg-green-600/90" }
    ],
    periods: { daily: "दैनंदिन", weekly: "साप्ताहिक", monthly: "मासिक", yearly: "वार्षिक" },
    kpi: { rev: "एकूण महसूल", exp: "एकूण खर्च", pro: "निव्वळ नफा", mar: "नफा दर" }
  },
  hindi: {
    agentTitle: "व्यापार मित्र AI सहायक",
    agentSub: "व्यक्तिगत सहायक: ",
    voiceListening: "हिंदी में सुन रहा हूँ... कृपया अब स्पष्ट बोलें",
    voiceLang: "हिंदी (Hindi)",
    chatPlaceholder: "बोलें या टाइप करें (उदा. 500 रुपये के सेब बेचे... / ऋण के लिए आवेदन करें...)",
    welcomeHeader: (name) => `नमस्ते ${name} जी! मैं आपका व्यापार मित्र AI सहायक हूँ 🙏`,
    welcomeText: "मैं स्ट्रीट वेंडर्स को तुरंत डिजिटल बनाने में मदद करता हूँ: **पीएम स्वनिधि ऋण आवेदन (₹15,000 - 7% ब्याज सब्सिडी)**, दैनिक बिक्री व लाभ का हिसाब, **ONDC Beckn 1.2.0** कैटलॉग और प्रिंटेबल UPI QR स्टैंडी तैयार करना।",
    quickStart: "तुरंत शुरू करें:",
    quickSaleBtn: "नई बिक्री",
    clearChatBtn: "साफ करें",
    tabs: {
      chat: "AI सहायक",
      reports: "📊 बिक्री और हिसाब",
      loan: "🏛️ पीएम स्वनिधि ऋण",
      ondc: "🌐 ONDC कैटलॉग",
      maps: "🍉 APMC मंडी व मैप्स",
      studio: "🎨 क्यूआर और पोस्टर",
      score: "📈 डिजिटल स्कोर",
      store: "🏪 मेरी दुकान"
    },
    chips: [
      { text: "🚀 ऑनबोर्डिंग किट", prompt: "पूरा डिजिटल ऑनबोर्डिंग किट बनाएं", color: "bg-blue-600/90" },
      { text: "🏛️ स्वनिधि ऋण ₹15k", prompt: "पीएम स्वनिधि पहली किश्त ऋण ₹15,000 के लिए आवेदन करें", color: "bg-purple-600/90" },
      { text: "📊 बिक्री रिपोर्ट", prompt: "साप्ताहिक बिक्री और मुनाफा रिपोर्ट दिखाएं", color: "bg-emerald-600/90" },
      { text: "🌐 ONDC कैटलॉग", prompt: "ओएनडीसी (ONDC) डिजिटल स्टोर कैटलॉग बनाएं", color: "bg-sky-600/90" },
      { text: "🗺️ गूगल मैप्स", prompt: "गूगल मैप्स स्थान और लोकल एसईओ दिखाएं", color: "bg-rose-600/90" },
      { text: "💰 लेन-देन दर्ज करें", prompt: "500 रुपये के केले बेचे, 80 रुपये का बर्फ खरीदा", color: "bg-amber-600/90" },
      { text: "📈 डिजिटल स्कोर", prompt: "मेरा डिजिटल स्कोर क्या है?", color: "bg-indigo-600/90" },
      { text: "🍉 पुणे मंडी भाव", prompt: "पुणे APMC फल मंडी के आज के भाव दिखाएं", color: "bg-teal-600/90" },
      { text: "🎨 बैनर प्रिंट", prompt: "स्टॉल मार्केटिंग बैनर और UPI QR स्टैंडी बनाएं", color: "bg-orange-600/90" },
      { text: "💬 व्हाट्सएप संदेश", prompt: "व्हाट्सएप प्रचार संदेश तैयार करें", color: "bg-green-600/90" }
    ],
    periods: { daily: "दैनिक", weekly: "साप्ताहिक", monthly: "मासिक", yearly: "वार्षिक" },
    kpi: { rev: "कुल बिक्री", exp: "कुल खर्च", pro: "शुद्ध लाभ", mar: "मार्जिन" }
  },
  english: {
    agentTitle: "Vyapar Mitra Assistant",
    agentSub: "Personalized for: ",
    voiceListening: "Listening in English... Please speak clearly now",
    voiceLang: "English (Indian)",
    chatPlaceholder: "Speak or type (e.g. Sold ₹600 mangoes, spent ₹100 ice / Apply loan...)",
    welcomeHeader: (name) => `Namaste ${name}! I am your Vyapar Mitra AI 🙏`,
    welcomeText: "I help street vendors digitize instantly: generate digital onboarding kits, compute loan applications for **PM SVANidhi (₹15,000 at 7% subsidy)**, track multi-period ledger profits, integrate with **ONDC Beckn 1.2.0**, and create printable high-res UPI QR standees.",
    quickStart: "Quick start:",
    quickSaleBtn: "Quick Sale",
    clearChatBtn: "Clear",
    tabs: {
      chat: "AI Assistant",
      reports: "📊 Sales & Ledger",
      loan: "🏛️ PM SVANidhi Loan",
      ondc: "🌐 ONDC Catalogue",
      maps: "🍉 APMC Mandi & Maps",
      studio: "🎨 QR & Poster Studio",
      score: "📈 Digital Score",
      store: "🏪 My Store"
    },
    chips: [
      { text: "🚀 Onboarding Kit", prompt: "Generate full digital onboarding kit", color: "bg-blue-600/90" },
      { text: "🏛️ PM SVANidhi Loan", prompt: "Apply for PM SVANidhi 1st tranche loan ₹15,000", color: "bg-purple-600/90" },
      { text: "📊 Sales Reports", prompt: "Show weekly sales and financial report", color: "bg-emerald-600/90" },
      { text: "🌐 ONDC Catalogue", prompt: "Generate ONDC store catalogue schema", color: "bg-sky-600/90" },
      { text: "🗺️ Maps & Local SEO", prompt: "Show Google Maps location and local SEO", color: "bg-rose-600/90" },
      { text: "💰 Log Transactions", prompt: "Sold 500 rupees of bananas, spent 80 on ice", color: "bg-amber-600/90" },
      { text: "📈 Digital Score", prompt: "What is my digital readiness score?", color: "bg-indigo-600/90" },
      { text: "🍉 Mandi Rates", prompt: "Show Pune APMC fruit mandi rates and peak selling times", color: "bg-teal-600/90" },
      { text: "🎨 Print Banner & QR", prompt: "Generate printable stall marketing banner and UPI QR standee", color: "bg-orange-600/90" },
      { text: "💬 WhatsApp Message", prompt: "Format WhatsApp broadcast promotional message", color: "bg-green-600/90" }
    ],
    periods: { daily: "Daily", weekly: "Weekly", monthly: "Monthly", yearly: "Yearly" },
    kpi: { rev: "Revenue", exp: "Expenses", pro: "Net Profit", mar: "Margin" }
  }
};

// Toast Notification System
function showToast(message, icon = "check-circle") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = "toast-item";
  toast.innerHTML = `<i data-lucide="${icon}" class="w-4 h-4 text-emerald-400 shrink-0"></i><span>${message}</span>`;
  container.appendChild(toast);
  safeCreateIcons();

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px) scale(0.95)";
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

function safeCreateIcons() {
  if (window.lucide && typeof window.lucide.createIcons === 'function') {
    try {
      window.lucide.createIcons();
    } catch (e) {
      console.warn("Lucide warning:", e);
    }
  }
}

// Apply Language to the entire UI dynamically
function applyLanguage(lang) {
  const dict = I18N[lang] || I18N.marathi;
  
  // 1. Update Title & Header
  const titleEl = document.getElementById("chat-agent-title");
  if (titleEl) titleEl.textContent = dict.agentTitle;

  const chatStoreName = document.getElementById("chat-store-name");
  if (chatStoreName) chatStoreName.textContent = vendorProfile.store_name;

  // 2. Update Input Placeholder & Voice Label
  const inputEl = document.getElementById("chat-input");
  if (inputEl) inputEl.placeholder = dict.chatPlaceholder;

  const voiceLangLabel = document.getElementById("voice-lang-label");
  if (voiceLangLabel) voiceLangLabel.textContent = dict.voiceLang;

  // 3. Update Tabs
  const tabKeys = ['chat', 'reports', 'loan', 'ondc', 'maps', 'studio', 'score', 'store'];
  const tabIcons = {
    chat: 'bot', reports: 'bar-chart-3', loan: 'file-check-2', ondc: 'shopping-bag',
    maps: 'map-pin', studio: 'qr-code', score: 'award', store: 'user-cog'
  };
  tabKeys.forEach(t => {
    const btn = document.getElementById(`tab-btn-${t}`);
    if (btn && dict.tabs[t]) {
      const span = btn.querySelector("span");
      if (span) span.textContent = dict.tabs[t];
    }
  });

  // 4. Update Action Chips Container
  const chipsDock = document.getElementById("action-chips-dock");
  if (chipsDock && dict.chips) {
    chipsDock.innerHTML = dict.chips.map(c => `
      <button onclick="sendQuickPrompt('${c.prompt.replace(/'/g, "\\'")}')" class="chip-btn px-2.5 py-1 rounded-lg ${c.color} hover:opacity-90 text-white font-semibold whitespace-nowrap transition-all border border-white/20 flex items-center gap-1 shadow-2xs">
        ${c.text}
      </button>
    `).join('');
  }

  // 5. Update Report Period Buttons
  if (dict.periods) {
    const pKeys = ['daily', 'weekly', 'monthly', 'yearly'];
    pKeys.forEach(p => {
      const pBtn = document.getElementById(`btn-period-${p}`);
      if (pBtn && dict.periods[p]) {
        pBtn.textContent = dict.periods[p];
      }
    });
  }

  // 6. Update Initial Welcome Message in Chat
  const welcomeHeader = document.getElementById("agent-welcome-header");
  if (welcomeHeader) welcomeHeader.textContent = dict.welcomeHeader(vendorProfile.owner_name);

  const welcomeText = document.getElementById("agent-welcome-text");
  if (welcomeText) welcomeText.innerHTML = dict.welcomeText;

  safeCreateIcons();
}

// Live Health Check
async function checkConnectionHealth() {
  const badge = document.getElementById("conn-status-badge");
  const txt = document.getElementById("conn-status-text");
  try {
    const res = await fetch(`${API_BASE}/api/health`, { method: "GET" });
    if (res.ok) {
      if (badge) badge.className = "flex items-center gap-2 bg-emerald-50/90 hover:bg-emerald-100 text-emerald-700 px-3.5 py-1.5 rounded-xl border border-emerald-200 text-xs font-bold transition-all shadow-2xs";
      if (txt) txt.textContent = currentLang === 'marathi' ? "AI इंजिन ऑनलाइन" : (currentLang === 'hindi' ? "AI इंजन ऑनलाइन" : "AI Engine Online");
      return true;
    }
  } catch (e) {
    console.warn("Health check error:", e);
  }
  if (badge) badge.className = "flex items-center gap-2 bg-rose-50/90 hover:bg-rose-100 text-rose-700 px-3.5 py-1.5 rounded-xl border border-rose-200 text-xs font-bold transition-all shadow-2xs";
  if (txt) txt.textContent = currentLang === 'marathi' ? "ऑफलाइन - पुन्हा प्रयत्न करा" : (currentLang === 'hindi' ? "ऑफलाइन - पुनः प्रयास करें" : "Offline - Click to Retry");
  return false;
}

// Multi-Period Sales Reports & High-Res Chart.js
async function loadSalesReport(period = "daily") {
  currentPeriod = period;
  ['daily', 'weekly', 'monthly', 'yearly'].forEach(p => {
    const btn = document.getElementById(`btn-period-${p}`);
    if (btn) {
      if (p === period) {
        btn.className = "period-tab-btn flex-1 py-1 rounded-lg bg-white text-emerald-700 shadow-xs font-bold transition-all";
      } else {
        btn.className = "period-tab-btn flex-1 py-1 rounded-lg text-slate-600 hover:text-slate-900 transition-all font-semibold";
      }
    }
  });

  try {
    const res = await fetch(`${API_BASE}/api/reports/sales?period=${period}&session_id=${sessionId}`);
    if (res.ok) {
      const data = await res.json();
      const incEl = document.getElementById("rep-income");
      const expEl = document.getElementById("rep-expense");
      const proEl = document.getElementById("rep-profit");
      const marEl = document.getElementById("rep-margin");

      if (incEl) incEl.textContent = "₹" + data.total_income;
      if (expEl) expEl.textContent = "₹" + data.total_expense;
      if (proEl) proEl.textContent = "₹" + data.net_profit;
      if (marEl) marEl.textContent = (data.profit_margin_pct || 0) + "%";

      renderSalesChart(data.chart_labels, data.chart_income, data.chart_expense, period);
    }
  } catch (e) {
    console.error("Sales report error:", e);
  }
}

function renderSalesChart(labels, incomeData, expenseData, period) {
  const ctx = document.getElementById("salesChart");
  if (!ctx) return;

  if (salesChartInstance) {
    salesChartInstance.destroy();
  }

  // Create subtle modern gradient fills
  const chartCtx = ctx.getContext('2d');
  const gradientInc = chartCtx.createLinearGradient(0, 0, 0, 160);
  gradientInc.addColorStop(0, 'rgba(16, 185, 129, 0.9)');
  gradientInc.addColorStop(1, 'rgba(5, 150, 105, 0.4)');

  const gradientExp = chartCtx.createLinearGradient(0, 0, 0, 160);
  gradientExp.addColorStop(0, 'rgba(244, 63, 94, 0.9)');
  gradientExp.addColorStop(1, 'rgba(225, 29, 72, 0.4)');

  const revLabel = currentLang === 'marathi' ? 'महसूल (₹)' : (currentLang === 'hindi' ? 'बिक्री आय (₹)' : 'Revenue (₹)');
  const expLabel = currentLang === 'marathi' ? 'खर्च (₹)' : (currentLang === 'hindi' ? 'खर्च (₹)' : 'Expenses (₹)');

  salesChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: revLabel,
          data: incomeData,
          backgroundColor: gradientInc,
          borderColor: '#10b981',
          borderWidth: 1.5,
          borderRadius: 8,
          barThickness: period === 'weekly' ? 14 : (period === 'daily' ? 24 : 18)
        },
        {
          label: expLabel,
          data: expenseData,
          backgroundColor: gradientExp,
          borderColor: '#f43f5e',
          borderWidth: 1.5,
          borderRadius: 8,
          barThickness: period === 'weekly' ? 14 : (period === 'daily' ? 24 : 18)
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          labels: { 
            boxWidth: 10, 
            boxHeight: 10,
            usePointStyle: true,
            font: { size: 11, family: 'Plus Jakarta Sans', weight: '600' },
            color: '#334155'
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          titleFont: { size: 12, family: 'Plus Jakarta Sans', weight: '700' },
          bodyFont: { size: 11, family: 'JetBrains Mono' },
          padding: 10,
          cornerRadius: 10,
          displayColors: true,
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ₹${context.raw.toLocaleString('en-IN')}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(226, 232, 240, 0.7)',
          },
          ticks: { 
            font: { size: 10, family: 'JetBrains Mono' },
            color: '#64748b',
            callback: (v) => '₹' + v
          }
        },
        x: {
          grid: { display: false },
          ticks: { 
            font: { size: 10, family: 'Plus Jakarta Sans', weight: '600' },
            color: '#475569'
          }
        }
      }
    }
  });
}

function downloadSalesCSV() {
  window.location.href = `${API_BASE}/api/reports/export?period=${currentPeriod}&session_id=${sessionId}`;
  showToast(currentLang === 'marathi' ? "विक्री अहवाल CSV डाउनलोड होत आहे..." : (currentLang === 'hindi' ? "बिक्री रिपोर्ट CSV डाउनलोड हो रही है..." : "Downloading sales report CSV..."), "download");
}

// Cash Flow Statement Modal
async function fetchAndShowStatement() {
  try {
    const res = await fetch(`${API_BASE}/api/ledger/statement?session_id=${sessionId}&vendor_name=${encodeURIComponent(vendorProfile.store_name)}`);
    if (res.ok) {
      const data = await res.json();
      const body = document.getElementById("statement-modal-body");
      if (body) {
        body.innerHTML = `
          <div class="bg-white p-4 rounded-2xl border border-slate-200 space-y-2 shadow-2xs">
            <div class="border-b border-slate-200 pb-2 flex justify-between items-center">
              <span class="font-extrabold text-slate-900 text-sm">🏛️ ${data.statement_title}</span>
              <span class="text-[10px] text-slate-500">${data.generated_at}</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <p><strong>Total Revenue:</strong> <span class="text-emerald-700 font-bold">₹${data.total_revenue}</span></p>
              <p><strong>Total Operating Expenses:</strong> <span class="text-rose-700 font-bold">₹${data.total_operating_expenses}</span></p>
              <p><strong>Net Operating Profit:</strong> <span class="text-blue-700 font-bold">₹${data.net_operating_profit}</span></p>
              <p><strong>Operating Margin:</strong> <span class="text-purple-700 font-bold">${data.operating_margin}</span></p>
            </div>
            <div class="p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 font-sans text-xs">
              <strong>Credit Readiness Evaluation:</strong> ${data.loan_readiness_indicator}
              <div class="mt-1 font-bold text-emerald-900">Recommended Loan: ${data.recommended_first_tranche}</div>
            </div>
          </div>
          <div class="bg-white p-3 rounded-2xl border border-slate-200">
            <span class="font-bold text-slate-800 block mb-1">Recent Audit Records (${data.record_count} Entries):</span>
            <div class="space-y-1 max-h-48 overflow-y-auto custom-scrollbar text-[11px]">
              ${data.transactions.slice(-6).reverse().map(t => `
                <div class="flex items-center justify-between p-1.5 rounded-lg bg-slate-50 border border-slate-100">
                  <span>${t.timestamp.substring(5, 16)} • ${t.description}</span>
                  <strong class="${t.type === 'income' ? 'text-emerald-700' : 'text-rose-700'}">${t.type === 'income' ? '+' : '-'}₹${t.amount}</strong>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }
      const modal = document.getElementById("statement-modal");
      if (modal) modal.classList.remove("hidden");
    }
  } catch (e) {
    console.error(e);
  }
}

function closeStatementModal() {
  const modal = document.getElementById("statement-modal");
  if (modal) modal.classList.add("hidden");
}

// Quick Add Transaction Modal
function openAddTxModal() {
  const modal = document.getElementById("tx-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeAddTxModal() {
  const modal = document.getElementById("tx-modal");
  if (modal) modal.classList.add("hidden");
}

async function submitManualTx(e) {
  if (e && e.preventDefault) e.preventDefault();
  const typeEls = document.getElementsByName("tx_type");
  let txType = "income";
  for (const el of typeEls) {
    if (el.checked) {
      txType = el.value;
      break;
    }
  }
  const amount = parseFloat(document.getElementById("manual-tx-amount").value);
  const desc = document.getElementById("manual-tx-desc").value.trim();
  const cat = document.getElementById("manual-tx-cat").value;

  if (!amount || isNaN(amount)) return;

  const phrase = txType === 'income' ? `Sold ${desc} for ${amount} rupees` : `Spent ${amount} rupees on ${desc}`;

  try {
    const res = await fetch(`${API_BASE}/api/ledger/transaction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: phrase, session_id: sessionId, language: currentLang })
    });
    if (res.ok) {
      closeAddTxModal();
      loadSalesReport(currentPeriod);
      showToast(`Logged ₹${amount} ${txType === 'income' ? 'Revenue' : 'Expense'}!`, "check");
      appendAgentSimpleMessage(
        currentLang === 'marathi'
          ? `✅ <strong>व्यवहार नोंदवला:</strong> ${txType === 'income' ? 'विक्री' : 'खर्च'} ₹${amount} (<em>${desc}</em> - ${cat}). दैनंदिन अहवाल अद्ययावत केला!`
          : (currentLang === 'hindi'
            ? `✅ <strong>लेन-देन दर्ज:</strong> ${txType === 'income' ? 'बिक्री' : 'खर्च'} ₹${amount} (<em>${desc}</em> - ${cat}). रिपोर्ट अपडेट की गई!`
            : `✅ <strong>Transaction Logged:</strong> ${txType === 'income' ? 'Received' : 'Paid'} ₹${amount} for <em>${desc}</em> (${cat}). Live reports updated!`)
      );
    }
  } catch (err) {
    console.error(err);
  }
}

// PM SVANidhi Application Kit Generator
async function generateLoanApplicationKit() {
  const vendorName = document.getElementById("loan-vendor-name").value.trim() || vendorProfile.owner_name;
  const mobile = document.getElementById("loan-mobile").value.trim() || vendorProfile.phone;
  const tvcStatus = document.getElementById("loan-tvc-status").value;
  const ifsc = document.getElementById("loan-ifsc").value.trim() || "SBIN0001234";

  try {
    const res = await fetch(`${API_BASE}/api/schemes/apply-pmsvanidhi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        vendor_name: vendorName,
        mobile: mobile,
        store_name: vendorProfile.store_name,
        location: vendorProfile.location,
        tvc_recommendation_status: tvcStatus,
        ifsc: ifsc,
        loan_tranche: 1
      })
    });

    if (res.ok) {
      const data = await res.json();
      renderLoanApplicationInChat(data);
      const chkScheme = document.getElementById("chk-scheme");
      if (chkScheme) chkScheme.checked = true;
      updateSignals();
      showToast(currentLang === 'marathi' ? "पीएम स्वनिधी कर्ज किट तयार!" : (currentLang === 'hindi' ? "पीएम स्वनिधि ऋण किट तैयार!" : "PM SVANidhi Loan Kit Generated!"), "award");
    }
  } catch (e) {
    console.error(e);
  }
}

function renderLoanApplicationInChat(app) {
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  div.className = "flex items-start gap-3";
  div.innerHTML = `
    <div class="w-9 h-9 rounded-xl bg-purple-600 flex items-center justify-center text-white shrink-0 text-xs font-black shadow-md shadow-purple-500/20">
      PM
    </div>
    <div class="bg-purple-50/90 text-purple-950 rounded-2xl rounded-tl-none p-4 max-w-[90%] border border-purple-200/80 shadow-premium text-xs space-y-3">
      <div class="flex items-center justify-between pb-2 border-b border-purple-200">
        <span class="font-extrabold text-sm text-purple-900">🏛️ PM SVANidhi 1st Tranche Loan Application Kit</span>
        <span class="font-black bg-purple-200/90 text-purple-950 px-2.5 py-0.5 rounded-md text-[11px]">${app.requested_amount} (7% Subsidy)</span>
      </div>
      
      <div class="bg-white p-3 rounded-xl border border-purple-100 space-y-1 text-slate-800 shadow-2xs">
        <p><strong>Applicant:</strong> ${app.applicant_profile.applicant_name} (${app.applicant_profile.business_name})</p>
        <p><strong>ULB / Municipal Corp:</strong> ${app.applicant_profile.urban_local_body}</p>
        <p><strong>Vending Status:</strong> ${app.applicant_profile.vending_status}</p>
        <p><strong>Disbursement Bank IFSC:</strong> <code class="font-mono bg-slate-100 px-1.5 py-0.5 rounded">${app.applicant_profile.disbursement_bank.ifsc_code}</code></p>
      </div>

      <div>
        <span class="font-bold text-purple-900 block mb-1">Required Documents Checklist:</span>
        <ul class="list-disc list-inside space-y-0.5 text-purple-900">
          ${app.required_documents_checklist.map(d => `<li>${d.doc} (${d.status})</li>`).join('')}
        </ul>
      </div>

      <div class="flex items-center gap-2 pt-1 flex-wrap">
        <a href="https://pmsvanidhi.mohua.gov.in/" target="_blank" class="px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white font-extrabold rounded-xl transition-all shadow-xs flex items-center gap-1">
          🚀 Open Official Portal <i data-lucide="external-link" class="w-3 h-3"></i>
        </a>
        <button onclick="window.print()" class="px-3 py-1.5 bg-white border border-purple-300 text-purple-900 font-bold rounded-xl hover:bg-purple-100 shadow-2xs">
          🖨️ Print Loan Kit
        </button>
      </div>
    </div>
  `;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
  safeCreateIcons();
}

// ONDC Catalogue JSON Download
async function downloadONDCJson() {
  try {
    const res = await fetch(`${API_BASE}/api/ondc/catalogue?session_id=${sessionId}`);
    if (res.ok) {
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ondc_beckn_catalogue_${vendorProfile.store_name.toLowerCase().replace(/\s+/g, '_')}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      const chkOndc = document.getElementById("chk-ondc");
      if (chkOndc) chkOndc.checked = true;
      updateSignals();
      showToast(currentLang === 'marathi' ? "ONDC बेकन कॅटलॉग JSON डाउनलोड झाले!" : (currentLang === 'hindi' ? "ONDC बेकन कैटलॉग JSON डाउनलोड हुआ!" : "ONDC Beckn JSON Catalogue Downloaded!"), "shopping-bag");
    }
  } catch (e) {
    console.error(e);
  }
}

// Store Profile Management
async function loadStoreProfile() {
  const saved = localStorage.getItem("vm_vendor_profile");
  if (saved) {
    try {
      vendorProfile = Object.assign(vendorProfile, JSON.parse(saved));
    } catch (e) {}
  }

  try {
    const res = await fetch(`${API_BASE}/api/vendor/profile?session_id=${sessionId}`);
    if (res.ok) {
      const data = await res.json();
      vendorProfile = Object.assign(vendorProfile, data);
    }
  } catch (e) {
    console.warn("Could not fetch remote profile, using local fallback.", e);
  }

  updateProfileUIElements();
}

function updateProfileUIElements() {
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el && val !== undefined) el.value = val;
  };
  setVal("loan-vendor-name", vendorProfile.owner_name);
  setVal("loan-mobile", vendorProfile.phone);
  setVal("prof-store-name", vendorProfile.store_name);
  setVal("prof-owner-name", vendorProfile.owner_name);
  setVal("prof-upi-id", vendorProfile.upi_id);
  setVal("prof-phone", vendorProfile.phone);
  setVal("prof-location", vendorProfile.location);
  setVal("prof-hours", vendorProfile.operating_hours);
  setVal("prof-goal", vendorProfile.daily_profit_goal);

  const storeNameEl = document.getElementById("chat-store-name");
  if (storeNameEl) storeNameEl.textContent = vendorProfile.store_name || "Camp Fresh Fruits";
  
  const headerSub = document.getElementById("header-store-sub");
  if (headerSub) {
    headerSub.innerHTML = `<i data-lucide="map-pin" class="w-3 h-3 text-rose-500 inline"></i> <span>${vendorProfile.store_name} • ${vendorProfile.owner_name} • ${vendorProfile.location}</span>`;
  }

  const ondcTitle = document.getElementById("ondc-store-title");
  if (ondcTitle) ondcTitle.textContent = `${vendorProfile.store_name} - ONDC Node`;

  const ondcLoc = document.getElementById("ondc-store-loc");
  if (ondcLoc) ondcLoc.textContent = `Location: ${vendorProfile.location} • Settlement: ${vendorProfile.upi_id}`;

  applyLanguage(currentLang);
  safeCreateIcons();
}

async function saveStoreProfile() {
  vendorProfile.store_name = document.getElementById("prof-store-name").value.trim() || vendorProfile.store_name;
  vendorProfile.owner_name = document.getElementById("prof-owner-name").value.trim() || vendorProfile.owner_name;
  vendorProfile.upi_id = document.getElementById("prof-upi-id").value.trim() || vendorProfile.upi_id;
  vendorProfile.phone = document.getElementById("prof-phone").value.trim() || vendorProfile.phone;
  vendorProfile.location = document.getElementById("prof-location").value.trim() || vendorProfile.location;
  vendorProfile.operating_hours = document.getElementById("prof-hours").value.trim() || vendorProfile.operating_hours;
  vendorProfile.daily_profit_goal = parseFloat(document.getElementById("prof-goal").value) || vendorProfile.daily_profit_goal;

  localStorage.setItem("vm_vendor_profile", JSON.stringify(vendorProfile));

  try {
    await fetch(`${API_BASE}/api/vendor/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        store_name: vendorProfile.store_name,
        owner_name: vendorProfile.owner_name,
        upi_id: vendorProfile.upi_id,
        phone: vendorProfile.phone,
        location: vendorProfile.location,
        operating_hours: vendorProfile.operating_hours,
        daily_profit_goal: vendorProfile.daily_profit_goal
      })
    });
  } catch (e) {
    console.warn("Could not save profile to API:", e);
  }

  updateProfileUIElements();
  showToast(currentLang === 'marathi' ? "दुकानाची माहिती सेव्ह झाली!" : (currentLang === 'hindi' ? "दुकान की जानकारी सुरक्षित हुई!" : "Store profile saved successfully!"), "check");
}

function openProfileModal() {
  switchTab('store');
}

// Tab Navigation Switching
function switchTab(tabId) {
  const tabs = ['chat', 'reports', 'loan', 'ondc', 'maps', 'studio', 'score', 'store'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab-btn-${t}`);
    if (btn) {
      if (t === tabId) {
        btn.className = "mode-tab-btn active px-3.5 py-2 rounded-xl flex items-center gap-2 bg-blue-600 text-white shadow-md shadow-blue-500/20 font-bold";
      } else {
        btn.className = "mode-tab-btn px-3.5 py-2 rounded-xl flex items-center gap-2 bg-white text-slate-700 hover:bg-slate-100/90 border border-slate-200/80 shadow-2xs font-semibold";
      }
    }
  });

  if (tabId === 'reports') {
    const repView = document.getElementById("view-reports");
    if (repView) repView.scrollIntoView({ behavior: "smooth" });
    loadSalesReport(currentPeriod);
  } else if (tabId === 'loan') {
    const loanView = document.getElementById("view-loan-app");
    if (loanView) loanView.scrollIntoView({ behavior: "smooth" });
  } else if (tabId === 'ondc') {
    const ondcView = document.getElementById("view-ondc-store");
    if (ondcView) ondcView.scrollIntoView({ behavior: "smooth" });
  } else if (tabId === 'maps') {
    const mapsView = document.getElementById("view-google-maps");
    if (mapsView) mapsView.scrollIntoView({ behavior: "smooth" });
  } else if (tabId === 'score') {
    const scoreView = document.getElementById("view-score");
    if (scoreView) scoreView.scrollIntoView({ behavior: "smooth" });
    updateSignals();
  } else if (tabId === 'store') {
    const storeView = document.getElementById("view-store");
    if (storeView) storeView.scrollIntoView({ behavior: "smooth" });
  } else if (tabId === 'studio') {
    if (activePosterSvg) {
      openPosterModal();
    } else {
      generateFreshPoster();
    }
  }
}

// Poster & QR Code Standee Generator
async function generateFreshPoster() {
  try {
    const res = await fetch(`${API_BASE}/api/poster/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stall_name: vendorProfile.store_name,
        tagline: `100% Farm-Fresh Daily • ${vendorProfile.owner_name}`,
        location: vendorProfile.location,
        operating_hours: vendorProfile.operating_hours,
        upi_id: vendorProfile.upi_id,
        language: currentLang
      })
    });
    if (res.ok) {
      const data = await res.json();
      activePosterSvg = data.svg;
      openPosterModal();
      showToast(currentLang === 'marathi' ? "छापील बॅनर तयार झाले!" : (currentLang === 'hindi' ? "प्रिंट बैनर तैयार हुआ!" : "Printable stall banner rendered!"), "printer");
    }
  } catch (e) {
    console.error(e);
  }
}

function openPosterModal() {
  const container = document.getElementById("poster-svg-container");
  if (activePosterSvg && container) {
    container.innerHTML = activePosterSvg;
  }
  const modal = document.getElementById("poster-modal");
  if (modal) modal.classList.remove("hidden");
  safeCreateIcons();
}

function closePosterModal() {
  const modal = document.getElementById("poster-modal");
  if (modal) modal.classList.add("hidden");
}

function printPosterSVG() {
  window.print();
}

// Voice Recognition (Speech-to-Text)
function initVoice() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    setVoiceLanguage();

    recognition.onstart = () => {
      isRecording = true;
      const btn = document.getElementById("mic-btn");
      if (btn) {
        btn.classList.add("bg-red-500", "text-white", "recording-pulse");
        btn.classList.remove("bg-slate-100", "text-slate-700");
      }
      const pulse = document.getElementById("mic-pulse");
      if (pulse) pulse.classList.remove("hidden");
      const status = document.getElementById("voice-status");
      if (status) status.classList.remove("hidden");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      document.getElementById("chat-input").value = transcript;
      handleChatSubmit(new Event('submit'));
    };

    recognition.onerror = (event) => {
      console.warn("Voice error:", event.error);
      stopVoice();
    };

    recognition.onend = () => {
      stopVoice();
    };
  }
}

function setVoiceLanguage() {
  if (!recognition) return;
  const label = document.getElementById("voice-lang-label");
  if (currentLang === "marathi") {
    recognition.lang = "mr-IN";
    if (label) label.textContent = "मराठी (Marathi)";
  } else if (currentLang === "hindi") {
    recognition.lang = "hi-IN";
    if (label) label.textContent = "हिंदी (Hindi)";
  } else {
    recognition.lang = "en-IN";
    if (label) label.textContent = "English (Indian)";
  }
}

function toggleVoiceRecording() {
  if (!recognition) {
    initVoice();
  }
  if (!recognition) {
    alert("Voice input is supported in Chrome, Edge, and Android browsers. You can also type directly in any language!");
    return;
  }
  if (isRecording) {
    recognition.stop();
  } else {
    try {
      setVoiceLanguage();
      recognition.start();
    } catch (e) {
      console.error(e);
    }
  }
}

function stopVoice() {
  isRecording = false;
  const btn = document.getElementById("mic-btn");
  if (btn) {
    btn.classList.remove("bg-red-500", "text-white", "recording-pulse");
    btn.classList.add("bg-slate-100", "text-slate-700");
  }
  const pulse = document.getElementById("mic-pulse");
  if (pulse) pulse.classList.add("hidden");
  const status = document.getElementById("voice-status");
  if (status) status.classList.add("hidden");
}

function setLanguage(lang) {
  currentLang = lang;
  ['mr', 'hi', 'en'].forEach(l => {
    const btn = document.getElementById(`lang-${l}`);
    if (btn) {
      if (l === (lang === 'marathi' ? 'mr' : lang === 'hindi' ? 'hi' : 'en')) {
        btn.className = "px-2.5 py-1 rounded-lg transition-all bg-white text-blue-700 shadow-xs font-bold";
      } else {
        btn.className = "px-2.5 py-1 rounded-lg transition-all text-slate-600 hover:text-slate-900 font-semibold";
      }
    }
  });
  setVoiceLanguage();
  applyLanguage(lang);
  loadSalesReport(currentPeriod);
  checkConnectionHealth();
  updateSignals();
  showToast(lang === 'marathi' ? "भाषा: मराठी निवडली" : (lang === 'hindi' ? "भाषा: हिंदी चुनी गई" : "Language set to ENGLISH"), "globe");
}

function sendQuickPrompt(promptText) {
  const inputEl = document.getElementById("chat-input");
  if (inputEl) {
    inputEl.value = promptText;
    handleChatSubmit(new Event('submit'));
  }
}

function clearChat() {
  const stream = document.getElementById("chat-stream");
  const dict = I18N[currentLang] || I18N.marathi;
  if (stream) {
    stream.innerHTML = `
      <div class="flex items-start gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shrink-0 text-xs font-black shadow-md shadow-blue-500/20">
          VM
        </div>
        <div class="bg-slate-100/90 text-slate-800 rounded-2xl rounded-tl-none p-4 max-w-[88%] text-sm leading-relaxed border border-slate-200/70 shadow-xs">
          <p class="font-extrabold text-slate-900 mb-1">${dict.welcomeHeader(vendorProfile.owner_name)}</p>
          <p class="text-xs text-blue-700">${dict.welcomeText}</p>
        </div>
      </div>
    `;
  }
}

// Chat API Submissions
async function handleChatSubmit(e) {
  if (e && e.preventDefault) e.preventDefault();
  const inputEl = document.getElementById("chat-input");
  const msg = inputEl.value.trim();
  if (!msg) return;

  // Append User Message Bubble
  appendUserMessage(msg);
  inputEl.value = "";

  // Append Thinking Indicator
  const thinkingId = appendThinkingBubble();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        session_id: sessionId,
        language: currentLang,
        signals: signals
      })
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data = await res.json();
    removeThinkingBubble(thinkingId);
    renderAgentResponse(data);
    loadSalesReport(currentPeriod); // Auto-refresh reports
  } catch (err) {
    removeThinkingBubble(thinkingId);
    console.error("Chat API Error:", err);
    appendAgentSimpleMessage(`⚠️ <strong>Connection Notice:</strong> Unable to connect to backend at <code>${API_BASE || window.location.origin}</code>.<br>Please ensure the server is running by typing <code>python run.py</code> in the terminal. <br><button onclick="checkConnectionHealth()" class="mt-2 px-3 py-1 bg-blue-600 text-white rounded-lg text-xs font-semibold">Retry Connection</button>`);
  }
}

function appendUserMessage(text) {
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  div.className = "flex items-start gap-3 justify-end";
  div.innerHTML = `
    <div class="bg-gradient-to-r from-blue-700 to-indigo-600 text-white rounded-2xl rounded-tr-none p-3.5 max-w-[85%] text-sm leading-relaxed shadow-md shadow-blue-600/15">
      ${escapeHtml(text)}
    </div>
    <div class="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white shrink-0 text-xs font-bold shadow-xs">
      You
    </div>
  `;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
}

function appendThinkingBubble() {
  const id = "think-" + Date.now();
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  div.id = id;
  div.className = "flex items-start gap-3";
  div.innerHTML = `
    <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shrink-0 text-xs font-black">
      VM
    </div>
    <div class="bg-slate-100 text-slate-600 rounded-2xl rounded-tl-none p-3.5 text-xs flex items-center gap-2 border border-slate-200/60 shadow-xs">
      <span class="w-2 h-2 rounded-full bg-blue-600 animate-bounce"></span>
      <span class="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style="animation-delay: 0.2s"></span>
      <span class="w-2 h-2 rounded-full bg-blue-600 animate-bounce" style="animation-delay: 0.4s"></span>
      <span class="ml-1 font-semibold">${currentLang === 'marathi' ? 'व्यापार मित्र प्रक्रिया करत आहे...' : (currentLang === 'hindi' ? 'व्यापार मित्र प्रोसेस कर रहा है...' : 'Vyapar Mitra is processing...')}</span>
    </div>
  `;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
  return id;
}

function removeThinkingBubble(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function appendAgentSimpleMessage(text) {
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  div.className = "flex items-start gap-3";
  div.innerHTML = `
    <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shrink-0 text-xs font-black shadow-md shadow-blue-500/20">
      VM
    </div>
    <div class="bg-slate-100/90 text-slate-800 rounded-2xl rounded-tl-none p-4 max-w-[88%] text-sm leading-relaxed border border-slate-200/70 shadow-xs">
      ${text}
    </div>
  `;
  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
  safeCreateIcons();
}

// Render Structured Agent Responses
function renderAgentResponse(data) {
  const stream = document.getElementById("chat-stream");
  const div = document.createElement("div");
  div.className = "flex items-start gap-3";

  let bodyHtml = "";

  if (data.mode === 1) {
    const prof = data.business_profile;
    const promo = data.promotional_material;
    activePosterSvg = promo.poster_svg;

    bodyHtml = `
      <div class="space-y-3 text-xs">
        <div class="flex items-center justify-between pb-2 border-b border-slate-200">
          <span class="font-extrabold uppercase tracking-wider text-blue-700 bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-200">
            🚀 Digital Onboarding Kit
          </span>
          <span class="text-slate-500 font-semibold">${prof.owner_name || 'Vendor'} • ONDC Ready</span>
        </div>

        <div class="bg-white p-3.5 rounded-2xl border border-slate-200 shadow-2xs">
          <h4 class="text-sm font-extrabold text-slate-900 mb-0.5">🏪 ${prof.suggested_name}</h4>
          <p class="text-blue-600 font-bold mb-1">${prof.tagline}</p>
          <p class="text-slate-600 leading-relaxed">${prof.description}</p>
        </div>

        <div class="bg-amber-50/80 p-3 rounded-2xl border border-amber-200 shadow-2xs">
          <h5 class="font-bold text-amber-950 mb-1 flex items-center gap-1"><i data-lucide="lightbulb" class="w-3.5 h-3.5 text-amber-600"></i> Hyperlocal Mandi Pricing Tips</h5>
          <ul class="space-y-1 text-amber-900 list-disc list-inside">
            ${data.pricing_tips.map(t => `<li>${t}</li>`).join('')}
          </ul>
        </div>

        <div class="bg-purple-50/80 p-3 rounded-2xl border border-purple-200 shadow-2xs">
          <h5 class="font-bold text-purple-950 mb-1 flex items-center gap-1"><i data-lucide="award" class="w-3.5 h-3.5 text-purple-600"></i> PM SVANidhi Match (₹15,000 Loan)</h5>
          <p class="text-purple-900 mb-1">7% interest subsidy & digital transaction cashback up to ₹1,200/yr.</p>
          <p class="font-bold text-purple-950 text-[11px]">⚠️ ${data.scheme_disclaimer}</p>
        </div>

        <div class="bg-blue-50/80 p-3 rounded-2xl border border-blue-200 shadow-2xs">
          <h5 class="font-bold text-blue-950 mb-1 flex items-center gap-1"><i data-lucide="message-square" class="w-3.5 h-3.5 text-blue-600"></i> Localized Stall Broadcast (${promo.language.toUpperCase()})</h5>
          <p class="bg-white p-2.5 rounded-xl border border-blue-100 text-blue-950 italic mb-2.5" id="promo-text-holder">${escapeHtml(promo.local_translation)}</p>
          <div class="flex items-center gap-2">
            <button onclick="openPosterModal()" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold shadow-xs transition-all flex items-center gap-1">
              🎨 Print Stall Banner
            </button>
            <button onclick="copyElementText('promo-text-holder')" class="px-3 py-1.5 bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 rounded-xl font-bold transition-all shadow-2xs">
              📋 Copy Message
            </button>
          </div>
        </div>
      </div>
    `;
  } else if (data.mode === 2) {
    updateScoreUI(data.score, data.badge, data.next_actions);
    bodyHtml = `
      <div class="space-y-2.5 text-xs">
        <div class="flex items-center justify-between pb-2 border-b border-slate-200">
          <span class="font-extrabold uppercase tracking-wider text-purple-700 bg-purple-50 px-2.5 py-1 rounded-lg border border-purple-200">
            📊 Digital Readiness Score
          </span>
          <span class="font-extrabold text-purple-900">${data.score} / ${data.max_score} (${data.badge})</span>
        </div>
        <p class="text-slate-800 leading-relaxed">${data.reply_text}</p>
        <div class="bg-slate-50 p-3 rounded-2xl border border-slate-200 space-y-1">
          <span class="font-bold text-slate-900">Ranked Next Actions:</span>
          ${data.next_actions.map(a => `<p class="text-slate-700">• ${a}</p>`).join('')}
        </div>
      </div>
    `;
  } else if (data.mode === 3) {
    bodyHtml = `
      <div class="space-y-2.5 text-xs">
        <div class="flex items-center justify-between pb-2 border-b border-slate-200">
          <span class="font-extrabold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
            💰 Micro-Ledger Entry
          </span>
          <span class="font-black text-emerald-950">Net Profit: ₹${data.summary.net_profit}</span>
        </div>
        <p class="text-slate-800 font-semibold">${data.confirmation}</p>
        <div class="bg-emerald-50/80 p-3 rounded-2xl border border-emerald-200">
          <span class="font-bold text-emerald-950">Loan Credit Readiness:</span>
          <p class="text-emerald-900">${data.credit_statement.loan_readiness_indicator} (${data.credit_statement.recommended_first_tranche}).</p>
        </div>
      </div>
    `;
  } else if (data.mode === 5) {
    bodyHtml = `
      <div class="space-y-2.5 text-xs">
        <div class="flex items-center justify-between pb-2 border-b border-slate-200">
          <span class="font-extrabold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
            💬 WhatsApp Micro-Card Format
          </span>
          <button onclick="copyElementText('wa-card-body')" class="text-blue-600 font-bold hover:underline">Copy Card</button>
        </div>
        <div id="wa-card-body" class="bg-[#e9fbf0] p-3 rounded-2xl border border-emerald-300 font-mono whitespace-pre-line text-emerald-950 shadow-inner">
${data.whatsapp_text}
        </div>
      </div>
    `;
  } else {
    bodyHtml = `<p class="text-xs text-slate-800 leading-relaxed">${data.reply_text || JSON.stringify(data)}</p>`;
  }

  div.innerHTML = `
    <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shrink-0 text-xs font-black shadow-md shadow-blue-500/20">
      VM
    </div>
    <div class="bg-slate-100/90 text-slate-800 rounded-2xl rounded-tl-none p-4 max-w-[90%] border border-slate-200/70 shadow-xs">
      ${bodyHtml}
    </div>
  `;

  stream.appendChild(div);
  stream.scrollTop = stream.scrollHeight;
  safeCreateIcons();
}

function updateScoreUI(score, badge, nextActions) {
  const scoreNum = document.getElementById("score-num");
  if (scoreNum) scoreNum.textContent = score;
  const badgePill = document.getElementById("badge-pill");
  if (badgePill) badgePill.textContent = badge;
  
  const path = document.getElementById("score-circle-path");
  if (path) path.setAttribute("stroke-dasharray", `${score}, 100`);

  if (nextActions && nextActions.length > 0) {
    const actEl = document.getElementById("score-action-text");
    if (actEl) actEl.textContent = nextActions[0];
  }
}

function updateSignals() {
  const chkUpi = document.getElementById("chk-upi");
  const chkMaps = document.getElementById("chk-maps");
  const chkOndc = document.getElementById("chk-ondc");
  const chkScheme = document.getElementById("chk-scheme");

  if (chkUpi) signals.upi_set_up = chkUpi.checked;
  if (chkMaps) signals.google_maps_listed = chkMaps.checked;
  if (chkOndc) signals.ondc_listed = chkOndc.checked;
  if (chkScheme) signals.scheme_registered = chkScheme.checked;

  fetch(`${API_BASE}/api/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "update score", session_id: sessionId, signals: signals, language: currentLang })
  })
  .then(res => res.json())
  .then(data => {
    updateScoreUI(data.score, data.badge, data.next_actions);
  })
  .catch(console.error);
}

function copyElementText(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const text = el.innerText || el.textContent;
  navigator.clipboard.writeText(text).then(() => {
    showToast(currentLang === 'marathi' ? "मजकूर कॉपी केला!" : (currentLang === 'hindi' ? "टेक्स्ट कॉपी किया गया!" : "Copied text to clipboard!"), "copy");
  }).catch(() => {
    prompt("Copy text:", text);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

document.addEventListener("DOMContentLoaded", () => {
  initVoice();
  loadStoreProfile();
  setLanguage(currentLang);
});