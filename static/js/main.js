/* NetShield AI — Main JavaScript */

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Navbar background opacity on scroll
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.glass-nav');
    if (nav) {
        nav.style.background = window.scrollY > 50
            ? 'rgba(10, 14, 23, 0.96)'
            : 'rgba(10, 14, 23, 0.88)';
    }
});
