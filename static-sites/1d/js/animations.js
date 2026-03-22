// Animation Module
class AnimationController {
    constructor() {
        this.observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        this.init();
    }
    
    init() {
        this.setupScrollAnimations();
        this.setupButtonAnimations();
        this.setupHoverEffects();
    }
    
    setupScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, this.observerOptions);
        
        // Elements to animate on scroll
        const animatedElements = document.querySelectorAll(
            '.card, .member-card, .gallery-item, .timeline-item, .feature-card, .section-title'
        );
        
        animatedElements.forEach(el => {
            el.classList.add('animate-on-scroll');
            observer.observe(el);
        });
    }
    
    setupButtonAnimations() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            button.addEventListener('click', this.createRippleEffect.bind(this));
        });
    }
    
    createRippleEffect(event) {
        const button = event.currentTarget;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    setupHoverEffects() {
        // Member card hover effects
        const memberCards = document.querySelectorAll('.member-card');
        memberCards.forEach(card => {
            const avatar = card.querySelector('.member-avatar');
            
            card.addEventListener('mouseenter', () => {
                if (avatar) {
                    avatar.style.transform = 'scale(1.1) rotate(5deg)';
                    avatar.style.boxShadow = '0 10px 30px rgba(108, 92, 231, 0.3)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                if (avatar) {
                    avatar.style.transform = 'scale(1) rotate(0deg)';
                    avatar.style.boxShadow = 'none';
                }
            });
        });
        
        // Gallery item effects
        const galleryItems = document.querySelectorAll('.gallery-item');
        galleryItems.forEach(item => {
            item.addEventListener('click', () => {
                item.style.animation = 'pulse 0.3s ease';
                setTimeout(() => {
                    item.style.animation = '';
                }, 300);
            });
        });
        
        // Feature card icons
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            const icon = card.querySelector('.feature-icon');
            
            card.addEventListener('mouseenter', () => {
                if (icon) {
                    icon.style.transform = 'scale(1.2) rotate(10deg)';
                }
            });
            
            card.addEventListener('mouseleave', () => {
                if (icon) {
                    icon.style.transform = 'scale(1) rotate(0deg)';
                }
            });
        });
    }
}

// Add CSS for animations
const animationStyles = document.createElement('style');
animationStyles.textContent = `
    .animate-on-scroll {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease;
    }
    
    .animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .member-avatar,
    .feature-icon {
        transition: all 0.3s ease;
    }
`;

document.head.appendChild(animationStyles);

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AnimationController();
});