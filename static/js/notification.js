document.addEventListener('DOMContentLoaded', function() {
    // Create floating particles
    const particlesContainer = document.getElementById('particles');
    const particleCount = Math.floor(window.innerWidth / 15);
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random properties
        const size = Math.random() * 6 + 2;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;
        const duration = Math.random() * 15 + 10;
        const delay = Math.random() * 5;
        const opacity = Math.random() * 0.4 + 0.1;
        const color = `hsl(${Math.random() * 60 + 180}, 100%, 70%)`;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}px`;
        particle.style.top = `${posY}px`;
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `${delay}s`;
        particle.style.opacity = opacity;
        particle.style.background = color;
        particle.style.boxShadow = `0 0 ${size * 2}px ${color}`;
        
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
            
            if (distance < 150) {
                const angle = Math.atan2(y - particleY, x - particleX);
                const force = (150 - distance) / 15;
                const newX = parseFloat(particle.style.left) - Math.cos(angle) * force;
                const newY = parseFloat(particle.style.top) - Math.sin(angle) * force;
                
                particle.style.left = `${newX}px`;
                particle.style.top = `${newY}px`;
            }
        });
    });
    
    // Button animations
    const cyberButtons = document.querySelectorAll('.cyber-btn');
    cyberButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = `0 0 40px ${this.classList.contains('cyber-btn-secondary') ? 'var(--accent)' : 'var(--primary)'}`;
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = `0 0 15px ${this.classList.contains('cyber-btn-secondary') ? 'var(--accent)' : 'var(--primary)'}`;
        });
    });
    
    // Random flicker effect
    setInterval(() => {
        if (Math.random() > 0.7) {
            document.querySelector('.scanlines').style.animation = 'flicker 0.5s';
            setTimeout(() => {
                document.querySelector('.scanlines').style.animation = '';
            }, 500);
        }
    }, 3000);
});

function showTransmissions() {
    alert('Displaying all transmissions');
}

function showFollowers() {
    alert('Displaying followers list');
}

function showFollowing() {
    alert('Displaying following list');
}