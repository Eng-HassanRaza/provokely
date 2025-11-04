// ReviewFlow Landing Page - Advanced Interactions & Animations

class ReviewFlowLanding {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupNavigation();
        this.setupPlatformInteractions();
        this.setupSocialCards();
        this.setupParallaxEffects();
        this.setupPerformanceOptimizations();
    }

    // Advanced Scroll Animations
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    
                    // Stagger animation for multiple elements
                    if (entry.target.classList.contains('social-post-card')) {
                        const cards = document.querySelectorAll('.social-post-card');
                        cards.forEach((card, index) => {
                            setTimeout(() => {
                                card.classList.add('revealed');
                            }, index * 100);
                        });
                    }
                }
            });
        }, observerOptions);

        document.querySelectorAll('.scroll-reveal').forEach(el => {
            observer.observe(el);
        });
    }

    // Enhanced Navigation
    setupNavigation() {
        const nav = document.querySelector('.nav-floating');
        let lastScrollY = window.scrollY;

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    const offsetTop = target.offsetTop - 100;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Navbar scroll effects
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                nav.style.transform = 'translateY(-100px)';
            } else {
                nav.style.transform = 'translateY(0)';
            }
            
            lastScrollY = currentScrollY;
        });

        // Active section highlighting
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-floating a[href^="#"]');

        window.addEventListener('scroll', () => {
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop - 150;
                if (window.scrollY >= sectionTop) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        });
    }

    // Interactive Platform Network
    setupPlatformInteractions() {
        const platformNodes = document.querySelectorAll('.platform-node');
        
        platformNodes.forEach(node => {
            node.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.2)';
                this.style.zIndex = '10';
                
                // Add ripple effect
                this.style.boxShadow = '0 0 0 10px rgba(255, 107, 107, 0.3)';
                
                // Show platform name
                this.setAttribute('data-tooltip', this.className.split(' ')[1]);
            });
            
            node.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.zIndex = '2';
                this.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
                this.removeAttribute('data-tooltip');
            });

            node.addEventListener('click', function() {
                // Add click animation
                this.style.animation = 'none';
                setTimeout(() => {
                    this.style.animation = 'float-node 4s ease-in-out infinite';
                }, 100);
                
                // Show platform details
                this.showPlatformDetails();
            });
        });
    }

    // Social Proof Cards Interactions
    setupSocialCards() {
        const socialCards = document.querySelectorAll('.social-post-card');
        
        socialCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'rotate(0deg) scale(1.05)';
                this.style.zIndex = '10';
                
                // Add glow effect
                this.style.boxShadow = '0 15px 40px rgba(255, 107, 107, 0.2)';
            });
            
            card.addEventListener('mouseleave', function() {
                const rotation = this.style.getPropertyValue('--rotation') || '0deg';
                this.style.transform = `rotate(${rotation}) scale(1)`;
                this.style.zIndex = '1';
                this.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
            });

            // Click to expand
            card.addEventListener('click', function() {
                this.classList.toggle('expanded');
                if (this.classList.contains('expanded')) {
                    this.style.transform = 'rotate(0deg) scale(1.1)';
                    this.style.zIndex = '20';
                } else {
                    const rotation = this.style.getPropertyValue('--rotation') || '0deg';
                    this.style.transform = `rotate(${rotation}) scale(1)`;
                    this.style.zIndex = '1';
                }
            });
        });
    }

    // Parallax Effects
    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('.hero-badge, .hero-title .accent-word');
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            parallaxElements.forEach(element => {
                element.style.transform = `translateY(${rate}px)`;
            });
        });
    }

    // Performance Optimizations
    setupPerformanceOptimizations() {
        // Throttle scroll events
        let ticking = false;
        
        function updateOnScroll() {
            // Scroll-based animations here
            ticking = false;
        }
        
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateOnScroll);
                ticking = true;
            }
        });

        // Lazy load images
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));

        // Preload critical resources
        this.preloadCriticalResources();
    }

    preloadCriticalResources() {
        const criticalFonts = [
            'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800;900&display=swap',
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
        ];

        criticalFonts.forEach(font => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'style';
            link.href = font;
            document.head.appendChild(link);
        });
    }

    // Demo Interaction Enhancement
    enhanceDemoInteraction() {
        const demoItems = document.querySelectorAll('.demo-item');
        const demoArrow = document.querySelector('.demo-arrow');
        
        demoItems.forEach((item, index) => {
            item.addEventListener('mouseenter', () => {
                demoArrow.style.color = 'var(--accent-coral)';
                demoArrow.style.transform = 'scale(1.2)';
            });
            
            item.addEventListener('mouseleave', () => {
                demoArrow.style.color = 'var(--accent-coral)';
                demoArrow.style.transform = 'scale(1)';
            });
        });

        // Animate arrow on scroll
        const demoObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    demoArrow.style.animation = 'pulse-flow 2s infinite';
                } else {
                    demoArrow.style.animation = 'none';
                }
            });
        });

        demoObserver.observe(document.querySelector('.demo-container'));
    }

    // CTA Button Enhancements
    enhanceCTAButtons() {
        const ctaButtons = document.querySelectorAll('.btn-primary-magazine, .btn-secondary-magazine');
        
        ctaButtons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px) scale(1.02)';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });

            // Add click ripple effect
            button.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }

    // Typing Animation for Hero Title
    typeWriterEffect() {
        const titleElement = document.querySelector('.hero-title');
        const text = titleElement.textContent;
        titleElement.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                titleElement.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        };
        
        setTimeout(typeWriter, 1000);
    }

    // Initialize all enhancements
    enhanceAll() {
        this.enhanceDemoInteraction();
        this.enhanceCTAButtons();
        this.typeWriterEffect();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ReviewFlowLanding();
});

// Add CSS for ripple effect
const rippleCSS = `
.btn-primary-magazine, .btn-secondary-magazine {
    position: relative;
    overflow: hidden;
}

.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: scale(0);
    animation: ripple-animation 0.6s linear;
    pointer-events: none;
}

@keyframes ripple-animation {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.social-post-card.expanded {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(1.2);
    z-index: 1000;
    max-width: 90vw;
    max-height: 90vh;
    overflow-y: auto;
}

.nav-floating a.active {
    color: var(--accent-coral);
}

.nav-floating a.active::after {
    width: 100%;
}
`;

// Inject CSS
const style = document.createElement('style');
style.textContent = rippleCSS;
document.head.appendChild(style);



