document.addEventListener('DOMContentLoaded', function() {
    // Initialize particle grid
    const grid = document.getElementById('particleGrid');
    const cols = Math.floor(window.innerWidth / 20);
    const rows = Math.floor(window.innerHeight / 20);
    
    grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    grid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    
    for (let i = 0; i < cols * rows; i++) {
        const particle = document.createElement('div');
        particle.className = 'grid-particle';
        grid.appendChild(particle);
        
        // Random activation
        if (Math.random() > 0.95) {
            particle.classList.add('active');
            setInterval(() => {
                particle.classList.toggle('active');
            }, 2000 + Math.random() * 3000);
        }
    }
    
    // Dynamic subtitle effect
    const subtitle = document.getElementById('dynamicSubtitle');
    if (subtitle) {
        const text = subtitle.textContent;
        subtitle.textContent = '';
        
        let i = 0;
        const typeWriter = setInterval(() => {
            if (i < text.length) {
                subtitle.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(typeWriter);
                
                // Continue animation
                setInterval(() => {
                    subtitle.style.textShadow = `0 0 5px ${getRandomColor()}`;
                }, 100);
            }
        }, 50);
    }
    
    // Cyber button hover effects
    const buttons = document.querySelectorAll('.cyber-btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.05)';
            this.style.boxShadow = `0 0 25px ${this.classList.contains('btn-primary') ? 'var(--primary)' : 'var(--accent)'}`;
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 0 10px rgba(0, 247, 255, 0.3)';
        });
    });
    
    // Audio feedback
    document.addEventListener('click', function() {
        playSound('click');
    });
    
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            playSound('hover');
        });
    });
    
    // Helper functions
    function getRandomColor() {
        const colors = ['var(--primary)', 'var(--secondary)', 'var(--accent)', 'var(--success)'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
    
    function playSound(type) {
        // In a real implementation, you would play actual sound files
        console.log(`Playing ${type} sound`);
    }
    
    // Responsive adjustments
    function handleResize() {
        const newCols = Math.floor(window.innerWidth / 20);
        const newRows = Math.floor(window.innerHeight / 20);
        grid.style.gridTemplateColumns = `repeat(${newCols}, 1fr)`;
        grid.style.gridTemplateRows = `repeat(${newRows}, 1fr)`;
    }
    
    window.addEventListener('resize', handleResize);
});