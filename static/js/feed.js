document.addEventListener('DOMContentLoaded', function() {
    // Create floating particles
    const particlesContainer = document.getElementById('particles');
    const particleCount = Math.floor(window.innerWidth / 20);
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random properties
        const size = Math.random() * 5 + 1;
        const posX = Math.random() * window.innerWidth;
        const posY = Math.random() * window.innerHeight;
        const duration = Math.random() * 10 + 10;
        const delay = Math.random() * 5;
        const opacity = Math.random() * 0.3 + 0.1;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}px`;
        particle.style.top = `${posY}px`;
        particle.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
        particle.style.opacity = opacity;
        
        // Random color
        const colors = ['var(--primary)', 'var(--secondary)', 'var(--accent)'];
        particle.style.background = colors[Math.floor(Math.random() * colors.length)];
        
        particlesContainer.appendChild(particle);
    }
     // Confirm before deleting
     const deleteForms = document.querySelectorAll('.delete-form');
    
     deleteForms.forEach(form => {
         form.addEventListener('submit', function(e) {
             if (!confirm('Are you sure you want to delete this post?')) {
                 e.preventDefault();
             }
         });
     });
    
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
    
    // Image upload preview
    const imageUpload = document.getElementById('image-upload');
    if (imageUpload) {
        imageUpload.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Create preview
                    const preview = document.createElement('div');
                    preview.style.position = 'relative';
                    preview.style.marginTop = '10px';
                    
                    preview.innerHTML = `
                        <img src="${e.target.result}" style="max-width: 100%; max-height: 200px; border-radius: 5px;">
                        <button type="button" style="position: absolute; top: 5px; right: 5px; background: var(--accent); border: none; border-radius: 50%; width: 25px; height: 25px; color: white; cursor: pointer;">×</button>
                    `;
                    
                    const form = imageUpload.closest('form');
                    const existingPreview = form.querySelector('.image-preview');
                    if (existingPreview) {
                        existingPreview.remove();
                    }
                    
                    preview.classList.add('image-preview');
                    form.insertBefore(preview, form.querySelector('.post-actions'));
                    
                    // Remove button
                    preview.querySelector('button').addEventListener('click', function() {
                        preview.remove();
                        imageUpload.value = '';
                    });
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Like animation
    document.querySelectorAll('.like-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('.btn-like');
            if (button) {
                button.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    button.style.transform = 'scale(1)';
                }, 300);
            }
        });
    });
});