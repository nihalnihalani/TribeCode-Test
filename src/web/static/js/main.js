// Main JS for BuildRadar

document.addEventListener('DOMContentLoaded', () => {
    console.log("BuildRadar Initialized 🚀");

    // Auto-dismiss alerts (if we add them later)
    
    // Confirm Like Action
    const likeForms = document.querySelectorAll('.like-form');
    likeForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!confirm('Are you sure you want to like this post? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Dynamic "Loading" state for Scout button
    const scoutForm = document.querySelector('form[action="/scout"]');
    if (scoutForm) {
        scoutForm.addEventListener('submit', (e) => {
            const btn = scoutForm.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '⏳ Scouting... (Check Archive)';
            
            // Re-enable after 2 seconds (since it's a background task, the redirect happens fast)
            // But if we stay on page (AJAX), we'd keep it disabled. 
            // Since it's a form POST redirect, the page will reload anyway.
        });
    }
});

