import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import lottie from 'lottie-web';

// Register GSAP plugins
// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// Expose GSAP globally for page micro-animations (AI Tutor drawer, typing wave & message bubbles)
if (typeof window !== 'undefined') {
    window.gsap = gsap;
    window.ScrollTrigger = ScrollTrigger;
    window.lottie = lottie;
    window.startTypingWave = startTypingWave;
    window.stopTypingWave = stopTypingWave;
}


// Retain system load verification messages
console.log("ECET-PREPHUB animation system loaded");
console.log("GSAP Version:", gsap.version);
console.log("ScrollTrigger loaded:", typeof ScrollTrigger !== 'undefined');
console.log("Lottie Web loaded:", typeof lottie !== 'undefined');

// Check for reduced motion preference
const prefersReducedMotion = () => {
    return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

// Check for mobile viewport
const isMobile = () => {
    return typeof window !== 'undefined' && window.innerWidth <= 768;
};

// =========================================================
// 1. NAVBAR ANIMATION & HOVER
// =========================================================
export function initNavbarAnimations() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    if (prefersReducedMotion()) {
        gsap.set(navbar, { opacity: 1 });
        return;
    }

    const navItems = navbar.querySelectorAll('.nav-links li, .nav-buttons > *');

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    tl.fromTo(navbar, 
        { opacity: 0, y: -12 }, 
        { opacity: 1, y: 0, duration: 0.6 }
    );

    if (navItems.length > 0) {
        tl.fromTo(navItems,
            { opacity: 0, y: -8 },
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.08 },
            '-=0.3'
        );
    }

    // Subtle hover interactions on navigation buttons
    const navButtons = navbar.querySelectorAll('.nav-btn, .nav-buttons a, .nav-buttons button');
    navButtons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            gsap.to(btn, { y: -2, scale: 1.02, duration: 0.25, ease: 'power2.out' });
        });
        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, { y: 0, scale: 1, duration: 0.25, ease: 'power2.out' });
        });
    });
}

// =========================================================
// 2. HERO HEADING & CONTENT ANIMATION
// =========================================================
export function initHeroAnimations() {
    const hero = document.querySelector('.hero');
    if (!hero) return;

    const heading = hero.querySelector('.hero-content h2');
    const badge = hero.querySelector('.hero-badge');
    const paragraph = hero.querySelector('.hero-content p');
    const buttons = hero.querySelectorAll('.hero-buttons a, .hero-buttons button');

    if (prefersReducedMotion()) {
        gsap.set([badge, heading, paragraph, buttons], { opacity: 1, x: 0, y: 0 });
        return;
    }

    const xOffset = isMobile() ? -25 : -50;
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    if (badge) {
        tl.fromTo(badge, 
            { opacity: 0, y: -12 }, 
            { opacity: 1, y: 0, duration: 0.5 }
        );
    }

    if (heading) {
        tl.fromTo(heading, 
            { opacity: 0, x: xOffset }, 
            { opacity: 1, x: 0, duration: 0.7 }, 
            '-=0.2'
        );
    }

    if (paragraph) {
        tl.fromTo(paragraph, 
            { opacity: 0, y: 15 }, 
            { opacity: 1, y: 0, duration: 0.6 }, 
            '-=0.3'
        );
    }

    if (buttons.length > 0) {
        tl.fromTo(buttons, 
            { opacity: 0, y: 12 }, 
            { opacity: 1, y: 0, duration: 0.5, stagger: 0.12 }, 
            '-=0.3'
        );

        buttons.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                gsap.to(btn, { y: -3, scale: 1.02, duration: 0.25, ease: 'power2.out' });
            });
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, { y: 0, scale: 1, duration: 0.25, ease: 'power2.out' });
            });
            btn.addEventListener('mousedown', () => {
                gsap.to(btn, { scale: 0.98, duration: 0.1 });
            });
            btn.addEventListener('mouseup', () => {
                gsap.to(btn, { scale: 1.02, duration: 0.15 });
            });
        });
    }
}

