// Custom JavaScript for College Hub
document.addEventListener('DOMContentLoaded', function() {
    // Add active class to current nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Animate cards on scroll
    const observerCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__fadeInUp');
                entry.target.style.opacity = 1;
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, {
        threshold: 0.1
    });

    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = 0;
        observer.observe(card);
    });

    // Add animation to alerts
    document.querySelectorAll('.alert').forEach(alert => {
        alert.classList.add('animate__animated', 'animate__fadeIn');
    });

    // Add animation to status badges
    document.querySelectorAll('.badge').forEach(badge => {
        badge.classList.add('animate__animated', 'animate__fadeIn');
    });

    // Smooth scroll to messages
    if(document.querySelector('.alert')) {
        window.scrollTo({
            top: document.querySelector('.alert').offsetTop - 100,
            behavior: 'smooth'
        });
    }

    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.classList.add('animate__fadeOut');
            setTimeout(() => alert.remove(), 1000);
        });
    }, 5000);

    // Add hover effects to cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg', 'animate__animated', 'animate__pulse');
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg', 'animate__animated', 'animate__pulse');
        });
    });
});
