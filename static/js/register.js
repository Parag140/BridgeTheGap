
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
                particle.style.animationDuration = `${duration}s`;
                particle.style.animationDelay = `${delay}s`;
                particle.style.opacity = opacity;
                
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
            
            // Input focus effects
            const inputs = document.querySelectorAll('input');
            inputs.forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.querySelector('label').style.textShadow = '0 0 10px var(--primary)';
                });
                
                input.addEventListener('blur', function() {
                    this.parentElement.querySelector('label').style.textShadow = 'none';
                });
            });
        });
        function selectGender(gender) {
            // Remove selected class from all buttons
            document.querySelectorAll('.gender-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            
            // Add selected class to clicked button
            event.target.classList.add('selected');
            
            // Set the hidden input value
            document.getElementById('gender').value = gender;
            
            // Show pronouns field for LGBTQ+ and Other options
            const pronounsInput = document.getElementById('pronouns-input');
            if (gender === 'lgbt' || gender === 'other') {
                pronounsInput.classList.add('show');
            } else {
                pronounsInput.classList.remove('show');
            }
            
            // Enable the register button
            document.getElementById('register-btn').disabled = false;
        }
        
        // Particle effect script
        document.addEventListener('DOMContentLoaded', function() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 30;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');
                
                // Random size between 1px and 3px
                const size = Math.random() * 2 + 1;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                
                // Random position
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                
                // Random animation duration
                const duration = Math.random() * 20 + 10;
                particle.style.animationDuration = `${duration}s`;
                
                // Random color (blueish or pinkish)
                const colors = ['rgba(0, 255, 252, 0.5)', 'rgba(255, 42, 109, 0.5)'];
                particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                
                particlesContainer.appendChild(particle);
            }
        });