// =========================================================
// 3. COLLEGE IMAGE REVEAL & AMBIENT EFFECT
// =========================================================
export function initCollegeImageAnimation() {
    const heroImage = document.querySelector('.hero-image');
    if (!heroImage) return;

    const img = heroImage.querySelector('img');
    if (!img) return;

    if (prefersReducedMotion()) {
        gsap.set(heroImage, { opacity: 1, x: 0, scale: 1 });
        return;
    }

    const xOffset = isMobile() ? 25 : 60;

    // Entrance animation
    gsap.fromTo(heroImage,
        { opacity: 0, x: xOffset, scale: 0.97 },
        { 
            opacity: 1, 
            x: 0, 
            scale: 1, 
            duration: 1.1, 
            ease: 'power2.out',
            onComplete: () => {
                // Check if SVG curve exists to animate
                initSvgCurveAnimation(heroImage);

                // Start subtle ambient floating motion if not on mobile
                if (!isMobile()) {
                    gsap.to(heroImage, {
                        y: 4,
                        duration: 3.2,
                        repeat: -1,
                        yoyo: true,
                        ease: 'sine.inOut'
                    });
                }
            }
        }
    );

    // Subtle hover effect
    img.addEventListener('mouseenter', () => {
        gsap.to(img, { 
            scale: 1.015, 
            boxShadow: '0 30px 60px -10px rgba(99, 102, 241, 0.35), 0 0 20px rgba(59, 130, 246, 0.2)', 
            duration: 0.4, 
            ease: 'power2.out' 
        });
    });
    img.addEventListener('mouseleave', () => {
        gsap.to(img, { 
            scale: 1, 
            boxShadow: 'var(--shadow-2xl, 0 25px 50px -12px rgba(0, 0, 0, 0.25))', 
            duration: 0.4, 
            ease: 'power2.out' 
        });
    });
}

// =========================================================
// 4. BLUE CURVED SVG ANIMATION (If present)
// =========================================================
function initSvgCurveAnimation(container) {
    const svgPath = container.querySelector('svg path');
    if (!svgPath) return;

    try {
        const pathLength = svgPath.getTotalLength();
        gsap.set(svgPath, {
            strokeDasharray: pathLength,
            strokeDashoffset: pathLength
        });

        gsap.to(svgPath, {
            strokeDashoffset: 0,
            duration: 1.2,
            ease: 'power2.inOut'
        });
    } catch (e) {
        // SVG metrics not supported or unavailable
    }
}

// =========================================================
// 5. FEATURE CARDS SCROLL ANIMATION
// =========================================================
export function initFeatureAnimations() {
    const featureCards = document.querySelectorAll('.features .feature-card');
    if (featureCards.length === 0) return;

    if (prefersReducedMotion()) {
        gsap.set(featureCards, { opacity: 1, y: 0 });
        return;
    }

    const yOffset = isMobile() ? 20 : 35;

    ScrollTrigger.batch('.features .feature-card', {
        start: 'top 85%',
        once: true,
        onEnter: (batch) => {
            gsap.fromTo(batch,
                { opacity: 0, y: yOffset },
                { 
                    opacity: 1, 
                    y: 0, 
                    duration: 0.7, 
                    stagger: 0.12, 
                    ease: 'power3.out' 
                }
            );
        }
    });

    // Subtle hover interactions
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, { y: -5, scale: 1.01, duration: 0.3, ease: 'power2.out' });
        });
        card.addEventListener('mouseleave', () => {
            gsap.to(card, { y: 0, scale: 1, duration: 0.3, ease: 'power2.out' });
        });
    });
}

