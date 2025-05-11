document.addEventListener('DOMContentLoaded', function() {
    // ======================
    // Floating Particles System
    // ======================
    const particlesContainer = document.getElementById('particles');
    if (particlesContainer) {
        const particleCount = Math.floor(window.innerWidth / 15);
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            
            // Random properties
            const size = Math.random() * 5 + 1;
            const posX = Math.random() * window.innerWidth;
            const posY = Math.random() * window.innerHeight;
            const duration = Math.random() * 15 + 10;
            const delay = Math.random() * 5;
            const opacity = Math.random() * 0.3 + 0.1;
            const color = `hsl(${Math.random() * 60 + 180}, 100%, 70%)`;
            
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}px`;
            particle.style.top = `${posY}px`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `${delay}s`;
            particle.style.opacity = opacity;
            particle.style.background = color;
            
            particlesContainer.appendChild(particle);
        }
        
        // Interactive particles
        document.addEventListener('mousemove', function(e) {
            const particles = document.querySelectorAll('.particle');
            particles.forEach(particle => {
                const x = e.clientX;
                const y = e.clientY;
                const particleX = parseFloat(particle.style.left) + parseFloat(particle.style.width) / 2;
                const particleY = parseFloat(particle.style.top) + parseFloat(particle.style.height) / 2;
                
                const distance = Math.sqrt(Math.pow(x - particleX, 2) + Math.pow(y - particleY, 2));
                
                if (distance < 100) {
                    const angle = Math.atan2(y - particleY, x - particleX);
                    const force = (100 - distance) / 20;
                    const newX = parseFloat(particle.style.left) - Math.cos(angle) * force;
                    const newY = parseFloat(particle.style.top) - Math.sin(angle) * force;
                    
                    particle.style.left = `${newX}px`;
                    particle.style.top = `${newY}px`;
                }
            });
        });
    }

    // ======================
    // Avatar Update System
    // ======================
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.getElementById('avatar-preview');
    const profileAvatar = document.getElementById('profile-avatar');
    
    // Function to update avatar with cache busting
    function updateAvatar(element) {
        if (element) {
            const timestamp = new Date().getTime();
            element.src = element.src.split('?')[0] + '?v=' + timestamp;
            element.classList.add('updating');
            setTimeout(() => element.classList.remove('updating'), 300);
        }
    }
    
    // Preview image before upload
    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    avatarPreview.src = e.target.result;
                    // Force refresh of profile image in other tabs
                    if (typeof(Storage) !== "undefined") {
                        localStorage.setItem('avatar_updated', Date.now());
                    }
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Listen for storage events to update avatar in real-time
    if (typeof(Storage) !== "undefined") {
        window.addEventListener('storage', function(event) {
            if (event.key === 'avatar_updated') {
                updateAvatar(avatarPreview);
                updateAvatar(profileAvatar);
            }
        });
    }
    
    // Check for avatar updates periodically
    setInterval(function() {
        if (typeof(Storage) !== "undefined" && localStorage.getItem('avatar_updated')) {
            updateAvatar(avatarPreview);
            updateAvatar(profileAvatar);
            localStorage.removeItem('avatar_updated');
        }
    }, 2000);
    
    // Also update when tab becomes visible
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            updateAvatar(avatarPreview);
            updateAvatar(profileAvatar);
        }
    });

    // ======================
    // UI Effects
    // ======================
    // Follow button animation
    const followBtn = document.querySelector('.follow-form button');
    if (followBtn) {
        followBtn.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
        });
    }

    // Stats hover effect
    const stats = document.querySelectorAll('.profile-stats span');
    stats.forEach(stat => {
        stat.addEventListener('mouseenter', () => {
            stat.style.transform = 'translateY(-3px)';
            stat.style.textShadow = '0 0 5px var(--primary)';
        });
        stat.addEventListener('mouseleave', () => {
            stat.style.transform = 'translateY(0)';
            stat.style.textShadow = 'none';
        });
    });

    // Avatar glow effect
    const avatar = document.querySelector('.profile-avatar');
    if (avatar) {
        avatar.addEventListener('mouseenter', () => {
            avatar.style.boxShadow = '0 0 30px var(--primary)';
        });
        avatar.addEventListener('mouseleave', () => {
            avatar.style.boxShadow = '0 0 20px var(--primary)';
        });
    }
});