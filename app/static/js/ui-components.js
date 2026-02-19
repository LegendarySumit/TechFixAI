/**
 * UI Components Library for TechFixAI
 * Reusable components adapted from VoicetoTicket
 */

// Audio Visualizer Component (Enhanced with Circular Mode)
class AudioVisualizer {
  constructor(containerId, barCount = 20, circularMode = false) {
    this.container = document.getElementById(containerId);
    this.barCount = barCount;
    this.bars = [];
    this.isRecording = false;
    this.animationId = null;
    this.audioLevel = 50;
    this.circularMode = circularMode;

    this.init();
  }

  init() {
    if (this.circularMode) {
      this.initCircular();
    } else {
      this.initLinear();
    }
  }

  initLinear() {
    this.container.className = 'd-flex align-items-end justify-content-center gap-1';
    this.container.style.height = '80px';
    
    for (let i = 0; i < this.barCount; i++) {
      const bar = document.createElement('div');
      bar.className = 'audio-bar';
      bar.style.width = '4px';
      bar.style.height = '8px';
      bar.style.borderRadius = '2px';
      bar.style.backgroundColor = 'var(--accent-primary, #3b82f6)';
      bar.style.transition = 'all 0.1s ease';
      this.bars.push(bar);
      this.container.appendChild(bar);
    }
  }

  initCircular() {
    this.container.style.position = 'relative';
    this.container.style.width = '100%';
    this.container.style.height = '100%';
    this.container.style.display = 'flex';
    this.container.style.alignItems = 'center';
    this.container.style.justifyContent = 'center';
    
    const circleSize = 200; // Diameter of the circle
    const centerX = circleSize / 2;
    const centerY = circleSize / 2;
    const radius = 80;
    
    for (let i = 0; i < this.barCount; i++) {
      const angle = (i / this.barCount) * Math.PI * 2;
      const bar = document.createElement('div');
      bar.className = 'audio-bar-circular';
      bar.style.position = 'absolute';
      bar.style.width = '4px';
      bar.style.height = '20px';
      bar.style.backgroundColor = '#ef4444';
      bar.style.transformOrigin = 'center bottom';
      bar.style.borderRadius = '2px';
      bar.style.transition = 'height 0.05s ease';
      
      // Position the bar
      const x = centerX + Math.cos(angle - Math.PI / 2) * radius;
      const y = centerY + Math.sin(angle - Math.PI / 2) * radius;
      bar.style.left = `${x}px`;
      bar.style.top = `${y}px`;
      bar.style.transform = `translate(-50%, 0) rotate(${angle}rad)`;
      
      this.bars.push(bar);
      this.container.appendChild(bar);
    }
    
    // Add timer display in center
    const timerDiv = document.createElement('div');
    timerDiv.id = 'timer-display';
    timerDiv.className = 'circle-timer';
    timerDiv.style.position = 'absolute';
    timerDiv.style.zIndex = '10';
    timerDiv.textContent = '00:00';
    this.container.appendChild(timerDiv);
  }

  start(recorder) {
    this.isRecording = true;
    this.animate(recorder);
  }

  stop() {
    this.isRecording = false;
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    this.reset();
  }

  animate(recorder) {
    if (!this.isRecording) return;

    const audioLevel = recorder ? recorder.getAudioLevel() : Math.random() * 70 + 20;
    
    if (this.circularMode) {
      this.bars.forEach((bar, i) => {
        const variation = Math.sin(i / 3 + Date.now() / 150) * 0.7 + 0.3;
        const height = 20 + (audioLevel * variation);
        bar.style.height = `${Math.max(15, Math.min(60, height))}px`;
      });
    } else {
      this.bars.forEach((bar, i) => {
        const height = Math.sin(i / 5 + Date.now() / 100) * audioLevel + 20;
        bar.style.height = `${Math.max(8, height)}px`;
        bar.style.backgroundColor = this.isRecording ? '#ef4444' : 'var(--accent-primary, #3b82f6)';
      });
    }

    this.animationId = requestAnimationFrame(() => this.animate(recorder));
  }

  reset() {
    if (this.circularMode) {
      this.bars.forEach(bar => {
        bar.style.height = '20px';
      });
    } else {
      this.bars.forEach(bar => {
        bar.style.height = '8px';
        bar.style.backgroundColor = 'var(--accent-primary, #3b82f6)';
      });
    }
  }
}

// Recording Timer Component
class RecordingTimer {
  constructor(displayElementId) {
    this.element = document.getElementById(displayElementId);
    this.seconds = 0;
    this.interval = null;
  }

  start() {
    this.seconds = 0;
    this.update();
    this.interval = setInterval(() => {
      this.seconds++;
      this.update();
    }, 1000);
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }

  reset() {
    this.stop();
    this.seconds = 0;
    this.update();
  }

  update() {
    const mins = Math.floor(this.seconds / 60);
    const secs = this.seconds % 60;
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    this.element.textContent = formatted;
  }

  getSeconds() {
    return this.seconds;
  }
}

// Security Badge Component
function createSecurityBadge(encrypted = true, level = "AES-256-GCM") {
  return `
    <div class="d-inline-flex align-items-center gap-2 px-3 py-2 rounded-pill" 
         style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);">
      <i class="bi bi-lock-fill" style="color: #10b981;"></i>
      <span class="small font-monospace" style="color: #10b981;">
        ${encrypted ? 'Secure' : 'Unencrypted'} • ${level}
      </span>
    </div>
  `;
}