// =========================================================
// 6. QUIZ, STATS, ABOUT & WHY CARDS ANIMATION
// =========================================================
export function initQuizAndWhyAnimations() {
    const whyCards = document.querySelectorAll('.why .why-card');
    const statBoxes = document.querySelectorAll('.stats .stat-box');
    const aboutContainer = document.querySelector('.about-container');

    if (prefersReducedMotion()) {
        gsap.set([whyCards, statBoxes, aboutContainer], { opacity: 1, y: 0, x: 0 });
        return;
    }

    if (aboutContainer) {
        const aboutImage = aboutContainer.querySelector('.about-image');
        const aboutText = aboutContainer.querySelector('.about-text');

        if (aboutImage && aboutText) {
            ScrollTrigger.create({
                trigger: aboutContainer,
                start: 'top 80%',
                once: true,
                onEnter: () => {
                    gsap.fromTo(aboutImage,
                        { opacity: 0, x: isMobile() ? 0 : -30, y: isMobile() ? 20 : 0 },
                        { opacity: 1, x: 0, y: 0, duration: 0.8, ease: 'power3.out' }
                    );
                    gsap.fromTo(aboutText,
                        { opacity: 0, x: isMobile() ? 0 : 30, y: isMobile() ? 20 : 0 },
                        { opacity: 1, x: 0, y: 0, duration: 0.8, ease: 'power3.out', delay: 0.15 }
                    );
                }
            });
        }
    }

    if (statBoxes.length > 0) {
        ScrollTrigger.batch('.stats .stat-box', {
            start: 'top 85%',
            once: true,
            onEnter: (batch) => {
                gsap.fromTo(batch,
                    { opacity: 0, y: 25 },
                    { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: 'power2.out' }
                );
            }
        });
    }

    if (whyCards.length > 0) {
        ScrollTrigger.batch('.why .why-card', {
            start: 'top 85%',
            once: true,
            onEnter: (batch) => {
                gsap.fromTo(batch,
                    { opacity: 0, y: 30 },
                    { opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: 'power3.out' }
                );
            }
        });

        whyCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                gsap.to(card, { y: -5, scale: 1.01, duration: 0.3, ease: 'power2.out' });
            });
            card.addEventListener('mouseleave', () => {
                gsap.to(card, { y: 0, scale: 1, duration: 0.3, ease: 'power2.out' });
            });
        });
    }
}

// =========================================================
// =========================================================
// AI TUTOR TYPING INDICATOR WAVE ANIMATION
// =========================================================
const activeTypingAnimations = new Map();

/**
 * Starts a smooth continuous left-to-right wave animation on the 3 typing dots.
 * @param {HTMLElement|string} bubbleOrId - The loading bubble element or its ID
 * @returns {gsap.core.Tween|null} - The GSAP animation instance or null
 */
export function startTypingWave(bubbleOrId) {
    const bubble = typeof bubbleOrId === 'string' ? document.getElementById(bubbleOrId) : bubbleOrId;
    if (!bubble) return null;

    const bubbleId = bubble.id || ('loading-' + Date.now());

    // Clean up any existing animation on this bubble
    stopTypingWave(bubbleId);

    const dots = bubble.querySelectorAll('.dot');
    if (!dots || dots.length === 0) return null;

    // Respect reduced motion
    if (prefersReducedMotion()) {
        gsap.set(dots, { y: 0, scale: 1, opacity: 0.65 });
        return null;
    }

    // Set initial resting state
    gsap.set(dots, { y: 0, scale: 1, opacity: 0.45 });

    // Continuous smooth left-to-right traveling wave
    // Dot 1 -> Dot 2 -> Dot 3 with staggered upward motion & sine curve
    const waveTween = gsap.to(dots, {
        y: -6.5,
        scale: 1.15,
        opacity: 1,
        duration: 0.5,
        stagger: {
            each: 0.15,
            repeat: -1,
            yoyo: true
        },
        ease: "sine.inOut"
    });

    activeTypingAnimations.set(bubbleId, waveTween);
    bubble._typingTween = waveTween;
    return waveTween;
}

/**
 * Stops and cleanly kills the GSAP wave animation for the given bubble ID.
 * @param {string} [bubbleId] - The ID of the loading bubble, or falsy to kill all
 */
export function stopTypingWave(bubbleId) {
    if (!bubbleId) {
        activeTypingAnimations.forEach(anim => {
            if (anim && anim.kill) anim.kill();
        });
        activeTypingAnimations.clear();
        return;
    }

    if (activeTypingAnimations.has(bubbleId)) {
        const anim = activeTypingAnimations.get(bubbleId);
        if (anim && anim.kill) {
            anim.kill();
        }
        activeTypingAnimations.delete(bubbleId);
    }
}

