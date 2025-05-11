// login.js - Cyberpunk Authentication Interface

document.addEventListener('DOMContentLoaded', function() {
    // Initialize particle effects
    initParticles();
    
    // Add interactive effects to form elements
    setupFormInteractions();
    
    // Add scanline animation
    setupScanlineEffect();
    
    // Add system boot-up sequence
    systemBootSequence();
});

function initParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = Math.floor(window.innerWidth / 8); // More dense particles
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Cyberpunk-style random properties
        const size = Math.random() * 4 + 1;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;
        const duration = Math.random() * 15 + 15; // Slower movement
        const delay = Math.random() * 10;
        const opacity = Math.random() * 0.5 + 0.2; // More visible
        
        // Neon colors
        const colors = [
            '#0ff0fc', // Electric cyan
            '#ff2a6d', // Hot pink
            '#f5d300', // Neon yellow
            '#05ffa1', // Mint green
            '#ff3864'  // Raspberry
        ];
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}px`;
        particle.style.top = `${posY}px`;
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `${delay}s`;
        particle.style.opacity = opacity;
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        particle.style.boxShadow = `0 0 ${size * 2}px currentColor`;
        
        particlesContainer.appendChild(particle);
    }
    
    // Interactive particles that react to mouse
    document.addEventListener('mousemove', function(e) {
        const particles = document.querySelectorAll('.particle');
        const mouseX = e.clientX;
        const mouseY = e.clientY;
        
        particles.forEach(particle => {
            const rect = particle.getBoundingClientRect();
            const particleX = rect.left + rect.width / 2;
            const particleY = rect.top + rect.height / 2;
            
            const distance = Math.sqrt(
                Math.pow(mouseX - particleX, 2) + 
                Math.pow(mouseY - particleY, 2)
            );
            
            if (distance < 150) {
                const angle = Math.atan2(mouseY - particleY, mouseX - particleX);
                const force = (150 - distance) / 25;
                
                gsap.to(particle, {
                    x: `+=${Math.cos(angle) * force}`,
                    y: `+=${Math.sin(angle) * force}`,
                    duration: 0.5,
                    ease: "power2.out"
                });
            }
        });
    });
}

function setupFormInteractions() {
    const inputs = document.querySelectorAll('.form-group input');
    const labels = document.querySelectorAll('.form-group label');
    const btn = document.querySelector('.btn');
    
    // Input focus effects
    inputs.forEach((input, index) => {
        input.addEventListener('focus', function() {
            labels[index].style.color = '#0ff0fc';
            labels[index].style.textShadow = '0 0 8px #0ff0fc';
            this.style.borderColor = '#0ff0fc';
            this.style.boxShadow = '0 0 10px rgba(0, 255, 252, 0.5)';
        });
        
        input.addEventListener('blur', function() {
            labels[index].style.color = '';
            labels[index].style.textShadow = '';
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
        
        // Cyberpunk keypress effect
        input.addEventListener('keydown', function(e) {
            if (e.key.length === 1 || e.key === 'Backspace') {
                const char = document.createElement('span');
                char.className = 'keypress-char';
                char.textContent = e.key === 'Backspace' ? '⌫' : e.key;
                char.style.left = `${Math.random() * this.offsetWidth}px`;
                char.style.top = `${-10 - Math.random() * 20}px`;
                char.style.color = `hsl(${Math.random() * 60 + 180}, 100%, 70%)`;
                this.parentNode.appendChild(char);
                
                // Animate and remove
                gsap.to(char, {
                    y: -50,
                    opacity: 0,
                    duration: 1,
                    onComplete: () => char.remove()
                });
            }
        });
    });
    
    // Button hover effects
    btn.addEventListener('mouseenter', function() {
        gsap.to(this, {
            y: -3,
            boxShadow: '0 5px 15px rgba(0, 255, 252, 0.6)',
            duration: 0.3
        });
    });
    
    btn.addEventListener('mouseleave', function() {
        gsap.to(this, {
            y: 0,
            boxShadow: '',
            duration: 0.3
        });
    });
    
    // Form submission effect
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Create loading effect
            const btn = this.querySelector('.btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-cog fa-spin"></i> AUTHENTICATING...';
            btn.disabled = true;
            
            // Add cyberpunk glitch effect
            gsap.to(this, {
                x: [0, 5, -5, 0],
                y: [0, 3, -3, 0],
                duration: 0.2,
                repeat: 3,
                onComplete: () => {
                    // Submit the form after effects
                    this.submit();
                }
            });
        });
    }
}

function setupScanlineEffect() {
    const scanline = document.querySelector('.scanline');
    if (scanline) {
        let pos = 0;
        function animateScanline() {
            pos = (pos + 1) % 100;
            scanline.style.background = `linear-gradient(
                to bottom,
                transparent 0%,
                rgba(0, 255, 252, 0.1) ${pos}%,
                rgba(0, 255, 252, 0.1) ${pos + 2}%,
                transparent ${pos + 3}%
            )`;
            requestAnimationFrame(animateScanline);
        }
        animateScanline();
    }
}

function systemBootSequence() {
    const messages = [
        "SYSTEM BOOT INITIATED",
        "LOADING CYBER CORE...",
        "CHECKING NEURAL LINKS...",
        "VERIFYING USER DATABASE...",
        "ESTABLISHING ENCRYPTION...",
        "SYSTEM READY"
    ];
    
    const authForm = document.querySelector('.auth-form h2');
    if (authForm) {
        let currentMessage = 0;
        const originalText = authForm.textContent;
        
        const interval = setInterval(() => {
            authForm.textContent = messages[currentMessage];
            authForm.style.color = `hsl(${currentMessage * 60}, 100%, 70%)`;
            
            // Add glitch effect
            if (currentMessage < messages.length - 1) {
                gsap.to(authForm, {
                    x: [0, 2, -2, 0],
                    duration: 0.1,
                    repeat: 3
                });
            }
            
            currentMessage++;
            if (currentMessage >= messages.length) {
                clearInterval(interval);
                authForm.textContent = originalText;
                authForm.style.color = '';
                
                // Final reveal effect
                gsap.fromTo(authForm,
                    { opacity: 0, scale: 0.8 },
                    { opacity: 1, scale: 1, duration: 0.5, ease: "back.out" }
                );
            }
        }, 500);
    }
    
    // Terminal-like typing effect for alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const originalText = alert.textContent;
        alert.textContent = '';
        
        let i = 0;
        const typing = setInterval(() => {
            if (i < originalText.length) {
                alert.textContent += originalText.charAt(i);
                i++;
            } else {
                clearInterval(typing);
            }
        }, 30);
    });
}

// Error message effects
function showError(message) {
    const errorBox = document.createElement('div');
    errorBox.className = 'error-message';
    errorBox.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    document.querySelector('.auth-form').prepend(errorBox);
    
    // Animation
    gsap.fromTo(errorBox,
        { y: -20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.3 }
    );
    
    // Auto-remove after delay
    setTimeout(() => {
        gsap.to(errorBox, {
            y: -20,
            opacity: 0,
            duration: 0.3,
            onComplete: () => errorBox.remove()
        });
    }, 5000);
}

// Flash message handling
function handleFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Entrance animation
        gsap.from(alert, {
            y: -20,
            opacity: 0,
            duration: 0.5,
            ease: "back.out"
        });
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            gsap.to(alert, {
                y: 20,
                opacity: 0,
                duration: 0.5,
                onComplete: () => alert.remove()
            });
        }, 5000);
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initParticles();
    setupFormInteractions();
    setupScanlineEffect();
    systemBootSequence();
    handleFlashMessages();
});