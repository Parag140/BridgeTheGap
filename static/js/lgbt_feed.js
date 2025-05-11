
// Initialize particles.js or any custom scripts
// Example if you're using particles.js
particlesJS.load('particles', 'path/to/particles.json', function() {
    console.log('Particles.js config loaded');
});

// Expand/Collapse comment sections
document.querySelectorAll('.comment-btn').forEach(button => {
    button.addEventListener('click', () => {
        const postId = button.getAttribute('data-post-id');
        const commentsSection = document.getElementById(`comments-${postId}`);
        if (commentsSection.style.display === "none" || commentsSection.style.display === "") {
            commentsSection.style.display = "block";
        } else {
            commentsSection.style.display = "none";
        }
    });
});

// Simple like button toggle
document.querySelectorAll('.like-btn').forEach(button => {
    button.addEventListener('click', () => {
        button.classList.toggle('liked');
        const likeCountSpan = button.querySelector('.like-count');
        let count = parseInt(likeCountSpan.innerText);
        if (button.classList.contains('liked')) {
            count++;
        } else {
            count--;
        }
        likeCountSpan.innerText = count;
    });
});