// Ticket Status Badge Component
function createTicketBadge(status) {
  const statusConfig = {
    "assigned": { color: "primary", icon: "person-fill" },
    "in_progress": { color: "warning", icon: "lightning-fill" },
    "resolved": { color: "success", icon: "check-circle-fill" },
    "open": { color: "info", icon: "clock-fill" },
    "on-hold": { color: "secondary", icon: "pause-circle-fill" },
  };

  const config = statusConfig[status] || statusConfig["assigned"];

  return `
    <span class="badge bg-${config.color}">
      <i class="bi bi-${config.icon} me-1"></i>${status.toUpperCase().replace('_', ' ')}
    </span>
  `;
}

// Developer Card Component (returns HTML string)
function createDeveloperCard(developer, isActive = false) {
  const statusDot = developer.status === 'online' 
    ? '<span class="position-absolute top-0 start-100 translate-middle p-1 bg-success border border-light rounded-circle"></span>'
    : '<span class="position-absolute top-0 start-100 translate-middle p-1 bg-secondary border border-light rounded-circle"></span>';

  return `
    <div class="card h-100 ${isActive ? 'border-primary shadow' : ''}" style="cursor: pointer;">
      <div class="card-body">
        <div class="d-flex align-items-center gap-3">
          <div class="position-relative">
            <div class="rounded-circle bg-gradient d-flex align-items-center justify-content-center text-white fw-bold"
                 style="width: 48px; height: 48px; background: linear-gradient(135deg, #3b82f6, #2563eb);">
              ${developer.avatar || developer.name.charAt(0)}
            </div>
            ${statusDot}
          </div>
          <div class="flex-grow-1">
            <h6 class="mb-0 fw-bold">${developer.name}</h6>
            <p class="mb-0 small text-muted">${developer.title || developer.expertise}</p>
            <small class="text-muted">
              <i class="bi bi-clock"></i> ${developer.responseTime || '2-5 min'}
            </small>
          </div>
        </div>
        ${developer.expertise ? `
          <div class="mt-2">
            <small class="text-muted">Expertise: ${developer.expertise}</small>
          </div>
        ` : ''}
      </div>
    </div>
  `;
}

// Message Bubble Component (returns HTML string)
function createMessageBubble(message, sender, timestamp, isUser = false) {
  const messageClass = isUser ? 'user' : 'developer';
  const bubbleClass = isUser ? 'chat-bubble user' : 'chat-bubble developer';
  const avatar = sender.charAt(0).toUpperCase();
  const avatarBg = isUser ? 'bg-info' : 'bg-primary';
  const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

  return `
    <div class="chat-message ${messageClass}">
      ${!isUser ? `
        <div class="rounded-circle ${avatarBg} d-flex align-items-center justify-content-center text-white fw-bold me-2"
             style="width: 28px; height: 28px; flex-shrink: 0; font-size: 0.75rem;">
          ${avatar}
        </div>
      ` : ''}
      <div class="${bubbleClass}">
        <p class="mb-1" style="line-height: 1.5;">${message}</p>
        ${timeStr ? `<div class="chat-timestamp">${timeStr}</div>` : ''}
      </div>
      ${isUser ? `
        <div class="rounded-circle ${avatarBg} d-flex align-items-center justify-content-center text-white fw-bold ms-2"
             style="width: 28px; height: 28px; flex-shrink: 0; font-size: 0.75rem;">
          ${avatar}
        </div>
      ` : ''}
    </div>
  `;
}

// Process Step Indicator
function createProcessStep(step, label, completed = false, current = false, error = false) {
  let badgeClass = 'bg-secondary text-white';
  let icon = step;
  
  if (completed) {
    badgeClass = 'bg-success text-white';
    icon = '✓';
  } else if (current) {
    badgeClass = 'bg-primary text-white';
  } else if (error) {
    badgeClass = 'bg-danger text-white';
    icon = '!';
  }

  const textClass = completed ? 'text-success' : current ? 'text-primary' : 'text-muted';

  return `
    <div class="d-flex align-items-center gap-3">
      <div class="rounded-circle ${badgeClass} d-flex align-items-center justify-content-center fw-bold ${current ? 'pulse' : ''}"
           style="width: 40px; height: 40px;">
        ${icon}
      </div>
      <span class="fw-medium ${textClass}">${label}</span>
    </div>
  `;
}

// Language Badge Component
function createLanguageBadge(language) {
  const flags = {
    'Japanese': '🇯🇵',
    'Odia': '🇮🇳',
    'Hindi': '🇮🇳',
    'English': '🇺🇸',
    'Chinese': '🇨🇳',
    'Spanish': '🇪🇸'
  };

  return `
    <span class="badge bg-info">
      ${flags[language] || '🌐'} ${language}
    </span>
  `;
}

// Export components
window.AudioVisualizer = AudioVisualizer;
window.RecordingTimer = RecordingTimer;
window.createSecurityBadge = createSecurityBadge;
window.createTicketBadge = createTicketBadge;
window.createDeveloperCard = createDeveloperCard;
window.createMessageBubble = createMessageBubble;
window.createProcessStep = createProcessStep;
window.createLanguageBadge = createLanguageBadge;
