'use strict';

function showLoading(msg) {
  var overlay = document.getElementById('loading-overlay');
  var txt = document.getElementById('spinner-text');
  if (!overlay) return;
  if (txt && msg) txt.textContent = msg;
  overlay.classList.add('show');
}

function hideLoading() {
  var overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.classList.remove('show');
}

function showToast(msg) {
  var toast = document.getElementById('toast');
  var toastMsg = document.getElementById('toast-msg');
  if (!toast) return;
  if (toastMsg) toastMsg.textContent = msg;
  toast.classList.add('show');
  setTimeout(function () { toast.classList.remove('show'); }, 3200);
}

var hamburger = document.getElementById('hamburger');
var mobileMenu = document.getElementById('mobile-menu');

if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', function () {
    mobileMenu.classList.toggle('open');
  });
  document.addEventListener('click', function (e) {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
    }
  });
}

document.querySelectorAll('.alert').forEach(function (alert) {
  setTimeout(function () {
    alert.style.opacity = '0';
    alert.style.transition = 'opacity 0.4s';
    setTimeout(function () { if (alert.parentNode) alert.remove(); }, 400);
  }, 4500);
});

function animateStats() {
  document.querySelectorAll('[data-target]').forEach(function (el) {
    var target = parseInt(el.dataset.target);
    var suffix = el.dataset.suffix !== undefined ? el.dataset.suffix : '+';
    var current = 0;
    var step = target / 60;
    var timer = setInterval(function () {
      current += step;
      if (current >= target) { current = target; clearInterval(timer); }
      el.textContent = Math.floor(current) + suffix;
    }, 16);
  });
}

if (document.querySelector('[data-target]')) {
  animateStats();
}

var fileInput = document.getElementById('file-input');
var uploadTitle = document.getElementById('upload-title');
var uploadZone = document.getElementById('upload-zone');

if (fileInput) {
  fileInput.addEventListener('change', function () {
    if (this.files.length > 0) {
      var name = this.files[0].name;
      var size = (this.files[0].size / 1024).toFixed(0);
      if (uploadTitle) {
        uploadTitle.textContent = name + ' (' + size + 'KB)';
        uploadTitle.style.color = '#1D9E75';
      }
      if (uploadZone) uploadZone.style.borderColor = '#1D9E75';
      showToast('Profile uploaded — ready to match');
    }
  });
}

if (uploadZone) {
  uploadZone.addEventListener('dragover', function (e) {
    e.preventDefault();
    this.classList.add('dragover');
  });
  uploadZone.addEventListener('dragleave', function () {
    this.classList.remove('dragover');
  });
  uploadZone.addEventListener('drop', function (e) {
    e.preventDefault();
    this.classList.remove('dragover');
    var file = e.dataTransfer.files[0];
    if (file) {
      if (uploadTitle) {
        uploadTitle.textContent = file.name + ' uploaded';
        uploadTitle.style.color = '#1D9E75';
      }
      this.style.borderColor = '#1D9E75';
      showToast('Profile uploaded — ready to match');
    }
  });
}

var textarea = document.getElementById('research-text');
var charCount = document.getElementById('char-count');

if (textarea && charCount) {
  textarea.setAttribute('maxlength', '5000');
  textarea.addEventListener('input', function () {
    var len = this.value.length;
    charCount.textContent = len + ' / 5000 characters';
    charCount.style.color = len > 4800 ? '#D85A30' : '#5F5E5A';
  });
}

