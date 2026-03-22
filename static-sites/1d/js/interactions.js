// Interactive Features Module
class InteractionController {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupFeatureButtons();
        this.setupGalleryInteractions();
        this.setupMemberCards();
        this.setupConsoleMessages();
    }
    
    setupFeatureButtons() {
        const featureButtons = document.querySelectorAll('.feature-card .btn');
        
        featureButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                
                const feature = button.closest('.feature-card');
                const featureTitle = feature.querySelector('h3').textContent;
                
                this.showFeatureModal(featureTitle);
            });
        });
    }
    
    showFeatureModal(featureName) {
        // Simple alert for now - could be enhanced with a proper modal
        const messages = {
            'Memory Wall': 'Share your favorite One Direction memories! This feature would allow fans to post their concert experiences, meet & greet stories, and special moments.',
            'Fan Art Gallery': 'Showcase your artistic talents! Upload drawings, digital art, crafts, and creative tributes to the band.',
            'Song Quiz': 'Test your 1D knowledge! Challenge yourself with lyrics, album facts, and trivia about the boys.',
            'Message Board': 'Connect with Directioners worldwide! Discuss songs, theories, solo careers, and share your love for the band.'
        };
        
        const message = messages[featureName] || `Welcome to the ${featureName} section!`;
        
        // Create a simple notification instead of alert
        this.showNotification(featureName, message);
    }
    
    showNotification(title, message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `
            <div class="notification-content">
                <h4>${title}</h4>
                <p>${message}</p>
                <button class="btn btn-primary btn-close">Got it!</button>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            z-index: 2000;
            max-width: 400px;
            width: 90%;
            text-align: center;
            animation: slideIn 0.3s ease;
        `;
        
        // Create overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1999;
            animation: fadeIn 0.3s ease;
        `;
        
        document.body.appendChild(overlay);
        document.body.appendChild(notification);
        
        // Close handlers
        const closeBtn = notification.querySelector('.btn-close');
        const close = () => {
            notification.style.animation = 'slideOut 0.3s ease forwards';
            overlay.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => {
                document.body.removeChild(notification);
                document.body.removeChild(overlay);
            }, 300);
        };
        
        closeBtn.addEventListener('click', close);
        overlay.addEventListener('click', close);
    }
    
    setupGalleryInteractions() {
        const galleryItems = document.querySelectorAll('.gallery-item');
        
        galleryItems.forEach((item, index) => {
            item.addEventListener('click', () => {
                const titles = [
                    'X Factor Journey',
                    'Up All Night Era',
                    'World Tours',
                    'Award Shows',
                    'Behind the Scenes',
                    'Final Performances'
                ];
                
                const descriptions = [
                    'Where five solo contestants became the biggest boy band in the world.',
                    'Their debut album that changed everything and launched them to global stardom.',
                    'Sold-out stadiums, screaming fans, and unforgettable performances worldwide.',
                    'Collecting awards and breaking records at every major music ceremony.',
                    'Candid moments, friendship, and the real boys behind the fame.',
                    'The emotional farewell tour that marked the end of an era.'
                ];
                
                this.showGalleryModal(titles[index] || 'Gallery Item', descriptions[index] || 'A special moment in One Direction history.');
            });
        });
    }
    
    showGalleryModal(title, description) {
        this.showNotification(title, description);
    }
    
    setupMemberCards() {
        const memberCards = document.querySelectorAll('.member-card');
        
        memberCards.forEach(card => {
            card.addEventListener('click', () => {
                const memberName = card.querySelector('h3').textContent;
                const memberInfo = this.getMemberInfo(memberName);
                
                this.showNotification(`About ${memberName}`, memberInfo);
            });
        });
    }
    
    getMemberInfo(name) {
        const info = {
            'Harry Styles': 'Born in Redditch, England. Known for his distinctive voice and fashion sense. Now a successful solo artist and actor.',
            'Liam Payne': 'From Wolverhampton, England. The determined one who often took leadership roles in the band. Solo career focuses on pop and R&B.',
            'Louis Tomlinson': 'From Doncaster, England. Known for his wit and stage presence. His solo work showcases his songwriting talents.',
            'Niall Horan': 'From Mullingar, Ireland. The musical one who played guitar and brought folk influences to the band.',
            'Zayn Malik': 'From Bradford, England. Left the band in 2015 to pursue a more artistic and R&B-focused solo career.'
        };
        
        return info[name] || 'A talented member of One Direction who contributed to their incredible success.';
    }
    
    setupConsoleMessages() {
        console.log('🎵 One Direction Forever - Wagtail-inspired design loaded! 🎵');
        console.log('Built with modern web technologies and clean design principles');
        console.log('Made with 💜 for Directioners everywhere');
    }
}

// Add notification animation styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.8);
        }
        to {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
    }
    
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
        to {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.8);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    .notification-content h4 {
        color: var(--primary-purple);
        margin-bottom: 1rem;
    }
    
    .notification-content p {
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
`;

document.head.appendChild(notificationStyles);

// Initialize interactions when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new InteractionController();
});