// 7. AI TUTOR ANIMATION & LOTTIE CHECK
// =========================================================
export function initAITutorAnimation() {
    const aiRobotIcon = document.querySelector('.workspace-header h2 i.fa-robot');
    const emptyChatHeader = document.querySelector('.empty-chat-state h2');

    // Subtle ambient glow on the AI Robot icon when on the AI Tutor page
    if (aiRobotIcon && !prefersReducedMotion()) {
        gsap.to(aiRobotIcon, {
            color: '#818CF8',
            scale: 1.08,
            duration: 1.8,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut'
        });
    }

    if (emptyChatHeader && !prefersReducedMotion()) {
        gsap.fromTo(emptyChatHeader,
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }
        );
    }
}

// =========================================================
// 8. FOOTER ANIMATION
// =========================================================
export function initFooterAnimation() {
    const footer = document.querySelector('footer');
    if (!footer) return;

    if (prefersReducedMotion()) {
        gsap.set(footer, { opacity: 1, y: 0 });
        return;
    }

    ScrollTrigger.create({
        trigger: footer,
        start: 'top 95%',
        once: true,
        onEnter: () => {
            gsap.fromTo(footer,
                { opacity: 0, y: 25 },
                { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' }
            );
        }
    });
}

// =========================================================
// 9. BRANCH CARDS GLOW INTERACTION
// =========================================================
export function initBranchCardGlow() {
    const cards = document.querySelectorAll('.paper-btn, .branch-card, .semester-card');
    if (!cards || !cards.length) return;

    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
            card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
        });
    });
}


// =========================================================
// 10. NEUMORPHIC AUTHENTICATION WITH TRUE 3D FLIP SYSTEM
// =========================================================

/**
 * Animate floating neumorphic background bubbles with subtle sine curves.
 */
export function initAuthBackground() {
    const bubbles = document.querySelectorAll('.auth-bg-bubbles .auth-bubble');
    if (!bubbles.length) return;

    if (prefersReducedMotion()) {
        gsap.set(bubbles, { opacity: 1, scale: 1, y: 0, x: 0 });
        return;
    }

    gsap.fromTo(bubbles,
        { opacity: 0, scale: 0.88 },
        { opacity: 1, scale: 1, duration: 0.9, stagger: 0.1, ease: 'power2.out' }
    );

    const floatParams = [
        { y: 8, x: 5, dur: 9.5 },
        { y: -7, x: -4, dur: 12.0 },
        { y: 9, x: -6, dur: 13.5 },
        { y: -5, x: 5, dur: 8.5 },
        { y: 7, x: -4, dur: 10.5 }
    ];

    bubbles.forEach((bubble, i) => {
        const p = floatParams[i % floatParams.length];
        gsap.to(bubble, {
            y: p.y,
            x: p.x,
            duration: p.dur,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut',
            delay: i * 0.3
        });
    });
}

/**
 * Handle initial entrance animation for the authentication card.
 */
export function initAuthEntrance(authCard, activeFace) {
    if (!authCard) return;

    if (prefersReducedMotion()) {
        gsap.set(authCard, { opacity: 1, y: 0, scale: 1 });
        return;
    }

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    // 1. Card rises softly
    tl.fromTo(authCard,
        { opacity: 0, y: 22, scale: 0.98 },
        { opacity: 1, y: 0, scale: 1, duration: 0.65 }
    );

    // 2. Active face badge & headings
    const face = activeFace || authCard.querySelector('.login-face');
    if (face) {
        const badge = face.querySelector('.auth-icon-badge');
        if (badge) {
            tl.fromTo(badge,
                { opacity: 0, scale: 0.6, y: -6 },
                { opacity: 1, scale: 1, y: 0, duration: 0.4, ease: 'back.out(1.6)' },
                '-=0.35'
            );
        }

        const headings = face.querySelectorAll('.brand-logo, .auth-brand h2, .auth-subtitle');
        if (headings.length) {
            tl.fromTo(headings,
                { opacity: 0, y: 8 },
                { opacity: 1, y: 0, duration: 0.35, stagger: 0.05 },
                '-=0.25'
            );
        }

        const formItems = face.querySelectorAll('.form-group, .btn-auth-submit, .auth-switch-section');
        if (formItems.length) {
            tl.fromTo(formItems,
                { opacity: 0, y: 8 },
                { opacity: 1, y: 0, duration: 0.32, stagger: 0.04 },
                '-=0.2'
            );
        }
    }
}