var sampleGrants = [
  {
    id: 1,
    title: 'Wellcome Trust — AI in Healthcare Research Grant',
    body: 'Wellcome Trust',
    deadline: '30 Jun 2026',
    tags: ['Artificial Intelligence', 'Healthcare', 'Early Career'],
    score: 90,
    type: 'top',
    feedback: 'This grant is highly relevant to your profile. Your expertise in machine learning applied to healthcare aligns directly with the funding call, and your status as an early career researcher meets the eligibility criteria.'
  },
  {
    id: 2,
    title: 'UKRI — Machine Learning for Public Good',
    body: 'UKRI',
    deadline: '15 Jul 2026',
    tags: ['Machine Learning', 'Public Sector', 'NLP'],
    score: 74,
    type: 'top',
    feedback: 'Your background in NLP and machine learning positions you well for this grant. The call targets researchers applying AI to societal challenges, which overlaps with your stated research interests.'
  },
  {
    id: 3,
    title: 'Research England — NLP and Sustainability Fund',
    body: 'Research England',
    deadline: '1 Aug 2026',
    tags: ['NLP', 'Sustainability', 'Data Science'],
    score: 58,
    type: 'mid',
    feedback: null
  },
  {
    id: 4,
    title: 'British Academy — Digital Humanities Small Grant',
    body: 'British Academy',
    deadline: '20 Aug 2026',
    tags: ['Digital', 'Humanities', 'Small Grant'],
    score: 31,
    type: 'alt',
    feedback: null
  },
  {
    id: 5,
    title: 'Leverhulme Trust — Early Career Fellowship',
    body: 'Leverhulme Trust',
    deadline: '10 Sep 2026',
    tags: ['Early Career', 'Fellowship', 'Any Discipline'],
    score: 28,
    type: 'alt',
    feedback: null
  }
];

var activeFilter = 'all';

function renderGrants(filter) {
  var list = document.getElementById('grants-list');
  if (!list) return;
  var filtered = filter === 'all' ? sampleGrants : sampleGrants.filter(function (g) { return g.type === filter; });
  if (filtered.length === 0) {
    list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--muted);">No grants in this category.</div>';
    return;
  }
  list.innerHTML = filtered.map(function (g) {
    var scoreClass = g.score >= 70 ? 'score-high' : g.score >= 40 ? 'score-mid' : 'score-low';
    var scoreLabel = g.score >= 70 ? 'Strong match' : g.score >= 40 ? 'Partial match' : 'Low match';
    var tags = g.tags.map(function (t) { return '<span class="tag">' + t + '</span>'; }).join('');
    var feedback = g.feedback ? '<div class="grant-feedback">' + g.feedback + '</div>' : '';
    return '<div class="grant-card">' +
      '<div class="grant-info">' +
        '<div class="grant-title">' + g.title + '</div>' +
        '<div class="grant-meta">' + g.body + ' &middot; Deadline: ' + g.deadline + '</div>' +
        '<div class="grant-tags">' + tags + '</div>' +
        feedback +
      '</div>' +
      '<div class="score-badge">' +
        '<div class="score-circle ' + scoreClass + '">' + g.score + '%</div>' +
        '<div class="score-label">' + scoreLabel + '</div>' +
      '</div>' +
    '</div>';
  }).join('');
}

function showResults() {
  var section = document.getElementById('results-section');
  if (!section) return;
  renderGrants('all');
  section.classList.add('visible');
  setTimeout(function () {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
  showToast('Matching complete — Hybrid algorithm selected');
}

document.querySelectorAll('.filter-btn').forEach(function (btn) {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.filter-btn').forEach(function (b) { b.classList.remove('active'); });
    this.classList.add('active');
    activeFilter = this.dataset.filter;
    renderGrants(activeFilter);
  });
});

var exportCsv = document.getElementById('export-csv');
var exportExcel = document.getElementById('export-excel');
if (exportCsv) exportCsv.addEventListener('click', function () { showToast('CSV file ready'); });
if (exportExcel) exportExcel.addEventListener('click', function () { showToast('Excel file downloaded'); });
// Filter buttons for results page
document.querySelectorAll('.filter-btn').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.filter-btn').forEach(function(b) {
      b.classList.remove('active');
    });
    this.classList.add('active');
    
    var filter = this.dataset.filter;
    var cards = document.querySelectorAll('.grant-card');
    
    cards.forEach(function(card) {
      if (filter === 'all') {
        card.style.display = 'flex';
      } else if (filter === 'top') {
        var score = parseFloat(card.dataset.score);
        card.style.display = score >= 70 ? 'flex' : 'none';
      } else if (filter === 'mid') {
        var score = parseFloat(card.dataset.score);
        card.style.display = (score >= 40 && score < 70) ? 'flex' : 'none';
      } else if (filter === 'alt') {
        card.style.display = card.classList.contains('alt-item') ? 'flex' : 'none';
      }
    });
  });
});