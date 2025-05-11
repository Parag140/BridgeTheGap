// This ensures no JavaScript interferes with the button
document.addEventListener('DOMContentLoaded', function() {
    // Explicitly set the button to do nothing but follow its href
    const accessBtn = document.getElementById('main-access-btn');
    if (accessBtn) {
        accessBtn.onclick = function(e) {
            // Allow default link behavior (navigation to /login)
            return true;
        };
    }
    
    // Keep gender selector functions if needed elsewhere
    window.showGenderSelector = function() {
        document.getElementById('gender-selector').style.display = 'block';
        document.querySelector('.auth-buttons').style.display = 'none';
    };
    
    window.hideGenderSelector = function() {
        document.getElementById('gender-selector').style.display = 'none';
        document.querySelector('.auth-buttons').style.display = 'block';
    };
    
    window.selectGender = function(gender) {
        // Gender selection logic if needed elsewhere
    };
});