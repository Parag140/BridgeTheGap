document.addEventListener('DOMContentLoaded', function() {
    // Like functionality
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            likePost(postId, this);
        });
    });
    
    // Comment toggle
    document.querySelectorAll('.comment-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const commentsSection = document.getElementById(`comments-${postId}`);
            commentsSection.style.display = commentsSection.style.display === 'none' ? 'block' : 'none';
        });
    });
    
    // Comment submission
    document.querySelectorAll('.add-comment').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            const input = this.querySelector('input');
            const content = input.value.trim();
            
            if (content) {
                addComment(postId, content, this);
                input.value = '';
            }
        });
    });
    
    // Follow buttons
    document.querySelectorAll('.follow-btn').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.dataset.userId;
            followUser(userId, this);
        });
    });
});

function likePost(postId, element) {
    fetch(`/post/${postId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            element.classList.add('liked');
        } else {
            element.classList.remove('liked');
        }
        element.querySelector('.like-count').textContent = data.like_count;
    })
    .catch(error => console.error('Error:', error));
}

function addComment(postId, content, formElement) {
    fetch(`/post/${postId}/comment`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `content=${encodeURIComponent(content)}`
    })
    .then(response => {
        if (response.ok) {
            location.reload(); // Refresh to show new comment
        }
    })
    .catch(error => console.error('Error:', error));
}

function followUser(userId, element) {
    fetch(`/user/${userId}/follow`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.is_following) {
            element.textContent = 'Following';
            element.classList.add('following');
        } else {
            element.textContent = 'Follow';
            element.classList.remove('following');
        }
        if (element.nextElementSibling && element.nextElementSibling.classList.contains('follower-count')) {
            element.nextElementSibling.textContent = `${data.follower_count} followers`;
        }
    })
    .catch(error => console.error('Error:', error));
}