/**
 * EduGenie Lightfall — Cinematic Flowing Light Trail Background
 * 
 * Visual Target: "Lightfall" — flowing cinematic light rain with:
 *   - Long flowing curved light trails (200px - 550px)
 *   - Cohesive diagonal perspective: ╲  ╲  ✦  ╲ cascading from celestial origin
 *   - 3 depth tiers: deep cosmic background, mid streaks, foreground hero trails
 *   - Smooth GPU-accelerated gradient curves with glowing tips & soft fading tails
 *   - Concentrated atmospheric light source (upper celestial bloom)
 *   - Pure purple / blue / cyan / violet / ethereal white palette
 *   - Subtle interactive mouse deflection & proximity brightening
 *   - Auto-dims in chat mode, respects prefers-reduced-motion
 *
 * 100% dependency-free, pure Canvas 2D, high-performance 60 FPS
 */
(function () {
    'use strict';

    // Singleton guard
    if (window.__edugenie_lightfall) {
        try { window.__edugenie_lightfall.destroy(); } catch (e) { }
    }

    // ─── User-specified Lightfall Palette ─────────────────────────────
    const PALETTE = [
        { r: 82,  g: 39,  b: 255, name: 'purple' }, // #5227FF — Primary Royal Purple
        { r: 82,  g: 39,  b: 255, name: 'purple' }, // extra weight for purple
        { r: 76,  g: 111, b: 255, name: 'blue'   }, // #4C6FFF — Electric Azure Blue
        { r: 76,  g: 111, b: 255, name: 'blue'   }, // extra weight for blue
        { r: 102, g: 204, b: 255, name: 'cyan'   }, // #66CCFF — Vibrant Cyan
        { r: 181, g: 140, b: 255, name: 'violet' }, // #B58CFF — Soft Violet
        { r: 245, g: 247, b: 255, name: 'white'  }, // #F5F7FF — Ethereal White
    ];

    // ─── Configuration ───────────────────────────────────────────────
    const CFG = {
        // Density & Counts
        densityPerMPx: 75,
        minTrails: 55,
        maxTrails: 95,
        mobileScale: 0.45,

        // Flow Direction: Diagonal down-right (╲ ╲ ╲)
        baseAngle: 0.46,          // ~26 degrees from vertical
        angleVariation: 0.16,     // variance +/- 9 degrees

        // Length & Speed
        lengthMin: 180,
        lengthMax: 520,
        speedMin: 0.8,
        speedMax: 3.6,

        // Curvature
        curveBase: 28,            // lateral bow amplitude (px)
        curveVariation: 22,

        // Interactive Mouse
        mouseRadius: 220,
        mouseBrighten: 0.45,
        mouseDeflect: 0.25,

        // Atmosphere
        bloomRadius: 0.62,
        bloomOpacity: 0.12,
        opacityDamping: 0.04
    };

    class Lightfall {
        constructor() {
            this.canvas = document.getElementById('lightfallCanvas');
            if (!this.canvas) return;
            this.ctx = this.canvas.getContext('2d');
            if (!this.ctx) return;

            this.trails = [];
            this.w = 0;
            this.h = 0;
            this.dpr = Math.min(window.devicePixelRatio || 1, 1.5);
            this.time = 0;
            this.animId = null;

            // Pointer
            this.ptr = { x: -9999, y: -9999, tx: -9999, ty: -9999, active: false, fade: 0 };

            // Mode & Motion
            this.opacity = 1.0;
            this.targetOpacity = 1.0;
            this.isMobile = false;
            this.reducedMotion = false;

            this._init();
        }

        _init() {
            const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
            this.reducedMotion = mq.matches;
            mq.addEventListener('change', e => {
                this.reducedMotion = e.matches;
                if (this.reducedMotion) {
                    if (this.animId) { cancelAnimationFrame(this.animId); this.animId = null; }
                    this._staticFrame();
                } else if (!this.animId) {
                    this._loop();
                }
            });

            this.isMobile = ('ontouchstart' in window) || window.innerWidth < 768;

            this._onResize = this._onResize.bind(this);
            this._onPtr = this._onPtr.bind(this);
            this._onPtrOut = this._onPtrOut.bind(this);
            this._loop = this._loop.bind(this);

            window.addEventListener('resize', this._onResize, { passive: true });
            if (!this.isMobile) {
                window.addEventListener('pointermove', this._onPtr, { passive: true });
                window.addEventListener('pointerleave', this._onPtrOut, { passive: true });
            }

            this._onResize();

            if (this.reducedMotion) {
                this._staticFrame();
            } else {
                this._loop();
            }

            window.__edugenie_lightfall = this;
        }

        _onResize() {
            this.w = window.innerWidth;
            this.h = window.innerHeight;
            this.isMobile = ('ontouchstart' in window) || this.w < 768;

            this.canvas.width = Math.floor(this.w * this.dpr);
            this.canvas.height = Math.floor(this.h * this.dpr);
            this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

            this._populate();
            if (this.reducedMotion) this._staticFrame();
        }

        _populate() {
            const area = this.w * this.h;
            let n = Math.round((area / 1e6) * CFG.densityPerMPx);
            if (this.isMobile) n = Math.round(n * CFG.mobileScale);
            n = Math.max(this.isMobile ? 24 : CFG.minTrails, Math.min(CFG.maxTrails, n));

            this.trails = [];
            for (let i = 0; i < n; i++) {
                this.trails.push(this._spawn(true));
            }
            // Sort by depth for correct layering
            this.trails.sort((a, b) => a.depth - b.depth);
        }

        _spawn(scatter) {
            // Depth distribution: 0.0 (far background) to 1.0 (crisp foreground)
            const depth = Math.random();

            // Color selection based on depth
            let colIndex;
            if (depth < 0.4) {
                // Background: mostly violet and purple
                colIndex = Math.random() < 0.6 ? 0 : 5;
            } else if (depth < 0.8) {
                // Midground: purple, blue, cyan
                colIndex = Math.floor(Math.random() * (PALETTE.length - 1));
            } else {
                // Foreground hero trails: vibrant cyan, blue, or crisp white tip
                colIndex = Math.random() < 0.4 ? 4 : (Math.random() < 0.4 ? 2 : 6);
            }
            const col = PALETTE[colIndex];

            // Cohesive diagonal flow: ╲ (angle from vertical with subtle variance)
            const angle = CFG.baseAngle + (Math.random() - 0.5) * CFG.angleVariation;

            // Length & width scale with perspective depth
            const len = CFG.lengthMin + Math.pow(depth, 1.2) * (CFG.lengthMax - CFG.lengthMin);
            const wid = 0.6 + Math.pow(depth, 1.4) * 2.4;

            // Speed scales with depth
            const spd = CFG.speedMin + Math.pow(depth, 1.2) * (CFG.speedMax - CFG.speedMin);

            // Alpha curve: background is ethereal & luminous, foreground is bold
            const alpha = depth < 0.35
                ? 0.07 + depth * 0.15           // 0.07 - 0.12
                : depth < 0.75
                    ? 0.15 + (depth - 0.35) * 0.35 // 0.15 - 0.29
                    : 0.32 + (depth - 0.75) * 0.55; // 0.32 - 0.46

            // Curve: gentle lateral bow along trajectory
            const curveBow = (CFG.curveBase + Math.random() * CFG.curveVariation) * (Math.random() < 0.25 ? -0.5 : 1.0);

            // Harmonic sway frequency & phase
            const swayRate = 0.008 + Math.random() * 0.015;
            const swayPhase = Math.random() * Math.PI * 2;

            // Spawn across screen boundaries (both top and left entry for diagonal drift)
            const margin = len + 100;
            let startX, startY;

            if (scatter) {
                // Initial distribution across entire canvas and immediate surroundings
                startX = -margin + Math.random() * (this.w + margin * 1.5);
                startY = -margin + Math.random() * (this.h + margin * 1.5);
            } else {
                // Continuous respawn: 60% from top edge, 40% from left edge
                const fromLeft = Math.random() < (this.h / (this.w + this.h * 1.2));
                if (fromLeft) {
                    startX = -margin * 0.5 - Math.random() * 80;
                    startY = -margin * 0.2 + Math.random() * (this.h * 0.85);
                } else {
                    startX = -margin * 0.5 + Math.random() * (this.w + margin * 0.5);
                    startY = -margin - Math.random() * 60;
                }
            }

            return {
                x: startX,
                y: startY,
                angle,
                len,
                wid,
                spd,
                alpha,
                col,
                depth,
                curveBow,
                swayRate,
                swayPhase,
                deflectX: 0,
                twinkle: Math.random() * Math.PI * 2
            };
        }

        _onPtr(e) {
            this.ptr.tx = e.clientX;
            this.ptr.ty = e.clientY;
            this.ptr.active = true;
        }

        _onPtrOut() {
            this.ptr.active = false;
        }

        _updatePtr() {
            const p = this.ptr;
            if (p.active) {
                p.fade += (1 - p.fade) * 0.08;
                p.x += (p.tx - p.x) * 0.1;
                p.y += (p.ty - p.y) * 0.1;
            } else {
                p.fade += (0 - p.fade) * 0.04;
            }
        }

        _updateMode() {
            const el = document.getElementById('appContainer');
            this.targetOpacity = (el && el.classList.contains('state-chat')) ? 0.45 : 1.0;
            this.opacity += (this.targetOpacity - this.opacity) * CFG.opacityDamping;
        }

        // ── Atmospheric celestial light source ────────────────────────
        _drawBloom() {
            const ctx = this.ctx;
            const w = this.w, h = this.h;
            const t = this.time;
            const op = this.opacity;

            // Concentrated upper light source (celestial origin)
            const cx = w * 0.48 + Math.sin(t * 0.0005) * 35;
            const cy = h * 0.18 + Math.cos(t * 0.0004) * 20;
            const r1 = Math.max(w, h) * CFG.bloomRadius;

            const g1 = ctx.createRadialGradient(cx, cy, 0, cx, cy, r1);
            const a = CFG.bloomOpacity * op;
            g1.addColorStop(0, `rgba(82, 39, 255, ${a * 1.35})`);      // #5227FF Core
            g1.addColorStop(0.22, `rgba(76, 111, 255, ${a * 0.85})`);  // #4C6FFF
            g1.addColorStop(0.48, `rgba(102, 204, 255, ${a * 0.38})`); // #66CCFF
            g1.addColorStop(0.75, `rgba(181, 140, 255, ${a * 0.14})`); // #B58CFF
            g1.addColorStop(1, 'rgba(5, 5, 16, 0)');

            ctx.fillStyle = g1;
            ctx.fillRect(0, 0, w, h);

            // Subtle cyan atmospheric glow in lower right
            if (!this.isMobile) {
                const c2x = w * 0.82 + Math.cos(t * 0.0004) * 25;
                const c2y = h * 0.78 + Math.sin(t * 0.0005) * 20;
                const r2 = Math.max(w, h) * 0.4;
                const g2 = ctx.createRadialGradient(c2x, c2y, 0, c2x, c2y, r2);
                const a2 = a * 0.4;
                g2.addColorStop(0, `rgba(102, 204, 255, ${a2})`);
                g2.addColorStop(0.55, `rgba(82, 39, 255, ${a2 * 0.35})`);
                g2.addColorStop(1, 'rgba(5, 5, 16, 0)');
                ctx.fillStyle = g2;
                ctx.fillRect(0, 0, w, h);
            }
        }

        _drawPointerGlow() {
            if (this.ptr.fade < 0.01 || this.isMobile) return;
            const ctx = this.ctx;
            const px = this.ptr.x, py = this.ptr.y;
            const rad = CFG.mouseRadius * 0.75;
            const a = 0.045 * this.ptr.fade * this.opacity;

            const g = ctx.createRadialGradient(px, py, 0, px, py, rad);
            g.addColorStop(0, `rgba(102, 204, 255, ${a})`);
            g.addColorStop(0.45, `rgba(82, 39, 255, ${a * 0.45})`);
            g.addColorStop(1, 'rgba(5, 5, 16, 0)');
            ctx.fillStyle = g;
            ctx.beginPath();
            ctx.arc(px, py, rad, 0, Math.PI * 2);
            ctx.fill();
        }

        // ── Draw continuous flowing curved light trail ─────────────────
        _drawTrail(t, proxFactor) {
            const ctx = this.ctx;
            const effAlpha = Math.min(0.52, t.alpha * proxFactor * this.opacity);
            if (effAlpha < 0.015) return;

            const c = t.col;

            // Geometry: Head is at (hx, hy), Tail is at (tx, ty)
            const hx = t.x + t.deflectX;
            const hy = t.y;

            const sinA = Math.sin(t.angle);
            const cosA = Math.cos(t.angle);

            const tx = hx - sinA * t.len;
            const ty = hy - cosA * t.len;

            // Organic subtle swaying curve along the descent
            const sway = Math.sin(this.time * t.swayRate + t.swayPhase) * 6;
            const bow = t.curveBow + sway;

            // Bezier control point perpendicular to trajectory
            const mx = (hx + tx) * 0.5 + cosA * bow;
            const my = (hy + ty) * 0.5 - sinA * bow;

            // Continuous Linear Gradient from tail to head
            const grad = ctx.createLinearGradient(tx, ty, hx, hy);
            grad.addColorStop(0.0, `rgba(${c.r}, ${c.g}, ${c.b}, 0)`);
            grad.addColorStop(0.35, `rgba(${c.r}, ${c.g}, ${c.b}, ${effAlpha * 0.18})`);
            grad.addColorStop(0.70, `rgba(${c.r}, ${c.g}, ${c.b}, ${effAlpha * 0.55})`);
            grad.addColorStop(0.92, `rgba(${c.r}, ${c.g}, ${c.b}, ${effAlpha * 0.95})`);
            grad.addColorStop(1.0, `rgba(245, 247, 255, ${effAlpha * 1.15})`);

            // Pass 1: Luminous atmospheric soft glow ribbon
            if (t.depth > 0.45) {
                ctx.beginPath();
                ctx.moveTo(tx, ty);
                ctx.quadraticCurveTo(mx, my, hx, hy);
                ctx.strokeStyle = `rgba(${c.r}, ${c.g}, ${c.b}, ${effAlpha * 0.28})`;
                ctx.lineWidth = t.wid * 2.8;
                ctx.lineCap = 'round';
                ctx.stroke();
            }

            // Pass 2: Sharp, brilliant inner core trail
            ctx.beginPath();
            ctx.moveTo(tx, ty);
            ctx.quadraticCurveTo(mx, my, hx, hy);
            ctx.strokeStyle = grad;
            ctx.lineWidth = t.wid;
            ctx.lineCap = 'round';
            ctx.stroke();

            // Pass 3: Luminous leading tip with soft celestial flare
            const tipR = t.wid * 1.1;
            const tipGlowR = tipR * (t.depth > 0.65 ? 4.0 : 2.5);

            // Radial tip glow
            const tipGrad = ctx.createRadialGradient(hx, hy, 0, hx, hy, tipGlowR);
            tipGrad.addColorStop(0, `rgba(255, 255, 255, ${Math.min(0.9, effAlpha * 1.5)})`);
            tipGrad.addColorStop(0.4, `rgba(${c.r}, ${c.g}, ${c.b}, ${effAlpha * 0.7})`);
            tipGrad.addColorStop(1, 'rgba(82, 39, 255, 0)');

            ctx.fillStyle = tipGrad;
            ctx.beginPath();
            ctx.arc(hx, hy, tipGlowR, 0, Math.PI * 2);
            ctx.fill();
        }

        _staticFrame() {
            this.ctx.clearRect(0, 0, this.w, this.h);
            this._updateMode();
            this._drawBloom();
            for (let i = 0; i < this.trails.length; i++) {
                this._drawTrail(this.trails[i], 1.0);
            }
        }

        _loop() {
            if (this.reducedMotion) return;

            this.time++;
            this._updatePtr();
            this._updateMode();

            const ctx = this.ctx;
            ctx.clearRect(0, 0, this.w, this.h);

            // Layer 1: Ambient Celestial Blooms
            this._drawBloom();
            this._drawPointerGlow();

            const px = this.ptr.x;
            const py = this.ptr.y;
            const hasPtr = this.ptr.fade > 0.03 && !this.isMobile;
            const mRad = CFG.mouseRadius;
            const mRadSq = mRad * mRad;

            // Render trails in depth order
            for (let i = 0; i < this.trails.length; i++) {
                const t = this.trails[i];

                // Progress along diagonal trajectory
                const sinA = Math.sin(t.angle);
                const cosA = Math.cos(t.angle);
                t.x += sinA * t.spd;
                t.y += cosA * t.spd;

                // Subtle twinkle & proximity reaction
                t.twinkle += 0.02;
                const twinkle = Math.sin(t.twinkle) * 0.12;
                let proxFactor = 1.0 + twinkle;

                // Gentle mouse deflection & brightening
                if (hasPtr) {
                    const dx = t.x - px;
                    const dy = t.y - py;
                    const distSq = dx * dx + dy * dy;

                    if (distSq < mRadSq) {
                        const dist = Math.sqrt(distSq);
                        const norm = 1 - dist / mRad;
                        proxFactor += norm * CFG.mouseBrighten;

                        const push = norm * CFG.mouseDeflect * 35 * (dx > 0 ? 1 : -1);
                        t.deflectX += (push - t.deflectX) * 0.08;
                    } else {
                        t.deflectX += (0 - t.deflectX) * 0.04;
                    }
                } else {
                    t.deflectX += (0 - t.deflectX) * 0.04;
                }

                this._drawTrail(t, proxFactor);

                // Respawn smoothly when exiting viewport bottom or right edge
                const margin = t.len + 60;
                if (t.y - t.len > this.h + 50 || t.x - t.len > this.w + 100) {
                    this.trails[i] = this._spawn(false);
                }
            }

            this.animId = requestAnimationFrame(this._loop);
        }

        destroy() {
            if (this.animId) {
                cancelAnimationFrame(this.animId);
                this.animId = null;
            }
            window.removeEventListener('resize', this._onResize);
            window.removeEventListener('pointermove', this._onPtr);
            window.removeEventListener('pointerleave', this._onPtrOut);
            if (this.ctx) this.ctx.clearRect(0, 0, this.w, this.h);
            if (window.__edugenie_lightfall === this) window.__edugenie_lightfall = null;
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => new Lightfall());
    } else {
        new Lightfall();
    }
})();