/**
 * True 3D Flip System between Login Face (0 deg) and Register Face (180 deg).
 * Completely isolates inactive face visibility so no misplaced buttons or leaks can occur.
 */
export function initAuthFlip() {
    const card = document.getElementById('authFlipCard');
    const wrapper = document.getElementById('authCardWrapper');
    const loginFace = document.getElementById('loginFace');
    const registerFace = document.getElementById('registerFace');
    const flipToRegisterBtn = document.getElementById('flipToRegisterBtn');
    const flipToLoginBtn = document.getElementById('flipToLoginBtn');

    if (!card || !wrapper || !loginFace || !registerFace) return;

    let isFlipping = false;

    // Detect initial face from attribute or URL
    const isRegisterInitial = 
        card.getAttribute('data-initial-face') === 'register' || 
        window.location.pathname.includes('register');

    let currentFace = isRegisterInitial ? 'register' : 'login';

    const setFaceState = (face) => {
        currentFace = face;
        if (face === 'register') {
            card.classList.remove('is-flipping', 'is-login-active');
            card.classList.add('is-register-active');
            gsap.set(card, { rotateY: 180 });
            wrapper.style.height = `${registerFace.offsetHeight}px`;
        } else {
            card.classList.remove('is-flipping', 'is-register-active');
            card.classList.add('is-login-active');
            gsap.set(card, { rotateY: 0 });
            wrapper.style.height = `${loginFace.offsetHeight}px`;
        }
    };

    // Apply initial state cleanly
    setFaceState(currentFace);

    // Re-measure after initial layout render
    setTimeout(() => {
        setFaceState(currentFace);
    }, 80);

    window.addEventListener('resize', () => {
        if (!isFlipping) {
            const active = currentFace === 'register' ? registerFace : loginFace;
            wrapper.style.height = `${active.offsetHeight}px`;
        }
    });

    /**
     * Flip from Login (0 deg) to Register (180 deg)
     */
    const flipToRegister = (pushState = true) => {
        if (isFlipping || currentFace === 'register') return;
        isFlipping = true;

        if (prefersReducedMotion()) {
            setFaceState('register');
            isFlipping = false;
            if (pushState && window.location.pathname !== '/register') {
                window.history.pushState({ authState: 'register' }, '', '/register');
                document.title = 'Student Registration — ECET-PREPHUB';
            }
            return;
        }

        // Micro interaction on switch button
        if (flipToRegisterBtn) {
            const icon = flipToRegisterBtn.querySelector('.circle-icon-wrap');
            if (icon) {
                gsap.to(icon, { scale: 1.25, rotate: 90, duration: 0.3, ease: 'back.out(2)' });
            }
        }

        // Enter flipping state (both faces 3D visible, backface hidden)
        card.classList.remove('is-login-active', 'is-register-active');
        card.classList.add('is-flipping');
        
        const targetHeight = registerFace.offsetHeight;
        wrapper.style.height = `${loginFace.offsetHeight}px`;

        const tl = gsap.timeline({
            defaults: { ease: 'power3.inOut' },
            onComplete: () => {
                setFaceState('register');
                isFlipping = false;
                if (pushState && window.location.pathname !== '/register') {
                    window.history.pushState({ authState: 'register' }, '', '/register');
                    document.title = 'Student Registration — ECET-PREPHUB';
                }
                if (flipToRegisterBtn) {
                    const icon = flipToRegisterBtn.querySelector('.circle-icon-wrap');
                    if (icon) gsap.set(icon, { scale: 1, rotate: 0 });
                }
            }
        });

        // 1. True 3D Flip 0 -> 180 deg
        tl.to(card, {
            rotateY: 180,
            duration: 0.85
        }, 0);

        // 2. Dynamic depth lighting and shadow elevation peaking at 90 deg
        tl.to(card, {
            boxShadow: '0 28px 55px rgba(163, 177, 198, 0.55), 0 0 24px rgba(59, 130, 246, 0.25)',
            duration: 0.42,
            yoyo: true,
            repeat: 1,
            ease: 'power2.inOut'
        }, 0);

        // 3. Smooth height interpolation
        if (targetHeight) {
            tl.to(wrapper, {
                height: targetHeight,
                duration: 0.85
            }, 0);
        }
    };

    /**
     * Flip from Register (180 deg) back to Login (0 deg)
     */
    const flipToLogin = (pushState = true) => {
        if (isFlipping || currentFace === 'login') return;
        isFlipping = true;

        if (prefersReducedMotion()) {
            setFaceState('login');
            isFlipping = false;
            if (pushState && window.location.pathname !== '/login') {
                window.history.pushState({ authState: 'login' }, '', '/login');
                document.title = 'Student Login — ECET-PREPHUB';
            }
            return;
        }

        // Micro interaction on switch button
        if (flipToLoginBtn) {
            const icon = flipToLoginBtn.querySelector('.circle-icon-wrap');
            if (icon) {
                gsap.to(icon, { scale: 1.25, rotate: -90, duration: 0.3, ease: 'back.out(2)' });
            }
        }

        card.classList.remove('is-login-active', 'is-register-active');
        card.classList.add('is-flipping');

        const targetHeight = loginFace.offsetHeight;
        wrapper.style.height = `${registerFace.offsetHeight}px`;

        const tl = gsap.timeline({
            defaults: { ease: 'power3.inOut' },
            onComplete: () => {
                setFaceState('login');
                isFlipping = false;
                if (pushState && window.location.pathname !== '/login') {
                    window.history.pushState({ authState: 'login' }, '', '/login');
                    document.title = 'Student Login — ECET-PREPHUB';
                }
                if (flipToLoginBtn) {
                    const icon = flipToLoginBtn.querySelector('.circle-icon-wrap');
                    if (icon) gsap.set(icon, { scale: 1, rotate: 0 });
                }
            }
        });

        // 1. True 3D Flip 180 -> 0 deg
        tl.to(card, {
            rotateY: 0,
            duration: 0.85
        }, 0);

        // 2. Dynamic depth lighting and shadow elevation peaking at 90 deg
        tl.to(card, {
            boxShadow: '0 28px 55px rgba(163, 177, 198, 0.55), 0 0 24px rgba(59, 130, 246, 0.25)',
            duration: 0.42,
            yoyo: true,
            repeat: 1,
            ease: 'power2.inOut'
        }, 0);

        // 3. Smooth height interpolation
        if (targetHeight) {
            tl.to(wrapper, {
                height: targetHeight,
                duration: 0.85
            }, 0);
        }
    };

    // Attach switch button listeners
    if (flipToRegisterBtn) {
        flipToRegisterBtn.addEventListener('click', (e) => {
            e.preventDefault();
            flipToRegister(true);
        });
    }

    if (flipToLoginBtn) {
        flipToLoginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            flipToLogin(true);
        });
    }

    // Browser back/forward button popstate synchronization
    window.addEventListener('popstate', (e) => {
        if (window.location.pathname.includes('register')) {
            flipToRegister(false);
        } else if (window.location.pathname.includes('login')) {
            flipToLogin(false);
        }
    });
}

/**
 * Master Authentication Initializer
 */
export function initAuthAnimations() {
    const authScene = document.querySelector('.auth-scene');
    const authCard = document.getElementById('authFlipCard');
    if (!authScene || !authCard) return;

    initAuthBackground();
    initAuthFlip();
    
    const isRegister = 
        authCard.getAttribute('data-initial-face') === 'register' || 
        window.location.pathname.includes('register');
    const activeFace = isRegister ? document.getElementById('registerFace') : document.getElementById('loginFace');

    initAuthEntrance(authCard, activeFace);
}

// =========================================================
// MASTER INITIALIZATION
// =========================================================
function initAnimations() {
    // Add marker class to document so CSS knows GSAP is active
    document.documentElement.classList.add('gsap-loaded');

    // Execute modular initializers with element existence checks
    initNavbarAnimations();
    initHeroAnimations();
    initCollegeImageAnimation();
    initFeatureAnimations();
    initQuizAndWhyAnimations();
    initAITutorAnimation();
    initFooterAnimation();
    initBranchCardGlow();
    initAuthAnimations();
}

if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAnimations);
    } else {
        initAnimations();
    }
}
